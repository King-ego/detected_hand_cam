import cv2
import os
from datetime import datetime
from detected import detect_hands_in_square


def access_cam_live():
    print("Start cam live...")
    capture = cv2.VideoCapture(0, cv2.CAP_V4L2)
    if not capture.isOpened():
        print("Error: Not open camera.")
        return

    win_name = 'Camera Live'

    try:
        while True:
            is_read, frame = capture.read()
            if not is_read:
                print("Frame not found, exit...")
                break

            cv2.imshow(win_name, frame)
            key = cv2.waitKey(1) & 0xFF

            try:
                visible = cv2.getWindowProperty(win_name, cv2.WND_PROP_VISIBLE)
            except cv2.error:
                print("windows not create, exit...")
                break

            if visible < 1:
                print("close windows, exit...")
                break
            if key == ord('h'):
                print("detected hand open...")
                capture.release()
                detect_hands_in_square(camera_index=0, window_name= win_name)
                capture = cv2.VideoCapture(0, cv2.CAP_V4L2)
                if not capture.isOpened():
                    print("Error: not open camera.")
                    break
                continue
            if key == ord('q'):
                print("Exit...")
                break
            if key == ord('s'):
                os.makedirs('temp', exist_ok=True)
                ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = os.path.join('temp', f'captured_frame_{ts}.jpg')
                cv2.imwrite(filename, frame)
                print(f"save screenshot in {filename}")
    finally:
        capture.release()
        cv2.destroyAllWindows()
        print("App close")