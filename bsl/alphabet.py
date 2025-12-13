import threading
#Não esquecer bsl = Brazilian Sign Language
LAST_ACTION = None
_PENDING = {"timer": None, "name": None}

def _bsl_a(annotated):
    print(f"A, Ação: BSL A")

def _run_action(name, annotated):
    cb = ACTIONS.get(name)
    print(f"name: {name} and annotated: {annotated.shape}")
    if not cb:
        print(f"Ação desconhecida: {name}")
        return
    try:
        cb(annotated)
    except Exception as e:
        print(f"Erro executando ação '{name}': {e}")
    finally:
        if _PENDING.get("name") == name:
            _PENDING["timer"] = None
            _PENDING["name"] = None

def schedule_action(name, annotated, delay=0.6):
    if _PENDING.get("timer"):
        try:
            _PENDING["timer"].cancel()
        except Exception:
            pass
        _PENDING["timer"] = None
        _PENDING["name"] = None
    t = threading.Timer(delay, _run_action, args=(name, annotated))
    _PENDING["timer"] = t
    _PENDING["name"] = name
    t.start()
    print(f"Ação agendada: {name} em {delay}s")

def cancel_pending_action():
    if _PENDING.get("timer"):
        try:
            _PENDING["timer"].cancel()
        except Exception:
            pass
        print(f"Ação pendente '{_PENDING.get('name')}' cancelada")
        _PENDING["timer"] = None
        _PENDING["name"] = None
    else:
        print("Nenhuma ação pendente para cancelar")

ACTIONS = {
    'bsl_a': _bsl_a,
}