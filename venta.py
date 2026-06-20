# Autores: Ricardo Pereira y Johan Veracierto
# Módulo que gestiona el registro de ventas de la máquina.
from datetime import datetime

class Venta:
    
    def __init__(self, producto_codigo, producto_nombre, cantidad, monto_total, tarjeta_hash):
        self.producto_codigo = producto_codigo
        self.producto_nombre = producto_nombre
        self.cantidad = cantidad
        self.monto_total = monto_total
        self.tarjeta_hash = tarjeta_hash
        
        # Fecha y hora automática de la transacción
        self.fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")