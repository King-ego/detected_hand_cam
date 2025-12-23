import logging

logger = logging.getLogger(__name__)

def is_bsl_c(landmarks, w, h, thumb_index_thresh=0.12, finger_fold_thresh=0.12):
    try:
        print(f"landmarks: {landmarks}, w: {w}, h: {h}")
        logger.info("Validating BSL C".upper())
    except Exception as e:
        logger.exception(e)
        return False