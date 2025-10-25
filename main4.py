import mysql.connector
import evdev
import usb.core
import usb.util
import time
import sys

# Configuración de la base de datos
DB_CONFIG = {
    "host": "ls-ac361eb6981fc8da3000dad63b382c39e5f1f3cd.cylsiewx0zgx.us-east-1.rds.amazonaws.com",
    "user": "dbmasteruser",
    "password": "CP7>2fobZp<7Kja!Efy3Q+~g:as2]rJD",
    "database": "parkingAndenes",
    "ssl_disabled": True
}

# Buscar CUALQUIER dispositivo de entrada USB
def find_usb_device():
    print("🔍 Buscando TODOS los dispositivos USB...")
    try:
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        
        if not devices:
            print("❌ No se encontraron dispositivos de entrada")
            return None
            
        print(f"✅ Encontrados {len(devices)} dispositivos:")
        for i, device in enumerate(devices):
            print(f"   {i+1}. {device.name} -> {device.path}")
        
        # Usar el PRIMER dispositivo
        selected_device = devices[0]
        print(f"🎯 Usando dispositivo: {selected_device.name}")
        return selected_device
        
    except PermissionError:
        print("❌ Error de permisos. Ejecuta con: sudo python3 script.py")
        return None
    except Exception as e:
        print(f"❌ Error buscando dispositivos: {e}")
        return None

# Obtener la última patente con estado "Ingresado"
def get_latest_parking_entry():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        query = """SELECT idmov, patente FROM movParking 
                   WHERE estado = 'Ingresado' 
                   ORDER BY idmov DESC LIMIT 1"""
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            print(f"✅ Patente encontrada: {result[1]}")
        else:
            print("📭 No hay patentes con estado 'Ingresado'")
            
        return result
    except Exception as e:
        print(f"❌ Error en base de datos: {e}")
        return None

# Actualizar el estado a "Insite"
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

# Enviar datos a la impresora KR403
def print_ticket(patente):
    try:
        printer = usb.core.find(idVendor=0x0483, idProduct=0x5743)
        if printer is None:
            print("❌ Impresora no encontrada. Verifica la conexión USB.")
            return False

        printer.set_configuration()
        usb.util.claim_interface(printer, 0)

        text = f"\nPatente: {patente}\n"
        barcode = f"\x1D\x6B\x04{patente}\x00"

        printer.write(1, text.encode("ascii"))
        printer.write(1, barcode.encode("ascii"))

        usb.util.release_interface(printer, 0)
        usb.util.dispose_resources(printer)
        
        print("✅ Ticket impreso correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error imprimiendo ticket: {e}")
        return False

# Detectar CUALQUIER tipo de evento
def listen_for_button(device):
    print(f"\n🎯 ESCUCHANDO EN: {device.name}")
    print("📍 PRESIONA EL BOTÓN AHORA...")
    print("💡 Cualquier evento activará el sistema")
    print("⏹️  Ctrl+C para salir\n")
    
    event_count = 0
    
    try:
        for event in device.read_loop():
            event_count += 1
            
            # Mostrar TODOS los eventos sin filtrar
            print(f"🎯 EVENTO #{event_count}: tipo={event.type}, código={event.code}, valor={event.value}")
            
            # CUALQUIER evento del botón activa el proceso
            if event.type != 0:  # Ignorar eventos de sincronización (tipo 0)
                print("🚀 ¡EVENTO DETECTADO! Iniciando proceso...")
                
                entry = get_latest_parking_entry()
                if entry:
                    idmov, patente = entry
                    print(f"🚗 Procesando patente: {patente}")
                    
                    if print_ticket(patente):
                        if update_parking_status(idmov):
                            print("🎉 PROCESO COMPLETADO EXITOSAMENTE")
                        else:
                            print("❌ Error al actualizar estado en BD")
                    else:
                        print("❌ Error al imprimir ticket")
                else:
                    print("📭 No hay patentes para procesar")
                
                print("\n📍 Esperando siguiente pulsación...\n")
                    
    except KeyboardInterrupt:
        print("\n👋 Programa terminado por el usuario")
    except Exception as e:
        print(f"❌ Error en la escucha: {e}")

# ------------------ MAIN ------------------
if __name__ == "__main__":
    print("=" * 60)
    print("🚗 SISTEMA DE IMPRESIÓN DE TICKETS - PARKING")
    print("=" * 60)
    
    # Buscar dispositivo USB
    device = find_usb_device()
    
    if device:
        try:
            listen_for_button(device)
        except Exception as e:
            print(f"❌ Error crítico: {e}")
    else:
        print("❌ No se detectó ningún dispositivo USB")
        print("💡 Ejecuta con: sudo python3 script.py")