# Autores: Ricardo Pereira y Johan Veracierto
"""Menu de la maquina."""
from maquina import Maquina

def main():
    """Inicia la máquina, carga y guarda los datos."""
    vending_machine = Maquina()
    vending_machine.iniciar_sistema()
    
    while True:
        print("\n BIENVENIDO A LA MÁQUINA EXPENDEDORA \n")
        print("A continuacion se le mostraran los productos disponibles con su coordenada:")
        vending_machine.mostrar_catalogo()
        
        print("~ Presione 'ENTER' para iniciar proceso de venta guiado")
        print("~ Escriba 'RS' para realizar restock")
        print("~ Escriba 'RP' para generar reporte")
        print("~ Escriba 'SALIR' para cerrar \n")
        
        entrada = input("Ingrese la opción que desee: ").strip().upper()
        
        # Validación de opciones válidas del menú
        while entrada != "RS" and entrada != "RP" and entrada != "SALIR" and entrada != "":
            print("ERROR: opción invalida.")
            entrada = input("Ingrese la opción que desee: ").strip().upper()
            
        if entrada == "SALIR":
            break
        elif entrada == "RS":
            vending_machine.realizar_restock()
        elif entrada == "RP":
            vending_machine.solicitar_reporte()
        elif entrada == "":
            # Proceso de venta guiada ingresando la coordenada por separado
            coord_directa = input("Ingrese coordenada: ").strip().upper()
            vending_machine.procesar_venta(coord_directa)
        else:
            vending_machine.procesar_venta(entrada)
            
        input("Presione 'ENTER' para volver al menú inicial: ")

# Llamando a la función para que realice el main o menu.
main()