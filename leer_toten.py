import evdev

# Encuentra los dispositivos disponibles
devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
for device in devices:
    print(device.path, device.name, device.phys)  # Muestra la ruta y nombre del dispositivo

# Reemplaza '/dev/input/eventX' con la ruta del botón USB
device_path = '/dev/input/event2'  # Ajusta según el resultado del listado

try:
    device = evdev.InputDevice(device_path)
    print(f"Escuchando en {device.name}...")

    for event in device.read_loop():
        if event.type == evdev.ecodes.EV_KEY and event.value == 1:  # 1 = Presionado
            print(f"Botón presionado: {evdev.categorize(event).keycode}")

except PermissionError:
    print("⚠️ No tienes permisos. Intenta ejecutar con sudo o agregar tu usuario al grupo input:")
    print("   sudo usermod -aG input $USER && newgrp input")
