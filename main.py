import logging
from access_cam import access_cam_live

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def main():
    access_cam_live()

if __name__ == "__main__":
    main()