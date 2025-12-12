import time
import math
from collections import deque

def _lm_to_point(lm, w, h):
    return int(lm.x * w), int(lm.y * h)

def _distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

def hand_center(landmarks, w, h):
    pts = [_lm_to_point(lm, w, h) for lm in landmarks.landmark]
    xs, ys = zip(*pts)
    return int(sum(xs) / len(xs)), int(sum(ys) / len(ys))

def count_extended_fingers(landmarks, w, h):
    pts = [_lm_to_point(lm, w, h) for lm in landmarks.landmark]
    wrist_y = pts[0][1]
    count = 0
    tips = [4, 8, 12, 16, 20]
    for t in tips:
        if pts[t][1] < wrist_y - 10:
            count += 1
    return count

class GestureRecognizer:
    def __init__(self, max_history=6, swipe_thresh_ratio=0.25, pinch_thresh_ratio=0.07, cooldown=0.8, global_cooldown=3.0):
        self.history = deque(maxlen=max_history)
        self.cooldowns = {}
        self.swipe_thresh_ratio = swipe_thresh_ratio
        self.pinch_thresh_ratio = pinch_thresh_ratio
        self.cooldown = cooldown
        self.global_cooldown = global_cooldown
        self.last_any_trigger = 0.0

    def update(self, center):
        self.history.append((center, time.time()))

    def _recent_motion(self):
        if len(self.history) < 2:
            return 0, 0
        (x0, y0), t0 = self.history[0]
        (x1, y1), t1 = self.history[-1]
        dt = max(1e-3, t1 - t0)
        return (x1 - x0) / dt, (y1 - y0) / dt

    def _is_cooled(self, name):
        last = self.cooldowns.get(name, 0)
        return (time.time() - last) >= self.cooldown

    def _trigger(self, name):
        self.cooldowns[name] = time.time()

    def _is_global_cooled(self):
        return (time.time() - self.last_any_trigger) >= self.global_cooldown

    def detect(self, hand_landmarks, w, h):
        center = hand_center(hand_landmarks, w, h)
        self.update(center)
        candidates = []

        swipe_px = min(w, h) * self.swipe_thresh_ratio
        if len(self.history) >= 2:
            dx = self.history[-1][0][0] - self.history[0][0][0]
            dy = self.history[-1][0][1] - self.history[0][0][1]
            if abs(dx) > swipe_px and abs(dx) > abs(dy) and self._is_cooled('swipe'):
                if dx > 0:
                    candidates.append('swipe_right')
                else:
                    candidates.append('swipe_left')

        thumb = _lm_to_point(hand_landmarks.landmark[4], w, h)
        index_tip = _lm_to_point(hand_landmarks.landmark[8], w, h)
        if _distance(thumb, index_tip) < min(w, h) * self.pinch_thresh_ratio and self._is_cooled('pinch'):
            candidates.append('pinch')

        n_fingers = count_extended_fingers(hand_landmarks, w, h)
        if n_fingers >= 4 and self._is_cooled('open'):
            print(f"hands: {hand_landmarks}, w: {w}, h: {h}, center: {center}")
            candidates.append('open_hand')
        if n_fingers <= 1 and self._is_cooled('fist'):
            candidates.append('fist')

        if candidates and self._is_global_cooled():
            now = time.time()
            for name in candidates:
                if name in ('swipe_left', 'swipe_right'):
                    self._trigger('swipe')
                else:
                    self._trigger(name if name != 'open_hand' else 'open')
            self.last_any_trigger = now
            return candidates

        return []

