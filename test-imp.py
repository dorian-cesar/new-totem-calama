import os
from datetime import datetime

# Configuración de la impresora CUPS
PRINTER_NAME = "ZebraRaw"  # Debe coincidir con la cola RAW creada en CUPS

def imprimir_ticket_zebra(patente):
    # Obtener hora actual
    hora_actual = datetime.now().strftime("%H:%M:%S")

    # Plantilla ZPL del ticket
    zpl = f"""
^XA
^MMC,Y
^FO60,50^A0N,40,40^FDPatente:^FS
^FO60,100^A0N,80,80^FD{patente}^FS
^FO60,200^A0N,40,40^FDHora: {hora_actual}^FS
~JK
^XZ
"""

    # Guardar temporalmente el archivo
    with open("ticket_temp.zpl", "w") as f:
        f.write(zpl)

    # Enviar a la impresora ZebraRaw mediante CUPS
    resultado = os.system(f'lp -d {PRINTER_NAME} ticket_temp.zpl')

    if resultado == 0:
        print(f"🖨️ Ticket impreso correctamente: {patente} - {hora_actual}")
    else:
        print("❌ Error al imprimir el ticket.")

# ---------------------------
# TEST LOCAL
# ---------------------------
if __name__ == "__main__":
    imprimir_ticket_zebra("ABC123")
