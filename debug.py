import evdev
from evdev import InputDevice, list_devices, categorize

print("=== Explorando dispositivos LinTx ===")
devices = [InputDevice(path) for path in list_devices()]
candidatos = [dev for dev in devices if "LinTx" in dev.name]

if not candidatos:
    print("No se encontró ningún dispositivo LinTx.")
    exit()

for dev in candidatos:
    print(f"\nProbando {dev.path} -> {dev.name}")
    print("Presiona el botón ahora... (Ctrl+C para salir)")

    try:
        for event in dev.read_loop():
            print(f"Evento detectado: type={event.type}, code={event.code}, value={event.value}")
    except Exception as e:
        print(f"Error leyendo {dev.path}: {e}")
