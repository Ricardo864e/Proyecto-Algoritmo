# Autores: Ricardo Pereira y Johan Veracierto
# Módulo de los productos.

class Producto:
    # Representa un producto dentro de la máquina expendedora.
    
    def __init__(self, codigo, nombre, precio, stock, mensaje_despedida, coordenada):
        # Inicializa un producto con sus datos básicos.
        
        self.codigo = codigo
        self.nombre = nombre
        self.precio = precio
        self.stock = stock
        self.stock_inicial = stock
        self.mensaje_despedida = mensaje_despedida
        self.coordenada = coordenada
        self.vendidos = 0

    def actualizar_stock(self, cantidad):
        # Reduce el inventario si hay disponibilidad.
        if self.stock >= cantidad:
            self.stock -= cantidad
            self.vendidos += cantidad
            return True
        return False