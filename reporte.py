# Autores: Ricardo Pereira y Johan Veracierto
# Módulo para la generación de reportes y bono de graficas.
from venta import Venta
from tarjeta import Tarjeta
import matplotlib.pyplot as plt

class Reporte:
    """Gestiona el historial de transacciones y exporta reportes en texto y gráfico."""

    def __init__(self):
        """Inicializa los contadores globales y la lista de ventas."""
        self.total_productos_vendidos = 0
        self.total_dinero_cobrado = 0.0
        self.ventas_registradas = []

    def registrar_venta(self, venta):
        # Registra una venta exitosa
        self.total_productos_vendidos += venta.cantidad
        self.total_dinero_cobrado += venta.monto_total
        self.ventas_registradas.append(venta)

    def generar_archivo_reporte(self, productos, tarjetas):
        # Crea el archivo de texto 'reporte_ventas.txt'
        dinero_real_cobrado = sum(t.total_gastado for t in tarjetas)
        productos_reales_vendidos = sum(p.vendidos for p in productos)
        try:
            with open("reporte_ventas.txt", "w", encoding="utf-8") as f:
                f.write("REPORTE DE SISTEMA MAQUINA EXPENDEDORA\n\n\n")
                f.write("  REPORTE DE PRODUCTOS\n\n")
                for p in productos:
                    f.write(f"     Coordenada: {p.coordenada} / Nombre: {p.nombre} / Código: {p.codigo}\n")
                    f.write(f"     Stock inicial: {p.stock_inicial}\n")
                    f.write(f"     Stock actual: {p.stock}\n")
                    f.write(f"     Cantidad de vendidos: {p.vendidos}\n\n")
                
                f.write("\n  RESUMEN GENERAL\n\n")
                f.write(f"     Total productos vendidos (acumulado): {self.total_productos_vendidos}\n")
                f.write(f"     Total productos vendidos (reales en inventario): {productos_reales_vendidos}\n")
                f.write(f"     Total dinero cobrado (acumulado): ${self.total_dinero_cobrado:.2f}\n")
                f.write(f"     Total dinero cobrado (reales de tarjetas): ${dinero_real_cobrado:.2f}\n")
            print("Archivo 'reporte_ventas.txt' generado exitosamente.")
        except Exception as e:
            print(f"Error al escribir el archivo de reporte: {e}")

    def generar_graficos(self, productos, tarjetas):
        # Bono de graficas usando Matplotlib.
        # plt.subplots: Crea el lienzo principal (fig) dividido en 1 fila y 3 columnas.
        # ax1, ax2 y ax3 son los 3 "sub-gráficos" individuales dentro de ese lienzo.
        # figsize=(18, 5) establece el ancho y alto de la imagen en pulgadas.
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 5))

        #GRÁFICO 1 (ax1): Productos más vendidos
        nombres = [p.nombre for p in productos if p.vendidos > 0]
        vendidos = [p.vendidos for p in productos if p.vendidos > 0]
        
        if nombres:
            # ax1.bar: Construye las barras verticales. Recibe los nombres en X y las cantidades en Y.
            ax1.bar(nombres, vendidos, color='skyblue', edgecolor='black')
            # ax1.set_title: Coloca el título superior de esta sección.
            ax1.set_title('Unidades Vendidas por Producto', fontweight='bold')
            # ax1.set_ylabel: Coloca la etiqueta textual del eje vertical.
            ax1.set_ylabel('Cantidad')
            ax1.tick_params(axis='x', rotation=45)
            ax1.tick_params(axis='x', labelsize=8)
        else:
            #Dibuja un texto libre en el centro
            ax1.text(0.5, 0.5, 'Sin datos de ventas', ha='center', va='center', fontsize=12)
            ax1.set_title('Unidades Vendidas por Producto', fontweight='bold')

        # GRÁFICO 2 (ax2): Distribución de ingresos 
        usuarios = [f"User...{t.hash_numero[:6]}" for t in tarjetas if t.total_gastado > 0]
        gastos = [t.total_gastado for t in tarjetas if t.total_gastado > 0]
        
        if gastos:
            # ax2.pie: Construye el gráfico circular. 
            # autopct='%1.1f%%' calcula y dibuja el porcentaje dentro de cada rebanada.
            # startangle=90 gira el gráfico para que la primera rebanada empiece desde arriba.
            ax2.pie(gastos, labels=usuarios, autopct='%1.1f%%', startangle=90, colors=['#ff9999','#66b3ff','#99ff99','#ffcc99'])
            ax2.set_title('Consumo de Dinero por Usuario', fontweight='bold')
        else:
            ax2.text(0.5, 0.5, 'Sin gastos registrados', ha='center', va='center', fontsize=12)
            ax2.set_title('Consumo de Dinero por Usuario', fontweight='bold')
            # ax2.axis('off'): Oculta las líneas de los ejes X e Y ya que un texto vacío no los necesita.
            ax2.axis('off')
            
        #GRÁFICO 3 (ax3): Evolución del dinero
        if self.ventas_registradas:
            historico_montos = []
            acumulado = 0.0
            for v in self.ventas_registradas:
                acumulado += v.monto_total
                historico_montos.append(acumulado)
            
            # ax3.plot: Dibuja una línea continua conectando puntos. marker='o' pone círculos en cada vértice.
            ax3.plot(range(1, len(historico_montos) + 1), historico_montos, marker='o', color='green', linewidth=2)
            ax3.set_title('Evolución de Ingresos Totales', fontweight='bold')
            ax3.set_xlabel('Número de Transacción')
            ax3.set_ylabel('Total Cobrado ($)')
            # ax3.grid: Dibuja una cuadrícula de fondo con líneas punteadas ('--') y semitransparentes (alpha=0.5).
            ax3.grid(True, linestyle='--', alpha=0.5)
        else:
            ax3.text(0.5, 0.5, 'Sin transacciones\npara graficar', ha='center', va='center', fontsize=12)
            ax3.set_title('Evolución de Ingresos Totales', fontweight='bold')
            ax3.grid(True, linestyle='--', alpha=0.5)

        # plt.tight_layout: Ajusta automáticamente los espacios entre los 3 gráficos para que no choquen.
        plt.tight_layout()
        # plt.savefig: Exporta y guarda el lienzo completo en el disco duro como una imagen PNG.
        plt.savefig("grafico_ventas.png", dpi=150)
        # plt.close: Libera la memoria de la computadora borrando el gráfico temporal.
        plt.close()
        print("Imagen integrada 'grafico_ventas.png' guardada de forma exitosa.")