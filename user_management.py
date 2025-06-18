# user_management.py
from abc import ABC, abstractmethod

# --- Interfaces e Classes Abstratas ---
class User(ABC):
    """Interface abstrata para todos os tipos de usuário."""
    @abstractmethod
    def get_permissions(self):
        pass

# --- Implementações Concretas ---
class Customer(User):
    """Representa um cliente da plataforma."""
    def get_permissions(self):
        return ["BROWSE_PRODUCTS", "BUY_PRODUCTS", "VIEW_ORDERS"]

class Seller(User):
    """Representa um vendedor da plataforma."""
    def get_permissions(self):
        return ["MANAGE_PRODUCTS", "VIEW_SALES", "MANAGE_COUPONS"]

# --- Fábrica (Factory) ---
class UserFactory:
    """Fábrica para criar objetos de usuário."""
    @staticmethod
    def create_user(user_type: str) -> User:
        if user_type.lower() == "customer":
            return Customer()
        elif user_type.lower() == "seller":
            return Seller()
        raise ValueError(f"Tipo de usuário desconhecido: {user_type}")