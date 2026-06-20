# Autores: Ricardo Pereira y Johan Veracierto
"""Revisa las tarjetas prepagadas y su saldo."""
import hashlib

class Tarjeta:
    
    def __init__(self, id_tarjeta, saldo):
        self.id_original = str(id_tarjeta)
        self.hash_numero = hashlib.sha256(self.id_original.encode()).hexdigest()
        self.saldo = float(saldo)
        self.total_gastado = 0.0

    def verificar_saldo(self, monto):
        # Comprueba si la tarjeta tiene fondos suficientes.
        return self.saldo >= monto

    def descontar_saldo(self, monto):
        # Resta el monto del saldo si existen fondos suficientes.
        if self.verificar_saldo(monto):
            self.saldo -= monto
            self.total_gastado += monto
            return True
        return False