import threading
import logging
from typing import Optional, Dict, Union
from threading import Timer


from bsl.actions.bsl_a import bsl_a
from bsl.actions.bsl_b import bsl_b
from bsl.actions.bsl_c import bsl_c
from bsl.actions.bsl_d import bsl_d
from bsl.actions.bsl_e import bsl_e
from bsl.actions.bsl_f import bsl_f
from bsl.actions.bsl_g import bsl_g
from bsl.actions.bsl_h import bsl_h

logger = logging.getLogger(__name__)
#Não esquecer bsl = Brazilian Sign Language
LAST_ACTION = None
_PENDING: Dict[str, Optional[Union[Timer, str]]] = {"timer": None, "name": None}

def _run_action(name, annotated):
    cb = ACTIONS.get(name)
    if not cb:
        print(f"Action '{name}' not found")
        return
    try:
        cb(annotated)
    except Exception as e:
        print(f"Error executing action '{name}': {e}")
    finally:
        if _PENDING.get("name") == name:
            _PENDING["timer"] = None
            _PENDING["name"] = None

def schedule_action(name, annotated, delay=0.6):
    if _PENDING.get("timer"):
        try:
            _PENDING["timer"].cancel()
        except Exception as e:
            logger.exception(f"Error: {e}")
            pass
        _PENDING["timer"] = None
        _PENDING["name"] = None
    t = threading.Timer(delay, _run_action, args=(name, annotated))
    _PENDING["timer"] = t
    _PENDING["name"] = name
    t.start()

def cancel_pending_action():
    if _PENDING.get("timer"):
        try:
            _PENDING["timer"].cancel()
        except Exception as e:
            logger.exception(f"Exception cancelling timer: {e}")
            pass
        print(f"Ação pendente '{_PENDING.get('name')}' cancelada")
        _PENDING["timer"] = None
        _PENDING["name"] = None
    else:
        print("Not pending action to cancel")

ACTIONS = {
    'bsl_a': bsl_a,
    'bsl_b': bsl_b,
    'bsl_c': bsl_c,
    'bsl_d': bsl_d,
    'bsl_e': bsl_e,
    'bsl_f': bsl_f,
    'bsl_g': bsl_g,
}