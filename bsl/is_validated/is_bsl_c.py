import logging

from bsl.validated import lm_to_point, distance

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

        palm_center = (
            (wrist[0] + index_mcp[0] + middle_mcp[0] + ring_mcp[0] + pinky_mcp[0]) / 5.0,
            (wrist[1] + index_mcp[1] + middle_mcp[1] + ring_mcp[1] + pinky_mcp[1]) / 5.0
        )

        tip_indices = [8, 12, 16, 20]

        dists = []

        for ti in tip_indices:
            tip = lm_to_point(landmarks.landmark[ti], w, h)
            dists.append(distance(tip, palm_center))

        dists.append(distance(thumb_tip, palm_center))

        min_open = open_dist_thresh * min_side
        if any(d <= min_open for d in dists):
            return False

        if max(dists) - min(dists) > circ_var_thresh * min_side:
            return False

        return True

        print(wrist, index_mcp, middle_mcp, ring_mcp, pinky_mcp, thumb_tip, min_side)
    except Exception as e:
        logger.exception(e)
        return False