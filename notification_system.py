# notification_system.py
from abc import ABC, abstractmethod
from typing import List, Dict
from email_service import email_service

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
    """Notificador por email integrado com o EmailService."""
    
    def update(self, event_type: str, data: any):
        """Processa eventos e envia emails apropriados."""
        try:
            if event_type == "order_created":
                # Enviar email de confirmação de pedido
                sucesso = email_service.email_pedido_criado(data)
                if sucesso:
                    print(f"✅ Email de confirmação enviado para pedido #{data.get('order_id', 'N/A')}")
                else:
                    print(f"❌ Falha ao enviar email de confirmação para pedido #{data.get('order_id', 'N/A')}")
                    
            elif event_type == "order_status_changed":
                # Enviar email de atualização de status
                sucesso = email_service.email_status_atualizado(data)
                if sucesso:
                    print(f"✅ Email de status enviado para pedido #{data.get('order_id', 'N/A')} - Status: {data.get('status', 'N/A')}")
                else:
                    print(f"❌ Falha ao enviar email de status para pedido #{data.get('order_id', 'N/A')}")
                    
            else:
                # Evento não reconhecido, apenas log
                print(f"📧 EMAIL: Evento '{event_type}' recebido. Dados: {data}")
                
        except Exception as e:
            print(f"❌ Erro no EmailNotifier: {e}")


# Instância global do gerenciador de eventos para ser usado na aplicação
event_manager = Subject()

email_notifier = EmailNotifier()

# Inscrever observadores nos eventos
event_manager.subscribe("order_created", email_notifier)
event_manager.subscribe("order_status_changed", email_notifier)