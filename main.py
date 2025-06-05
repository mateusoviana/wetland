# main.py
from user_management import UserFactory
from order_processing import OrderBuilder
from shipping_calculator import ShippingContext, SedexStrategy, PacStrategy
from notification_system import event_manager, EmailNotifier, SMSNotifier


def run_ecommerce_simulation():
    print("--- 🚀 INICIANDO SIMULAÇÃO DO E-COMMERCE ---\n")

    # 1. Configurar Notificações (Padrão Observer)
    email_notifier = EmailNotifier()
    sms_notifier = SMSNotifier()

    # Clientes e vendedores se inscrevem em eventos
    event_manager.subscribe("order:created", email_notifier)
    event_manager.subscribe("order:paid", email_notifier)
    event_manager.subscribe("order:paid", sms_notifier)
    event_manager.subscribe("order:shipped", email_notifier)
    event_manager.subscribe("order:delivered", email_notifier)

    print("--- 1. Sistema de Notificação Configurado ---\n")

    # 2. Criar Usuários (Padrão Factory Method)
    customer = UserFactory.create_user("customer")
    seller = UserFactory.create_user("seller")
    print(f"Cliente criado com permissões: {customer.get_permissions()}")
    print(f"Vendedor criado com permissões: {seller.get_permissions()}\n")

    print("--- 2. Usuários Criados ---\n")

    # 3. Calcular Frete (Padrão Strategy)
    shipping_strategy = SedexStrategy()  # Escolhendo a estratégia de frete
    shipping_context = ShippingContext(shipping_strategy)
    shipping_cost = shipping_context.execute_calculation(weight_kg=2.5, distance_km=350.0)
    print(f"Custo do frete (Sedex) calculado: R${shipping_cost:.2f}\n")

    print("--- 3. Frete Calculado ---\n")

    # 4. Construir um Pedido (Padrão Builder)
    print("Cliente está montando um pedido...")
    order_builder = OrderBuilder()
    order = (order_builder
             .set_id(101)
             .add_product("Livro de Python", 99.90)
             .add_product("Mouse Gamer", 150.00)
             .apply_shipping(shipping_cost)
             .build())

    print(f"Pedido finalizado: {order}\n")
    print("--- 4. Pedido Construído ---\n")

    # 5. Processar o Status do Pedido (Padrão State)
    print("Iniciando processamento do pedido...")
    order.proceed_to_next_status()  # Pending -> Paid
    order.proceed_to_next_status()  # Paid -> Shipped
    order.proceed_to_next_status()  # Shipped -> Delivered

    print(f"\nStatus final do pedido: {order.status}\n")
    print("--- 5. Pedido Processado ---\n")

    print("--- ✅ SIMULAÇÃO FINALIZADA ---")


if __name__ == "__main__":
    run_ecommerce_simulation()