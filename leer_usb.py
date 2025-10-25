from pynput import keyboard

def on_press(key):
    try:
        print(f"Tecla presionada: {key.char}")
    except AttributeError:
        print(f"Tecla especial presionada: {key}")

# Escuchar las teclas
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()