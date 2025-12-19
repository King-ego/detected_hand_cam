import logging
import math
from bsl.validated import lm_to_point, distance

logger = logging.getLogger(__name__)

def is_bsl_b(landmarks, w, h, thumb_index_thresh=0.12, finger_fold_thresh=0.12 ):
    try:
        wrist = lm_to_point(landmarks[0], w, h)
        index_mcp = lm_to_point(landmarks[5], w, h)
        middle_mcp = lm_to_point(landmarks[9], w, h)
        ring_mcp = lm_to_point(landmarks[13], w, h)
        pinky_mcp = lm_to_point(landmarks[17], w, h)
        thumb_tip = lm_to_point(landmarks[4], w, h)

        diag = math.hypot(w,h)

        palm_center = (
            (wrist[0] + index_mcp[0] + middle_mcp[0] + ring_mcp[0] + pinky_mcp[0]) / 4.0,
            (wrist[1] + index_mcp[1] + middle_mcp[1] + ring_mcp[1] + pinky_mcp[1]) / 4.0
        )

        thumb_folded = distance(thumb_tip, palm_center) < thumb_index_thresh + diag

        if not thumb_folded:
            return False

        dx = middle_mcp[0] - wrist[0]

    except Exception as e:
        logger.exception(e)
        return False