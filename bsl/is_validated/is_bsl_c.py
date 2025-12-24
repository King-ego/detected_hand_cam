import logging
import math

from bsl.validated import lm_to_point, distance

logger = logging.getLogger(__name__)

def is_bsl_c(landmarks, w, h,
             open_dist_thresh=0.10,
             circ_var_thresh=0.20,
             finger_fold_thresh=0.07,
             min_span_deg=90,
             max_span_deg=260):
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

        tip_indices = [8, 12, 16, 20]  # pontas dos 4 dedos
        pip_indices = [6, 10, 14, 18]  # PIP correspondentes (verificação de dobra)

        # distâncias radiais dos tips e polegar ao centro da palma
        dists = []
        for ti in tip_indices:
            pt = lm_to_point(landmarks.landmark[ti], w, h)
            dists.append(distance(pt, palm_center))
        dists.append(distance(thumb_tip, palm_center))

        # 1) verificar abertura mínima (não muito fechado)
        min_open = open_dist_thresh * min_side
        if any(d <= min_open for d in dists):
            print("Falhou aqui 1")
            logger.debug("Algum dedo muito próximo da palma (muito fechado)")
            return False

        # 2) verificar se há muitos folds (PIP -> TIP deve ser razoável)
        for pip_idx, tip_idx in zip(pip_indices, tip_indices):
            pip = lm_to_point(landmarks.landmark[pip_idx], w, h)
            tip = lm_to_point(landmarks.landmark[tip_idx], w, h)
            if distance(pip, tip) < finger_fold_thresh * min_side:
                print("Falhou aqui 2")
                logger.debug("Dedo possivelmente dobrado (PIP->TIP curto)")
                return False

        # 3) variação radial: usar mediana para ser independente do tamanho da mão
        sorted_d = sorted(dists)
        median = sorted_d[len(sorted_d) // 2]
        if median == 0:
            print("Falhou aqui 3")
            logger.debug("median radius zero")
            return False
        if (max(dists) - min(dists)) > circ_var_thresh * median:
            print("Falhou aqui 4")
            logger.debug("Variação radial entre pontas muito grande (relativa à mediana)")
            return False

        # 4) cobertura angular (calcular span circular que engloba os pontos)
        angles = []
        for ti in tip_indices + [4]:  # incluir polegar
            pt = lm_to_point(landmarks.landmark[ti], w, h)
            ang = math.degrees(math.atan2(pt[1] - palm_center[1], pt[0] - palm_center[0]))
            if ang < 0:
                ang += 360.0
            angles.append(ang)

        angles.sort()
        n = len(angles)
        gaps = [((angles[(i + 1) % n] - angles[i]) + 360.0) % 360.0 for i in range(n)]
        max_gap = max(gaps)
        angular_span = 360.0 - max_gap

        if not (min_span_deg <= angular_span <= max_span_deg):
            print("Falhou aqui 5")
            logger.debug("Cobertura angular inválida: %s", angular_span)
            return False

        return True

    except Exception as e:
        logger.exception(e)
        return False