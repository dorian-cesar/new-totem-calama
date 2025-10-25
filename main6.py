import mysql.connector
import requests
import usb.core
import usb.util
import sys
import time

# ================== CONFIGURACIÓN ==================
DB_CONFIG = {
    "host": "ls-ac361eb6981fc8da3000dad63b382c39e5f1f3cd.cylsiewx0zgx.us-east-1.rds.amazonaws.com",
    "user": "dbmasteruser",
    "password": "CP7>2fobZp<7Kja!Efy3Q+~g:as2]rJD",
    "database": "parkingAndenes",
    "ssl_disabled": True
}

API_URL = "https://zkteco.terminal-calama.com/zteco-backend/openEntrada.php"
# ===================================================

def get_latest_parking_entry():
    try:
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
    except Exception as e:
        print(f"❌ Error en base de datos: {e}")
        return None

def update_parking_status(idmov):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        query = "UPDATE movParking SET estado = 'Insite' WHERE idmov = %s"
        cursor.execute(query, (idmov,))
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Estado actualizado a 'Insite'")
        return True
    except Exception as e:
        print(f"❌ Error actualizando estado: {e}")
        return False

def call_api():
    try:
        response = requests.get(API_URL, timeout=5)
        if response.status_code == 200:
            print("🌐 API llamada exitosamente.")
            return True
        else:
            print(f"⚠️ Error en la API: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error al llamar la API: {e}")
        return False

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

def main():
    print("=" * 50)
    print("🚗 SISTEMA DE PARKING - IMPRESIÓN DE TICKETS")
    print("=" * 50)
    print("✅ Sistema iniciado. Presiona ENTER para procesar ingreso.")
    print("⏹️  Ctrl+C para salir\n")
    
    while True:
        try:
            input()  # Espera a que se presione Enter
            print("\n🔘 Botón presionado, procesando...")
            
            entry = get_latest_parking_entry()
            if entry:
                idmov, patente = entry
                print(f"🚗 Patente encontrada: {patente}")
                
                # Imprimir ticket
                print_ticket(patente)
                
                # Actualizar estado en BD
                if update_parking_status(idmov):
                    # Llamar API
                    if call_api():
                        print("🎉 PROCESO COMPLETADO EXITOSAMENTE")
                    else:
                        print("⚠️  Proceso completado con error en API")
                else:
                    print("❌ Error al actualizar estado en BD")
            else:
                print("⚠️ No hay registros con estado 'Ingresado' y tipo 'Parking'.")
            
            print("\n📍 Esperando siguiente pulsación...\n")
            
        except KeyboardInterrupt:
            print("\n👋 Sistema terminado por el usuario")
            break
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            print("\n📍 Reintentando...\n")

if __name__ == "__main__":
    main()