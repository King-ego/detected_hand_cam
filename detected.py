import cv2
import os
from datetime import datetime
import mediapipe as mp

from actions import schedule_action, cancel_pending_action
from gestures import GestureRecognizer

DELAY_SECONDS = 1.2


def _bbox_from_landmarks(landmarks, w, h):
    x_coords = [min(max(int(lm.x * w), 0), w - 1) for lm in landmarks.landmark]
    y_coords = [min(max(int(lm.y * h), 0), h - 1) for lm in landmarks.landmark]
    return min(x_coords), min(y_coords), max(x_coords), max(y_coords)

def _is_bbox_inside(square, bbox):
    sx1, sy1, sx2, sy2 = square
    bx1, by1, bx2, by2 = bbox
    return bx1 >= sx1 and by1 >= sy1 and bx2 <= sx2 and by2 <= sy2

def detect_hands_in_square(camera_index=0, window_name='Hand Square', square_ratio=50,
                           min_detection_confidence=0.5, min_tracking_confidence=0.5,
                           max_num_hands=2, fullscreen=True):

    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print("Error: not open camera.")
        return

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    if fullscreen:
        try:
            cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        except cv2.error:
            pass

    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils

    try:
        with mp_hands.Hands(static_image_mode=False,
                            max_num_hands=max_num_hands,
                            min_detection_confidence=min_detection_confidence,
                            min_tracking_confidence=min_tracking_confidence) as hands:
            recognizer = GestureRecognizer(global_cooldown=4.0)

            while True:
                ret, frame = cap.read()
                if not ret or frame is None:
                    print("Error: frame not found, exiting...")
                    break

                h, w = frame.shape[:2]
                ratio = max(0.0, min(1.0, square_ratio))
                side = int(min(w, h) * ratio)
                cx, cy = w // 2, h // 2
                sx1, sy1 = cx - side // 2, cy - side // 2
                sx2, sy2 = cx + side // 2, cy + side // 2
                square = (sx1, sy1, sx2, sy2)

                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(frame_rgb)

                annotated = frame.copy()

                if ratio > 0:
                    cv2.rectangle(annotated, (sx1, sy1), (sx2, sy2), (0, 255, 255), 2)

                if results.multi_hand_landmarks:
                    for hand_landmarks, handedness in zip(results.multi_hand_landmarks,
                                                          results.multi_handedness or []):
                        mp_drawing.draw_landmarks(
                            annotated, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                            mp_drawing.DrawingSpec(color=(0,255,0), thickness=2, circle_radius=2),
                            mp_drawing.DrawingSpec(color=(0,128,255), thickness=2)
                        )

                        bbox = _bbox_from_landmarks(hand_landmarks, w, h)
                        bx1, by1, bx2, by2 = bbox
                        inside = _is_bbox_inside(square, bbox) if ratio > 0 else False

                        color = (0, 200, 0) if inside else (0, 0, 255)
                        #label = "" if inside else "" if ratio > 0 else "Mão"
                        cv2.rectangle(annotated, (bx1-5, by1-5), (bx2+5, by2+5), color, 2)
                        #cv2.putText(annotated, label, (bx1, max(by1-10, 15)),
                        #           cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

                        detections = recognizer.detect(hand_landmarks, w, h)

                        for g in detections:
                            if ratio > 0 and not inside:
                                continue
                            if g == "cancel":
                                cancel_pending_action()
                                continue
                            schedule_action(g, annotated, delay=DELAY_SECONDS)

                cv2.imshow(window_name, annotated)
                key = cv2.waitKey(1) & 0xFF

                try:
                    visible = cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE)
                except cv2.error:
                    print("GUI not created, exiting...")
                    break

                if visible < 1:
                    break
                if key == ord('q'):
                    break
                if key == ord('s'):
                    os.makedirs('temp', exist_ok=True)
                    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = os.path.join('temp', f'hand_{ts}.jpg')
                    cv2.imwrite(filename, annotated)
                    print(f"Screenshot save in {filename}")
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    detect_hands_in_square(fullscreen=True, square_ratio=1)