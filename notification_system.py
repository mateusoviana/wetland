# notification_system.py
from abc import ABC, abstractmethod
from typing import List, Dict

# --- Interfaces Observer e Subject ---
class Observer(ABC):
    """Interface para os 'observadores' que reagem a eventos."""
    @abstractmethod
    def update(self, event_type: str, data: any):
        pass

class Subject:
    """Gerencia os observadores e notifica sobre eventos."""
    def __init__(self):
        self._observers: Dict[str, List[Observer]] = {}

    def subscribe(self, event_type: str, observer: Observer):
        if event_type not in self._observers:
            self._observers[event_type] = []
        self._observers[event_type].append(observer)

    def unsubscribe(self, event_type: str, observer: Observer):
        if event_type in self._observers:
            self._observers[event_type].remove(observer)

    def notify(self, event_type: str, data: any):
        if event_type in self._observers:
            for observer in self._observers[event_type]:
                observer.update(event_type, data)

# --- Implementações Concretas de Observadores ---
class EmailNotifier(Observer):
    def update(self, event_type: str, data: any):
        print(f"📧 EMAIL: Evento '{event_type}' ocorreu. Dados: {data}")

class SMSNotifier(Observer):
    def update(self, event_type: str, data: any):
        print(f"📱 SMS: Evento '{event_type}' ocorreu. Dados: {data}")

# Instância global do gerenciador de eventos para ser usado na aplicação
event_manager = Subject()