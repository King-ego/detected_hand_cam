import logging

from bsl.validated import lm_to_point

logger = logging.getLogger(__name__)

def is_bsl_c(landmarks, w, h, open_dist_thresh=0.10, circ_var_thresh=0.08, min_span_deg=90, max_span_deg=260):
    try:
        logger.info("Validating BSL C".upper())

        wrist = lm_to_point(landmarks.landmark[0], w, h)
        index_mcp = lm_to_point(landmarks.landmark[5], w, h)
        middle_mcp = lm_to_point(landmarks.landmark[9], w, h)
        ring_mcp = lm_to_point(landmarks.landmark[13], w, h)
        pinky_mcp = lm_to_point(landmarks.landmark[17], w, h)
        thumb_tip = lm_to_point(landmarks.landmark[4], w, h)

        min_side = min(w, h)

        print(wrist, index_mcp, middle_mcp, ring_mcp, pinky_mcp, thumb_tip, min_side)
    except Exception as e:
        logger.exception(e)
        return False