#!/usr/bin/env python3
import usb.core
import usb.util
import subprocess
import sys
import time
import signal
import os

VENDOR = 0x0a5f
PRODUCT = 0x00b1

removed_module = False

def is_module_loaded(name="usblp"):
    out = subprocess.run(["lsmod"], capture_output=True, text=True)
    return name in out.stdout

def remove_module(name="usblp"):
    global removed_module
    try:
        # modprobe -r es preferible (gestiona dependencias)
        subprocess.run(["modprobe", "-r", name], check=True)
        removed_module = True
        print(f"⚙️  Módulo '{name}' removido correctamente.")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ No se pudo remover '{name}': {e}. Puedes intentar 'sudo modprobe -r {name}' manualmente.")
        # no abortamos; intentaremos detach_kernel_driver() de todas formas

def reload_module_if_needed(name="usblp"):
    global removed_module
    if removed_module:
        try:
            subprocess.run(["modprobe", name], check=True)
            print(f"🔁 Módulo '{name}' recargado correctamente.")
            removed_module = False
        except subprocess.CalledProcessError as e:
            print(f"❗ No se pudo recargar '{name}': {e}. Recarga manual con: sudo modprobe {name}")

def on_exit(signum=None, frame=None):
    print("\n🛑 Saliendo — intentando restaurar el sistema...")
    try:
        usb.util.dispose_resources(printer_ref)  # safe if exists
    except Exception:
        pass
    reload_module_if_needed()
    sys.exit(0)

# Señales para asegurar que recargamos el módulo si presionas Ctrl+C
signal.signal(signal.SIGINT, on_exit)
signal.signal(signal.SIGTERM, on_exit)

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("🔒 Debes ejecutar este script como root (sudo).")
        sys.exit(1)

    # 1) Detectar y remover usblp si está presente
    if is_module_loaded("usblp"):
        print("⚠️ Módulo usblp cargado — lo intentaremos remover temporalmente.")
        remove_module("usblp")
    else:
        print("👍 Módulo usblp no está cargado — continuando.")

    # 2) Buscar la impresora
    printer = usb.core.find(idVendor=VENDOR, idProduct=PRODUCT)
    printer_ref = printer  # para on_exit
    if printer is None:
        print("❌ Impresora no encontrada (verifica ids con lsusb).")
        reload_module_if_needed()
        sys.exit(1)

    try:
        printer.set_configuration()
        cfg = printer.get_active_configuration()
        intf = cfg[(0, 0)]
        # intentar detach si sigue ocupado
        try:
            if printer.is_kernel_driver_active(0):
                print("⚙️ Kernel driver activo, intentando detach_kernel_driver(0)...")
                printer.detach_kernel_driver(0)
                time.sleep(0.2)
        except (NotImplementedError, usb.core.USBError):
            # Algunos backends/OS no implementan is_kernel_driver_active o detach
            pass

        usb.util.claim_interface(printer, 0)
        message = "\n\n*** HOLA MUNDO (SAFE) ***\n\n".encode("ascii")

        printed = False
        for ep in range(1, 6):
            try:
                printer.write(ep, message)
                print(f"✅ Mensaje enviado (endpoint {ep}).")
                printed = True
                break
            except usb.core.USBError as e:
                # errno puede no estar presente en todas las plataformas; imprimimos info útil
                err_no = getattr(e, "errno", None)
                print(f"⚠️ Error en endpoint {ep}: {e} (errno={err_no}). Probando siguiente...")
                time.sleep(0.1)

        if not printed:
            print("❌ No se pudo imprimir en endpoints 1-5. Revisa endpoints con 'lsusb -v -d {VENDOR:04x}:{PRODUCT:04x}'.")

    except Exception as e:
        print(f"❌ Error general durante impresión: {e}")

    finally:
        try:
            usb.util.release_interface(printer, 0)
        except Exception:
            pass
        try:
            usb.util.dispose_resources(printer)
        except Exception:
            pass

        # 3) Restaurar módulo usblp si lo removimos
        reload_module_if_needed()
        print("✅ Script finalizado.")
