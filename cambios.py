class Tarjeta:
    
    def __init__(self, numero_hash, saldo):
        self.hash_numero = numero_hash
        self.saldo = saldo
        self.total_gastado = 0.0

    def verificar_saldo(self, monto):
        return self.saldo >= monto

    def descontar_saldo(self, monto):
        if self.verificar_saldo(monto):
            self.saldo -= monto
            self.total_gastado += monto
            return True
        return False
    
    def cargar_datos_locales(self):
        """
        Manejo de Archivos (Lectura): Carga el estado de la máquina desde un archivo JSON local.
        Si el archivo no existe, cumple estrictamente el PDF iniciando la máquina vacía.
        """
        if os.path.exists("maquina_data.json"):
            try:
                with open("maquina_data.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Rehidratación de objetos Producto si el archivo existe
                    for coord, p_data in data["inventario"].items():
                        p = Producto(p_data["codigo"], p_data["nombre"], p_data["precio"], p_data["stock"], p_data["mensaje_despedida"], coord)
                        p.stock_inicial = p_data.get("stock_inicial", p_data["stock"])
                        p.vendidos = p_data.get("vendidos", 0)
                        self.inventario[coord] = p
                    
                    # Rehidratación de objetos Tarjeta
                    self.tarjetas_validas = []
                    for t_data in data["tarjetas"]:
                        t = Tarjeta("123", 0)
                        t.hash_numero = t_data["hash_numero"]
                        t.saldo = t_data["saldo"]
                        t.total_gastado = t_data.get("total_gastado", 0.0)
                        self.tarjetas_validas.append(t)
                return  # Si todo sale bien, termina la función aquí
            except Exception:
                pass # Si el archivo está corrupto, continúa abajo para resetear la máquina
                
        # =========================================================================
        # CORRECCIÓN AQUÍ: SI NO EXISTE EL ARCHIVO (Instrucción estricta del PDF)
        # =========================================================================
        print("AVISO: Archivo local 'maquina_data.json' no encontrado.")
        print("Suponiendo máquina vacía según las indicaciones del proyecto...")
        
        # 1. El inventario se inicializa COMPLETAMENTE VACÍO
        self.inventario = {}  
        
        # 2. Las tarjetas bancarias base se inicializan para permitir operar el sistema
        numeros_base = ["1234567890", "9876543210", "1223334444", "4444333221", "1010101010"]
        self.tarjetas_validas = [Tarjeta(num, 50.0) for num in numeros_base]
        
        # 3. Guardamos este estado inicial (máquina vacía) en el disco duro
        self.guardar_datos_locales()

    def guardar_datos_locales(self):
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
        except Exception:
            pass
import hashlib

texto = "1010101010"
hash_calculado = hashlib.sha256(texto.encode()).hexdigest()

print("El hash SHA-256 es:", hash_calculado)