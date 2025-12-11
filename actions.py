import os
import cv2
import shutil
import threading
from datetime import datetime

LAST_ACTION = None
_PENDING = {"timer": None, "name": None}

def _set_last(name, meta):
    global LAST_ACTION
    LAST_ACTION = (name, meta)

def _run_action(name, annotated):
    cb = ACTIONS.get(name)
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

def action_swipe_left(annotated):
    print("Ação: swipe left")
    _set_last("swipe_left", {})

def action_swipe_right(annotated):
    print("Ação: swipe right")
    _set_last("swipe_right", {})

def action_pinch(annotated):
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(temp_dir, f"pinch_{ts}.jpg")
    cv2.imwrite(filename, annotated)
    _set_last("pinch", {"path": filename})
    print(f"Pinch: screenshot salvo em {filename}")

def action_open(annotated):
    temp_dir = 'temp'
    if not os.path.exists(temp_dir):
        print("Pasta temp não existe.")
        return
    removed = 0
    for name in os.listdir(temp_dir):
        path = os.path.join(temp_dir, name)
        try:
            if os.path.isfile(path) or os.path.islink(path):
                os.remove(path)
                removed += 1
            elif os.path.isdir(path):
                shutil.rmtree(path)
                removed += 1
        except Exception as e:
            print(f"Erro removendo {path}: {e}")
    print(f"Pasta temp limpa, {removed} item(s) removido(s).")
    print("Ação: open hand")

def action_fist(annotated):
    print("Ação: fist")
    _set_last("fist", {})

def action_clear_last(annotated):
    clear_last_action()

def clear_last_action():
    global LAST_ACTION
    if not LAST_ACTION:
        print("Nenhuma ação anterior para limpar.")
        return
    name, meta = LAST_ACTION
    if name == "pinch":
        path = meta.get("path")
        if path and os.path.exists(path):
            try:
                os.remove(path)
                print(f"Arquivo de pinch removido: {path}")
            except Exception as e:
                print(f"Erro removendo arquivo {path}: {e}")
        else:
            print("Arquivo de pinch não encontrado para remover.")
    elif name == "open_hand":
        moved = meta.get("moved", [])
        restored = 0
        for src, dst in moved:
            # dst é caminho atual, src é caminho original
            if os.path.exists(dst):
                try:
                    # garante diretório destino original exista
                    os.makedirs(os.path.dirname(src), exist_ok=True)
                    shutil.move(dst, src)
                    restored += 1
                except Exception as e:
                    print(f"Erro restaurando {dst} -> {src}: {e}")
        # tenta remover pasta de lixo se vazia
        trash_dir = meta.get("trash_dir")
        try:
            if trash_dir and os.path.isdir(trash_dir) and not os.listdir(trash_dir):
                os.rmdir(trash_dir)
        except Exception:
            pass
        print(f"Restaurados {restored} item(s) da limpeza anterior.")
    else:
        print(f"Limpeza da última ação: {name} (nenhuma reversão implementada).")
    LAST_ACTION = None

ACTIONS = {
    "swipe_left": action_swipe_left,
    "swipe_right": action_swipe_right,
    "pinch": action_pinch,
    "open_hand": action_open,
    "fist": action_fist,
    "clear_last": action_clear_last,
}
