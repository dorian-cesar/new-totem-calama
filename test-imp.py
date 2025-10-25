import usb.core
import usb.util
from datetime import datetime
import time

def find_zebra_kr403():
    """
    Busca la impresora Zebra KR403 conectada por USB
    y retorna el objeto USB si se encuentra.
    """
    # IDs según tu lsusb
    printer = usb.core.find(idVendor=0x0A5F, idProduct=0x00B1)
    if printer is None:
        print("❌ Impresora KR403 no encontrada")
    return printer

def get_out_endpoint(printer):
    """
    Detecta automáticamente el endpoint de salida (OUT) válido
    de la impresora KR403.
    """
    cfg = printer.get_active_configuration()
    intf = cfg[(0, 0)]
    # Buscar endpoint de salida
    endpoints = [ep for ep in intf.endpoints() if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_OUT]
    if not endpoints:
        print("❌ No se encontró ningún endpoint de salida")
        return None
    # Retornar el primero disponible
    return endpoints[0]

def print_ticket(patente):
    printer = find_zebra_kr403()
    if printer is None:
        return

    try:
        # Configurar interfaz USB
        printer.set_configuration()
        usb.util.claim_interface(printer, 0)

        endpoint = get_out_endpoint(printer)
        if endpoint is None:
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

        # Comando de corte completo de KR403 (ESC/POS estándar)
        corte = b"\x1D\x56\x42\x00"  # GS V B n

        # Enviar texto
        endpoint.write(texto.encode("utf-8"))
        time.sleep(1)  # Dar tiempo al buffer

        # Enviar corte de papel
        endpoint.write(corte)
        time.sleep(0.5)

        print(f"🖨️ Ticket impreso y cortado correctamente: {patente}")

    except usb.core.USBError as e:
        print(f"⚠️ Error de impresión USB: {e}")

    finally:
        # Liberar recursos
        usb.util.release_interface(printer, 0)
        usb.util.dispose_resources(printer)

# ----------------------
# Prueba rápida
if __name__ == "__main__":
    # Reemplaza "ABC123" con la patente real
    print_ticket("ABC123")
