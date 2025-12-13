import math
def lm_to_point(lm, w, h):
    return int(lm.x * w), int(lm.y * h)

def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


WRIST = 0
THUMB_TIP = 4
INDEX_MCP = 5
FINGER_TIPS = [8, 12, 16, 20]

def is_bsl_a(landmarks, w, h, thumb_index_thresh=0.12, finger_fold_thresh=0.12):
    try:
        min_side = min(w, h)

        wrist = lm_to_point(landmarks.landmark[WRIST], w, h)
        thumb = lm_to_point(landmarks.landmark[THUMB_TIP], w, h)
        index_mcp = lm_to_point(landmarks.landmark[INDEX_MCP], w, h)

        for i in FINGER_TIPS:
            tip = lm_to_point(landmarks.landmark[i], w, h)
            if distance(tip, wrist) > min_side + finger_fold_thresh:
                return False

        if distance(thumb, index_mcp) > min_side + thumb_index_thresh:
            return False

        return True
    except Exception:
        return False