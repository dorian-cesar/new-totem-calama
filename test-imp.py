import usb.core
import usb.util
from datetime import datetime
import time

def print_ticket(patente):
    # Buscar la impresora Zebra KR403
    printer = usb.core.find(idVendor=0x0A5F, idProduct=0x00B1)  # IDs correctos para KR403

    if printer is None:
        print("❌ ¡Error! Impresora KR403 no encontrada.")
        return

    try:
        # Configurar la interfaz USB
        printer.set_configuration()
        cfg = printer.get_active_configuration()
        intf = cfg[(0, 0)]

        # Buscar endpoint de escritura
        endpoint = usb.util.find_descriptor(
            intf,
            custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT
        )

        if endpoint is None:
            print("❌ No se encontró endpoint de salida.")
            return

        # Generar texto del ticket
        hora_actual = datetime.now().strftime("%H:%M:%S")
        texto = (
            "\n\n"
            "-----------------------------\n"
            "     P A R K I N G  C A L A M A\n"
            "-----------------------------\n"
            f"Patente : {patente}\n"
            f"Hora     : {hora_actual}\n"
            "-----------------------------\n\n"
        )

        # Secuencia de corte para KR403 (ESC/POS estándar)
        corte = b"\x1D\x56\x42\x00"  # GS V B n  → corte completo

        # Enviar texto
        endpoint.write(texto.encode("utf-8"))

        # Esperar un momento
        time.sleep(0.5)

        # Enviar comando de corte
        endpoint.write(corte)

        print(f"🖨️ Ticket impreso y cortado correctamente ({patente})")

    except usb.core.USBError as e:
        print(f"⚠️ Error de impresión USB: {e}")

    finally:
        # Liberar recursos USB
        usb.util.release_interface(printer, 0)
        usb.util.dispose_resources(printer)
