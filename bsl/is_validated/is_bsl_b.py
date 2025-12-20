import logging
import math
from bsl.validated import lm_to_point, distance

logger = logging.getLogger(__name__)

def is_bsl_b(landmarks, w, h, thumb_index_thresh=0.12, finger_fold_thresh=0.12 ):
    try:
        wrist = lm_to_point(landmarks.landmark[0], w, h)
        index_mcp = lm_to_point(landmarks.landmark[5], w, h)
        middle_mcp = lm_to_point(landmarks.landmark[9], w, h)
        ring_mcp = lm_to_point(landmarks.landmark[13], w, h)
        pinky_mcp = lm_to_point(landmarks.landmark[17], w, h)
        thumb_tip = lm_to_point(landmarks.landmark[4], w, h)

        min_side = min(w, h)

        palm_center = (
            (wrist[0] + index_mcp[0] + middle_mcp[0] + ring_mcp[0] + pinky_mcp[0]) / 5.0,
            (wrist[1] + index_mcp[1] + middle_mcp[1] + ring_mcp[1] + pinky_mcp[1]) / 5.0
        )

        thumb_folded = distance(thumb_tip, palm_center) < thumb_index_thresh * min_side

        if not thumb_folded:
            return False

        dx = middle_mcp[0] - wrist[0]
        dy = middle_mcp[1] - wrist[1]

        norm = math.hypot(dx, dy)
        if norm == 0:
            logger.debug("hand direction zero")
            return False

        hand_dir = (dx / norm, dy / norm)

        def proj_along_hand(pt):
            return (pt[0] - wrist[0]) * hand_dir[0] + (pt[1] - wrist[1]) * hand_dir[1]

        fingers = [
            (6, 8),   # index pip, tip
            (10, 12), # middle
            (14, 16), # ring
            (18, 20),
        ]

        for pip_idx, tip_idx in fingers:
            pip = lm_to_point(landmarks.landmark[pip_idx], w, h)
            tip = lm_to_point(landmarks.landmark[tip_idx], w, h)
            if proj_along_hand(tip) <= proj_along_hand(pip) + finger_fold_thresh * min_side:
                return False

        return True

    except Exception as e:
        logger.exception(e)
        return False
