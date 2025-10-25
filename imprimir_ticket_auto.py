import os
import subprocess
from datetime import datetime

IMPRESORA = "Zebra_Technologies_ZTC_KR403"

def verificar_modo_zpl():
    """
    Consulta a la impresora el modo actual de lenguaje.
    Retorna True si ya está en ZPL, False en caso contrario.
    """
    try:
        # Enviamos comando de consulta
        resultado = subprocess.run(
            f'echo "! U1 getvar \"device.languages\"" | lp -d {IMPRESORA}',
            shell=True,
            capture_output=True,
            text=True
        )
        salida = resultado.stdout + resultado.stderr
        if "zpl" in salida.lower():
            print("✅ La impresora ya está en modo ZPL.")
            return True
        else:
            print("⚠️ La impresora NO está en modo ZPL (respuesta:", salida.strip(), ")")
            return False
    except Exception as e:
        print("❌ Error verificando el modo de la impresora:", e)
        return False


def cambiar_a_zpl():
    """
    Envía el comando para poner la impresora en modo ZPL.
    """
    print("🔄 Cambiando impresora a modo ZPL...")
    os.system(f'echo "! U1 setvar \"device.languages\" \"zpl\"" | lp -d {IMPRESORA}')
    print("✅ Modo ZPL activado.")


def imprimir_ticket_zebra(patente):
    """
    Genera y envía un ticket en formato ZPL a la impresora Zebra.
    """
    hora_actual = datetime.now().strftime("%H:%M:%S")
    zpl = f"""
^XA
^FO50,50^A0N,50,50^FDPatente:^FS
^FO50,110^A0N,70,70^FD{patente}^FS
^FO50,200^A0N,40,40^FDHora: {hora_actual}^FS
^FO50,260^A0N,30,30^FDEste ticket se imprimió correctamente^FS
~JK
^XZ
"""
    with open("ticket.zpl", "w") as f:
        f.write(zpl)
    
    os.system(f'lp -d {IMPRESORA} ticket.zpl')
    print(f"🖨️ Ticket enviado: {patente} - {hora_actual}")


if __name__ == "__main__":
    # 1️⃣ Verificar si la impresora está en modo ZPL
    if not verificar_modo_zpl():
        cambiar_a_zpl()
    
    # 2️⃣ Imprimir un ticket de prueba
    imprimir_ticket_zebra("ABC123")
