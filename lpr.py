import mysql.connector
import requests
import sys
import time
import usb.core
import usb.util
from datetime import datetime

# ================== CONFIGURACIÓN ==================
DB_CONFIG = {
    "host": "ls-ac361eb6981fc8da3000dad63b382c39e5f1f3cd.cylsiewx0zgx.us-east-1.rds.amazonaws.com",
    "user": "dbmasteruser",
    "password": "CP7>2fobZp<7Kja!Efy3Q+~g:as2]rJD",
    "database": "parkingAndenes"
}

API_URL = "https://zkteco.terminal-calama.com/zteco-backend/openEntrada.php"
# ===================================================


# Obtener la última patente con estado "Ingresado" y tipo "Parking"
def get_latest_parking_entry():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    query = """SELECT idmov, patente FROM movParking 
               WHERE estado = 'Ingresado' AND tipo = 'Parking'
               ORDER BY idmov DESC LIMIT 1"""
    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result


# Actualizar el estado a "Insite"
def update_parking_status(idmov):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    query = "UPDATE movParking SET estado = 'Insite' WHERE idmov = %s"
    cursor.execute(query, (idmov,))
    conn.commit()
    cursor.close()
    conn.close()


# Llamar a la API
def call_api():
    try:
        response = requests.get(API_URL, timeout=5)
        if response.status_code == 200:
            print("🌐 API llamada exitosamente.")
        else:
            print(f"⚠️ Error en la API: {response.status_code}")
    except Exception as e:
        print(f"❌ Error al llamar la API: {e}")


# Imprimir ticket en impresora Zebra KR403
def print_ticket(patente):
    try:
        # Buscar la impresora KR403 (Zebra)
        printer = usb.core.find(idVendor=0x0483, idProduct=0x5743)

        if printer is None:
            print("❌ Impresora Zebra KR403 no encontrada.")
            return

        # Activar la configuración e interfaz
        printer.set_configuration()
        usb.util.claim_interface(printer, 0)

        # Generar texto y hora
        hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # ZPL: lenguaje de impresión de Zebra
        zpl = f"""
^XA
^FO50,50^A0N,50,50^FDPatente:^FS
^FO50,110^A0N,70,70^FD{patente}^FS
^FO50,200^A0N,40,40^FDHora: {hora_actual}^FS
^XZ
"""
        printer.write(1, zpl.encode("ascii"))
        print(f"🖨️ Ticket impreso correctamente: {patente} - {hora_actual}")

        # Liberar recursos
        usb.util.release_interface(printer, 0)
        usb.util.dispose_resources(printer)

    except Exception as e:
        print(f"❌ Error al imprimir: {e}")


# ================== MAIN ==================
def main():
    print("✅ Sistema iniciado. Presiona ENTER en el dispositivo LinTx para procesar ingreso.\n")
    while True:
        sys.stdin.readline()  # Espera Enter del lector LinTx
        print("🔘 Botón presionado, procesando...")

        entry = get_latest_parking_entry()
        if entry:
            idmov, patente = entry
            print(f"Última patente ingresada: {patente}")
            update_parking_status(idmov)
            print("Estado actualizado a 'Insite'")
            call_api()
            print_ticket(patente)
        else:
            print("⚠️ No hay registros con estado 'Ingresado' y tipo 'Parking'.")

        print("\nEsperando siguiente pulsación...\n")


if __name__ == "__main__":
    main()
