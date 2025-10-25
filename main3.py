import mysql.connector
#import usb.core
#import usb.util
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

# Obtener la última patente con estado "Ingresado"
def get_latest_parking_entry():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    query = """SELECT idmov, patente FROM movParking 
               WHERE estado = 'Ingresado' and tipo= 'Parking'
               ORDER BY idmov DESC LIMIT 1"""
    cursor.execute(query)
    result = cursor.fetchone()
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
    #printer = usb.core.find(idVendor=0x0483, idProduct=0x5743)  # ID de la KR403
    #if printer is None:
    #    print("¡Error! Impresora no encontrada")
    #    return
    #
    ## Activar la interfaz
    #printer.set_configuration()
    #usb.util.claim_interface(printer, 0)
    #
    ## Texto y código de barras
    #text = f"\nPatente: {patente}\n"
    #barcode = f"\x1D\x6B\x04{patente}\x00"  # Formato GS1-128 para KR403
    #
    ## Enviar datos
    #printer.write(1, text.encode("ascii"))
    #printer.write(1, barcode.encode("ascii"))
    #
    ## Liberar la impresora
    #usb.util.release_interface(printer, 0)
    #usb.util.dispose_resources(printer)
    #
    print(f"Ticket simulado para patente: {patente}")

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

# ------------------ MAIN ------------------
if __name__ == "__main__":
    print("Ejecutando script automáticamente...\n")
    
    entry = get_latest_parking_entry()
    if entry:
        idmov, patente = entry
        print(f"Última patente ingresada: {patente}")
        print_ticket(patente)
        update_parking_status(idmov)
        print("Estado actualizado a 'Insite'")
        call_api()
    else:
        print("No hay registros con estado 'Ingresado'.")
