import logging

logger = logging.getLogger(__name__)

def is_bsl_b(landmarks, w, h, thumb_index_thresh=0.12, finger_fold_thresh=0.12 ):
    try:
        logger.info("Test")
    except Exception as e:
        logger.exception(e)