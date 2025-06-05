# shipping_calculator.py
from abc import ABC, abstractmethod

# --- Interface da Estratégia ---
class ShippingStrategy(ABC):
    @abstractmethod
    def calculate(self, weight_kg: float, distance_km: float) -> float:
        pass

# --- Estratégias Concretas ---
class SedexStrategy(ShippingStrategy):
    def calculate(self, weight_kg: float, distance_km: float) -> float:
        # Lógica de cálculo para Sedex (exemplo)
        return 10.0 + (weight_kg * 3.5) + (distance_km * 0.1)

class PacStrategy(ShippingStrategy):
    def calculate(self, weight_kg: float, distance_km: float) -> float:
        # Lógica de cálculo para PAC (exemplo)
        return 5.0 + (weight_kg * 2.5) + (distance_km * 0.05)

class LocalPickupStrategy(ShippingStrategy):
    def calculate(self, weight_kg: float, distance_km: float) -> float:
        return 0.0 # Retirada no local não tem custo de frete

# --- Contexto ---
class ShippingContext:
    def __init__(self, strategy: ShippingStrategy):
        self._strategy = strategy

    def execute_calculation(self, weight_kg: float, distance_km: float) -> float:
        return self._strategy.calculate(weight_kg, distance_km)