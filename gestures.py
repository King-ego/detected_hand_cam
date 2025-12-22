import time
import math
from collections import deque
import bsl.validated as bsl_validated

def lm_to_point(lm, w, h):
    return int(lm.x * w), int(lm.y * h)

def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

def hand_center(landmarks, w, h):
    pts = [lm_to_point(lm, w, h) for lm in landmarks.landmark]
    xs, ys = zip(*pts)
    return int(sum(xs) / len(xs)), int(sum(ys) / len(ys))

def count_extended_fingers(landmarks, w, h):
    pts = [lm_to_point(lm, w, h) for lm in landmarks.landmark]
    wrist_y = pts[0][1]
    count = 0
    tips = [4, 8, 12, 16, 20]
    for t in tips:
        if pts[t][1] < wrist_y - 10:
            count += 1
    return count

class GestureRecognizer:
    def __init__(self, max_history=6, swipe_thresh_ratio=0.25, pinch_thresh_ratio=0.07, cooldown=0.8, global_cooldown=1.5):
        self.history = deque(maxlen=max_history)
        self.cooldowns = {}
        self.swipe_thresh_ratio = swipe_thresh_ratio
        self.pinch_thresh_ratio = pinch_thresh_ratio
        self.cooldown = cooldown
        self.global_cooldown = global_cooldown
        self.last_any_trigger = 0.0

    def update(self, center):
        self.history.append((center, time.time()))

    """def _recent_motion(self):
        if len(self.history) < 2:
            return 0, 0
        (x0, y0), t0 = self.history[0]
        (x1, y1), t1 = self.history[-1]
        dt = max(1e-3, t1 - t0)
        return (x1 - x0) / dt, (y1 - y0) / dt
        """

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

        """if is_bsl_a(hand_landmarks, w, h) and self._is_cooled('bsl_a'):
            candidates.append('bsl_a')
           """
        for ch in 'abcçdefghijklmnopqrstuvwxyz':
            func = getattr(bsl_validated, f'is_bsl_{ch}', None)
            action = f'bsl_{ch}'
            if callable(func) and func(hand_landmarks, w, h) and self._is_cooled(action):
                candidates.append(action)

        if candidates and self._is_global_cooled():
            now = time.time()

            first = candidates[0]
            self._trigger(first)
            self.last_any_trigger = now
            return candidates

        return []

