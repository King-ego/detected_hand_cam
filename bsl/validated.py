import math
import importlib
import pkgutil
import logging

logger = logging.getLogger(__name__)

def lm_to_point(lm, w, h):
    return int(lm.x * w), int(lm.y * h)

def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

__all__ = ["lm_to_point", "distance"]

try:
    import bsl.is_validated as _pkg
    for _finder, _name, _ in pkgutil.iter_modules(_pkg.__path__):
        try:
            _mod = importlib.import_module(f"{_pkg.__name__}.{_name}")
        except Exception as e:
            logger.exception(f"Error: {e}")
            continue
        for _attr in dir(_mod):
            if _attr.startswith("is_bsl_"):
                _obj = getattr(_mod, _attr)
                if callable(_obj):
                    globals()[_attr] = _obj
                    __all__.append(_attr)
except Exception as e:
    logger.exception(f"Error: {e}")
    pass