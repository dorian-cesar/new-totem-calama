import mysql.connector
import evdev
import usb.core
import usb.util
import time
import requests  

# Configuración de la base de datos
DB_CONFIG = {
    "host": "ls-ac361eb6981fc8da3000dad63b382c39e5f1f3cd.cylsiewx0zgx.us-east-1.rds.amazonaws.com",
    "user": "dbmasteruser",
    "password": "CP7>2fobZp<7Kja!Efy3Q+~g:as2]rJD",
    "database": "parkingAndenes"
}

API_URL = "https://zkteco.terminal-calama.com/zteco-backend/openEntrada.php"  # URL de la API

# Buscar un dispositivo de entrada (teclado USB)
def find_usb_keyboard():
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    for device in devices:
        print(f"Dispositivo encontrado: {device.name}")  # Imprimir los dispositivos encontrados
        if "LinTx LinTx Keyboard" in device.name:  # Buscar el nombre completo
            print(f"Dispositivo detectado: {device.name}")
            return device
    return None

# Obtener la última patente con estado "Ingresado"
def get_latest_parking_entry():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    query = """SELECT idmov, patente FROM movParking 
               WHERE estado = 'Ingresado' 
               ORDER BY idmov DESC LIMIT 1"""
    cursor.execute(query)
    result = cursor.fetchone()
    print(f"[DEBUG] Resultado obtenido: {result}")
    cursor.close()
    conn.close()
    return result  # (idmov, patente)

# Actualizar el estado a "Insite"
def update_parking_status(idmov):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    query = "UPDATE movParking SET estado = 'Insite' WHERE idmov = %s"
    cursor.execute(query, (idmov,))
    conn.commit()
    cursor.close()
    conn.close()

# Enviar datos a la impresora KR403 (Raw Printing)
def print_ticket(patente):
    printer = usb.core.find(idVendor=0x0483, idProduct=0x5743)  # ID de la KR403
    if printer is None:
        print("¡Error! Impresora no encontrada")
        return

    # Activar la interfaz
    printer.set_configuration()
    usb.util.claim_interface(printer, 0)

    # Texto y código de barras
    text = f"\nPatente: {patente}\n"
    barcode = f"\x1D\x6B\x04{patente}\x00"  # Formato GS1-128 para KR403

    # Enviar datos
    printer.write(1, text.encode("ascii"))
    printer.write(1, barcode.encode("ascii"))

    # Liberar la impresora
    usb.util.release_interface(printer, 0)
    usb.util.dispose_resources(printer)
    print("Ticket impreso correctamente")

# Llamar a la API
def call_api():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            print("API llamada exitosamente.")
        else:
            print(f"Error en la API: {response.status_code}")
    except Exception as e:
        print(f"Error al llamar la API: {e}")

# Detectar la pulsación de un botón USB (teclado)
def listen_for_button(device):
    print("Esperando pulsación del botón...")
    for event in device.read_loop():
        if event.type == evdev.ecodes.EV_KEY and event.value == 1:  # Tecla presionada
            print("Botón presionado, procesando...")
            entry = get_latest_parking_entry()
            if entry:
                idmov, patente = entry
                print(f"Última patente ingresada: {patente}")
                print_ticket(patente)
                update_parking_status(idmov)
                print("Estado actualizado a 'Insite'")
                call_api()  # Llamar a la API después de actualizar el estado
            else:
                print("No hay registros con estado 'Ingresado'.")

# ------------------ MAIN ------------------
if __name__ == "__main__":
    keyboard = find_usb_keyboard()
    if keyboard:
        listen_for_button(keyboard)
    else:
        print("No se detectó un teclado USB.")
