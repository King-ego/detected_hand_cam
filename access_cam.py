# python
import cv2
import os
from datetime import datetime
from detected import detect_hands_in_square


def access_cam_live():
    print("Iniciando câmera ao vivo...")
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    if not cap.isOpened():
        print("Erro: não foi possível abrir a câmera.")
        return

    win_name = 'Camera Live'
    cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Frame não disponível, saindo...")
                break

            cv2.imshow(win_name, frame)
            key = cv2.waitKey(1) & 0xFF

            try:
                visible = cv2.getWindowProperty(win_name, cv2.WND_PROP_VISIBLE)
            except cv2.error:
                print("GUI indisponível ou janela não criada, saindo...")
                break

            if visible < 1:
                print("Janela fechada, saindo...")
                break
            if key == ord('h'):
                print("Abrindo detector de mãos...")
                cap.release()
                cv2.destroyAllWindows()
                detect_hands_in_square(camera_index=0, window_name= win_name)
                cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
                if not cap.isOpened():
                    print("Erro: não foi possível reabrir a câmera.")
                    break
                cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
            if key == ord('q'):
                print("Saindo...")
                break
            if key == ord('s'):
                os.makedirs('temp', exist_ok=True)
                ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = os.path.join('temp', f'captured_frame_{ts}.jpg')
                cv2.imwrite(filename, frame)
                print(f"Screenshot salvo em {filename}")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("Câmera liberada.")