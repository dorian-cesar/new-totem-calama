import mysql.connector
import requests
import sys
import time
import subprocess
from datetime import datetime

# ================== CONFIGURACIÓN ==================
DB_CONFIG = {
    "host": "ls-ac361eb6981fc8da3000dad63b382c39e5f1f3cd.cylsiewx0zgx.us-east-1.rds.amazonaws.com",
    "user": "dbmasteruser",
    "password": "CP7>2fobZp<7Kja!Efy3Q+~g:as2]rJD",
    "database": "parkingAndenes"
}

API_URL = "https://zkteco.terminal-calama.com/zteco-backend/openEntrada.php"
PRINTER_NAME = "ZebraRaw"
# ===================================================

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

def update_parking_status(idmov):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    query = "UPDATE movParking SET estado = 'Insite' WHERE idmov = %s"
    cursor.execute(query, (idmov,))
    conn.commit()
    cursor.close()
    conn.close()

def call_api():
    try:
        response = requests.get(API_URL, timeout=5)
        if response.status_code == 200:
            print("🌐 API llamada exitosamente.")
        else:
            print(f"⚠️ Error en la API: {response.status_code}")
    except Exception as e:
        print(f"❌ Error al llamar la API: {e}")

def print_ticket(patente):
    """Imprime la patente y hora actual con corte automático"""
    hora_actual = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    zpl = f"""
^XA
^CF0,60
^FO80,60^FDPatente:^FS
^CF0,100
^FO80,130^FD{patente}^FS
^CF0,50
^FO80,260^FDHora: {hora_actual}^FS
^FO60,330^GB700,2,2^FS
^FO200,380^FDBienvenido al Parking!^FS
^MMC,Y
~JK
^XZ
"""
    try:
        subprocess.run(
            ["lp", "-d", PRINTER_NAME],
            input=zpl.encode("utf-8"),
            check=True
        )
        print(f"🖨️ Ticket impreso para {patente}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al imprimir: {e}")

def main():
    print("✅ Sistema iniciado. Presiona ENTER en el dispositivo LinTx para procesar ingreso.\n")
    while True:
        sys.stdin.readline()  # Espera a que se presione Enter
        print("🔘 Botón presionado, procesando...")
        entry = get_latest_parking_entry()
        if entry:
            idmov, patente = entry
            print(f"Última patente ingresada: {patente}")
            update_parking_status(idmov)
            print("Estado actualizado a 'Insite'")
            print_ticket(patente)
            call_api()
        else:
            print("⚠️ No hay registros con estado 'Ingresado' y tipo 'Parking'.")
        print("\nEsperando siguiente pulsación...\n")

if __name__ == "__main__":
    main()
