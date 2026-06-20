# Autores: Ricardo Pereira y Johan Veracierto

import json      # Maneja la lectura y escritura de archivos de texto en formato JSON.
import os        # Revisa si los archivos existen en la carpeta del sistema lo hace asi: os.path.exists.
import hashlib   # Hace el hash de la tarjeta
import requests  # Realiza peticiones HTTP para descargar desde GitHub.

from producto import Producto  
from tarjeta import Tarjeta    
from venta import Venta        
from reporte import Reporte    

BASE_URL = "https://github.com/FernandoSapient/BPTSP05_2526-3"

class Maquina:

    def __init__(self):
        self.inventario = {}
        self.tarjetas_validas = []
        self.repositorio_url = BASE_URL
        self.gestor_reporte = Reporte()
        self.filas = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14"]
        self.columnas = ["A", "B", "C", "D"]
    
    def conectar_github_api(self):
        """Actualiza los precios locales con el archivo JSON en GitHub."""
        url_raw = "https://raw.githubusercontent.com/FernandoSapient/BPTSP05_2526-3/main/maquina_data.json"
        
        try:
            print("Sincronizando precios con el repositorio remoto de GitHub...")
            respuesta = requests.get(url_raw, timeout=5)
            
            if respuesta.status_code == 200:
                datos_remotos = respuesta.json()
                inventario_remoto = datos_remotos.get("inventario", {})
                
                cambios_detectados = False
                for coord, p_remoto in inventario_remoto.items():
                    if coord in self.inventario:
                        precio_remoto = float(p_remoto.get("precio", 0))
                        # Si el precio remoto es diferente, actualiza la propiedad local
                        if self.inventario[coord].precio != precio_remoto:
                            print(f"-> Actualizando precio de {self.inventario[coord].nombre}: ${self.inventario[coord].precio} => ${precio_remoto}")
                            self.inventario[coord].precio = precio_remoto
                            cambios_detectados = True
                
                if cambios_detectados:
                    self.guardar_datos_locales()
                    print("Sincronización completada. Precios actualizados localmente.")
                else:
                    print("Todos los precios están al día.")
            else:
                print("No se pudo sincronizar: El servidor respondió con un error.")
                
        except Exception as e:
            # Si falla la conexión a internet, se mantiene el programa corriendo con los datos locales
            print("Aviso: No se pudo conectar al repositorio de GitHub. Usando precios locales.")
    
    def iniciar_sistema(self):
        """Arranca la máquina cargando la base de datos local y buscando actualizaciones en la nube."""
        self.cargar_datos_locales()
        self.conectar_github_api()

    def mostrar_catalogo(self):
        """Imprime el catalogo de los productos."""
        print(f"{'CATÁLOGO DE PRODUCTOS DISPONIBLES'}")
        ancho_celda = 20
        
        # Construcción del encabezado de columnas.
        encabezado_columnas = "     " 
        for col in self.columnas:
            encabezado_columnas += f"{col:^{ancho_celda}}" 
        print(encabezado_columnas)
        print("    " + "-" * (len(self.columnas) * ancho_celda))
        
        # Impresión de cada una de las filas activas en el inventario
        for fila in self.filas:
            linea_productos = f"{fila:>2} | "
            for col in self.columnas:
                coord = f"{fila}{col}"
                prod = self.inventario.get(coord)
                
                # Solo muestra el código si el producto existe y tiene unidades disponibles
                if prod and prod.stock > 0:
                    texto_celda = f"{prod.codigo}"
                else:
                    texto_celda = ""
                    
                linea_productos += f"{texto_celda:^{ancho_celda}}"
            print(linea_productos)
            
        print("     " + "-" * (len(self.columnas) * ancho_celda) + "\n")

    def procesar_venta(self, coordenada):
        """Hace el proceso de compra."""
        prod: Producto = self.inventario.get(coordenada)
        
        # Validaciones.
        if not prod:
            print("Error: Coordenada invalida")
            return
        if prod.stock <= 0:
            print(f"Producto agotado: {prod.nombre}")
            return
            
        print(f"Producto seleccionado: {prod.nombre}")
        print(f"Precio:{prod.precio:.2f}")
        
        confirmacion = input(f"¿Desea confirmar la compra de {prod.nombre}? (Si/No): ").strip().upper()
        if confirmacion != "SI":
            print("Operacion cancelada")
            return

        # Captura y hash inmediato del número de tarjeta.
        num_tarjeta = input("Ingrese su número de tarjeta: ").strip()   
        hash_ingresado = hashlib.sha256(num_tarjeta.encode()).hexdigest()
        tarjeta_cliente = None
        
        # Búsqueda de la tarjeta dentro de la lista de clientes.
        for t in self.tarjetas_validas:
            if t.hash_numero == hash_ingresado:
                tarjeta_cliente = t
                break
                
        if not tarjeta_cliente:
            print("Error: Tarjeta no válida")
            return
            
        if not tarjeta_cliente.verificar_saldo(prod.precio):
            print(f"Error: Saldo insuficiente: {tarjeta_cliente.saldo:.2f}")
            return
            
        # Ejecución del cobro y actualización de stock
        tarjeta_cliente.descontar_saldo(prod.precio)
        prod.actualizar_stock(1)
        
        # Registro formal del ticket en el módulo de reportes
        nueva_venta = Venta(prod.codigo, prod.nombre, 1, prod.precio, tarjeta_cliente.hash_numero)
        self.gestor_reporte.registrar_venta(nueva_venta)
        
        print(f"Dispensando producto... {prod.nombre}")
        print(f"{prod.mensaje_despedida}")
        self.guardar_datos_locales()

    def realizar_restock(self):
        """Permite al stocker añadir inventario o expandir los límites de la máquina."""
        print("RESTOCK DE INVENTARIO")
        print("Opcion 1: Actualizar stock de un producto existente")
        print("Opcion 2: Actualizar un producto por completo")
        opcion = input("Seleccione opcion (1 o 2): ").strip()
        
        if opcion not in ["1", "2"]:
            print("Error: Opción inválida.")
            return
            
        coord = input("Ingrese coordenada del producto.\n Ejemplo (1C, primero el numero de la fila y luego la columna).\n-->").strip().upper()

        if opcion == "1":
            if coord in self.inventario:
                producto = self.inventario[coord]
                print(f"\n El producto a modificar es: {producto.nombre}")
            else:
                print("Error: Coordenada vacía. No hay un producto asignado aquí para actualizar.")
                return
            
            try:
                cantidad = int(input("Ingrese cantidad a añadir: "))
                if cantidad < 0:
                    raise ValueError
                
                self.inventario[coord].stock += cantidad
                self.inventario[coord].stock_inicial = self.inventario[coord].stock
                print(f"Stock actualizado exitosamente. Nuevo stock: {self.inventario[coord].stock}")
                self.guardar_datos_locales() 
                
            except ValueError:
                print("Error: Número inválido.")
                
        elif opcion == "2":
            # Validación y lógica matemática para la expansión consecutiva de la matriz (Bono)
            if coord not in self.inventario:
                if len(coord) in [2, 3]:
                    nueva_fila = coord[0]
                    nueva_columna = coord[1]
                    
                    fila_siguiente_valida = str(int(self.filas[-1]) + 1)
                    columna_siguiente_valida = chr(ord(self.columnas[-1]) + 1)
                    
                    # Caso A: Añadir una nueva fila consecutiva hacia abajo
                    if nueva_fila == fila_siguiente_valida and nueva_columna in self.columnas:
                        self.filas.append(nueva_fila)
                        print(f"-> Se ha añadido la fila {nueva_fila} al sistema.")
                    
                    # Caso B: Añadir una nueva columna consecutiva hacia la derecha
                    elif nueva_columna == columna_siguiente_valida and nueva_fila in self.filas:
                        self.columnas.append(nueva_columna)
                        print(f"-> Se ha añadido la columna {nueva_columna} al sistema.")
                    
                    # Caso C: Añadir una nueva celda en la esquina diagonal de expansión
                    elif nueva_fila == fila_siguiente_valida and nueva_columna == columna_siguiente_valida:
                        self.filas.append(nueva_fila)
                        self.columnas.append(nueva_columna)
                        print(f"-> Se añadieron la fila {nueva_fila} y columna {nueva_columna}.")
                    
                    else:
                        print("Error: La coordenada no es consecutiva. No se pueden dejar casilleros vacios.")
                        return
                else:
                    print("Error: Formato de coordenada inválido (Debe ser de 2 caracteres, ej: 6E).")
                    return

            # Creación.
            codigo = input("Ingrese el código del producto: ").strip()
            nombre = input("Ingrese nombre del producto: ").strip()
            try:
                precio = float(input("Ingrese precio: "))
                stock = int(input("Ingrese la cantidad de stock: "))
                msg = input("Ingrese mensaje de despedida: ").strip()
                
                self.inventario[coord] = Producto(codigo, nombre, precio, stock, msg, coord)
                print(f"Coordenada {coord} registrada exitosamente con el producto: {nombre}")
                self.guardar_datos_locales()
                
            except ValueError:
                print("Error: Datos numéricos incorrectos.")

    def solicitar_reporte(self):
        """Ordena la exportación del archivo TXT, las gráficas estadísticas y evalúa encoger la matriz."""
        lista_productos = list(self.inventario.values())
        
        self.gestor_reporte.generar_archivo_reporte(lista_productos, self.tarjetas_validas)
        self.gestor_reporte.generar_graficos(lista_productos, self.tarjetas_validas)
        
        if self.inventario:
            self._verificar_y_encoger_matriz()

    def cargar_datos_locales(self):
        """Carga el JSON local; si no existe: descarga los productos y clientes puros desde GitHub."""
        if os.path.exists("maquina_data.json"):
            try:
                with open("maquina_data.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                    # actualizar los objetos.
                    self.inventario = {}
                    for coord, p_data in data["inventario"].items():
                        p = Producto(p_data["codigo"], p_data["nombre"], p_data["precio"], p_data["stock"], p_data["mensaje_despedida"], coord)
                        p.stock_inicial = p_data.get("stock_inicial", p_data["stock"])
                        p.vendidos = p_data.get("vendidos", 0)
                        self.inventario[coord] = p
                    
                    # actualizar los objetos Tarjeta inyectando directamente sus hashes guardados
                    self.tarjetas_validas = []
                    for t_data in data["tarjetas"]:
                        t = Tarjeta("TEMPORAL", 0) 
                        t.hash_numero = t_data["hash_numero"] 
                        t.saldo = float(t_data["saldo"])
                        t.total_gastado = float(t_data.get("total_gastado", 0.0))
                        self.tarjetas_validas.append(t)
                        
                self._verificar_y_encoger_matriz()
                return 
            except Exception as e:
                print(f"Error leyendo archivo local: {e}")

        # Descarga desde cero usando las URLs raw si la máquina corre por primera vez
        print("AVISO: 'maquina_data.json' no encontrado. Descargando datos desde GitHub...")
        url_productos_raw = "https://raw.githubusercontent.com/FernandoSapient/BPTSP05_2526-3/main/productos.json"
        url_clientes_raw = "https://raw.githubusercontent.com/FernandoSapient/BPTSP05_2526-3/main/clientes.json"
        
        try:
            # Descarga de Clientes (Tarjetas)
            respuesta_tarjetas = requests.get(url_clientes_raw, timeout=5)
            if respuesta_tarjetas.status_code == 200:
                nuevas_tarjetas_json = respuesta_tarjetas.json()
                self.tarjetas_validas = [Tarjeta(t["id"], t["saldo"]) for t in nuevas_tarjetas_json]
                print(f"-> {len(self.tarjetas_validas)} tarjetas cargadas con éxito.")
            else:
                raise Exception("No se pudo obtener el JSON de tarjetas.")

            # Descarga de Productos distribuyéndolos automáticamente en una matriz de 4 columnas
            respuesta_productos = requests.get(url_productos_raw, timeout=5)
            if respuesta_productos.status_code == 200:
                nuevos_productos_json = respuesta_productos.json()
                
                self.inventario = {}
                cols_permitidas = ["A", "B", "C", "D"]
                
                for index, p_json in enumerate(nuevos_productos_json):
                    num_fila = (index // 4) + 1
                    letra_col = cols_permitidas[index % 4]
                    coord = f"{num_fila}{letra_col}"
                    
                    prod_obj = Producto(p_json["cod"], p_json["prod"], p_json["precio"], 5, p_json["despedida"], coord)
                    self.inventario[coord] = prod_obj
                    
                    if str(num_fila) not in self.filas:
                        self.filas.append(str(num_fila))
                    if letra_col not in self.columnas:
                        self.columnas.append(letra_col)
                
                self.filas.sort(key=int)
                self.columnas.sort()
                print(f"-> {len(self.inventario)} productos distribuidos en la máquina.")
            else:
                raise Exception("No se pudo obtener el JSON de productos.")
                
            self.guardar_datos_locales()
            print("Sincronización inicial exitosa. Archivo 'maquina_data.json' creado.")

        except Exception as e:
            print(f"CRÍTICO: No se pudieron descargar los datos iniciales de GitHub. {e}")
            print("El sistema iniciará vacío de forma preventiva.")
            self.inventario = {}
            self.tarjetas_validas = []
    
    def guardar_datos_locales(self):
        """Serializa y exporta el estado completo actual del inventario y tarjetas al JSON local."""
        try:
            inventario_dict = {}
            for coord, p in self.inventario.items():
                inventario_dict[coord] = {
                    "codigo": p.codigo,
                    "nombre": p.nombre,
                    "precio": p.precio,
                    "stock": p.stock, 
                    "stock_inicial": p.stock_inicial,
                    "mensaje_despedida": p.mensaje_despedida,
                    "vendidos": p.vendidos
                }
            tarjetas_list = []
            for t in self.tarjetas_validas:
                tarjetas_list.append({
                    "hash_numero": t.hash_numero,
                    "saldo": t.saldo,
                    "total_gastado": t.total_gastado
                })
            data = {"inventario": inventario_dict, "tarjetas": tarjetas_list}       
            with open("maquina_data.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error guardando datos locales: {e}")
    
    def _verificar_y_encoger_matriz(self):
        """Remueve de las listas de control aquellas filas o columnas que se queden sin productos (Bono de Encogimiento)."""
        filas_con_productos = set()
        columnas_con_productos = set()
        
        for coord in self.inventario.keys():
            if len(coord) >= 2:
                columna = coord[-1]
                fila = coord[:-1]
                
                filas_con_productos.add(fila)
                columnas_con_productos.add(columna)
        
        # Resguardo mínimo para mantener dimensiones por defecto si se vacía por completo
        if not filas_con_productos: filas_con_productos.add("1")
        if not columnas_con_productos: columnas_con_productos.add("A")
            
        self.filas = [f for f in self.filas if f in filas_con_productos]
        self.columnas = [c for c in self.columnas if c in columnas_con_productos]
        
        # Ordenamiento correcto convirtiendo filas a números temporalmente
        self.filas.sort(key=int)
        self.columnas.sort()