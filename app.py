from flask import Flask, render_template, request, redirect, url_for, abort
from dataclasses import dataclass

# Importa toda a lógica de negócio que já criamos
from order_processing import OrderBuilder
from shipping_calculator import ShippingContext, SedexStrategy
from notification_system import event_manager, EmailNotifier, SMSNotifier

app = Flask(__name__)


# --- CONFIGURAÇÃO INICIAL E DADOS MOCK (SIMULADOS) ---

# Vamos criar uma classe simples para representar nossos produtos
@dataclass
class Product:
    id: int
    name: str
    price: float


# Banco de dados em memória para simulação
# Em uma aplicação real, isso viria de um banco de dados (ex: PostgreSQL, MySQL)
PRODUCTS_DB = {
    1: Product(id=1, name="Livro de Design Patterns", price=120.50),
    2: Product(id=2, name="Teclado Mecânico RGB", price=350.00),
    3: Product(id=3, name="Mouse Gamer Sem Fio", price=180.75),
    4: Product(id=4, name="Monitor Ultrawide 34\"", price=2100.00),
}
ORDERS_DB = {}  # Usaremos para armazenar os pedidos criados

# Configurando o sistema de notificação (Observer)
# Os prints aparecerão no seu terminal quando os eventos ocorrerem
email_notifier = EmailNotifier()
sms_notifier = SMSNotifier()
event_manager.subscribe("order:created", email_notifier)
event_manager.subscribe("order:paid", email_notifier)
event_manager.subscribe("order:paid", sms_notifier)
event_manager.subscribe("order:shipped", email_notifier)


# --- ROTAS DA APLICAÇÃO WEB ---

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Página inicial.
    GET: Mostra a lista de produtos.
    POST: Cria um novo pedido com os produtos selecionados.
    """
    if request.method == 'POST':
        selected_ids = request.form.getlist('product_ids')
        if not selected_ids:
            return redirect(url_for('index'))  # Se nada for selecionado, volta para a home

        # Lógica de negócio para criar o pedido
        builder = OrderBuilder()
        new_order_id = len(ORDERS_DB) + 1
        builder.set_id(new_order_id)

        total_weight = 0
        for product_id in selected_ids:
            product = PRODUCTS_DB[int(product_id)]
            builder.add_product(product.name, product.price)
            total_weight += 0.5  # Simula 0.5kg por produto

        # Padrão Strategy para calcular o frete
        shipping_strategy = SedexStrategy()
        shipping_context = ShippingContext(shipping_strategy)
        shipping_cost = shipping_context.execute_calculation(weight_kg=total_weight, distance_km=100)  # Distância fixa

        builder.apply_shipping(shipping_cost)

        # Padrão Builder para construir o objeto final do pedido
        new_order = builder.build()
        ORDERS_DB[new_order.id] = new_order

        return redirect(url_for('view_order', order_id=new_order.id))

    # Se for GET, apenas mostra a página com a lista de produtos
    return render_template('index.html', products=list(PRODUCTS_DB.values()))


@app.route('/order/<int:order_id>')
def view_order(order_id):
    """Mostra os detalhes de um pedido específico."""
    order = ORDERS_DB.get(order_id)
    if not order:
        abort(404)  # Erro se o pedido não for encontrado
    return render_template('order.html', order=order)


@app.route('/order/<int:order_id>/next_status', methods=['POST'])
def next_status(order_id):
    """Avança o status de um pedido (demonstra o Padrão State)."""
    order = ORDERS_DB.get(order_id)
    if order:
        order.proceed_to_next_status()
    return redirect(url_for('view_order', order_id=order_id))


if __name__ == '__main__':
    # Roda o servidor web no modo de desenvolvimento
    app.run(debug=True, port=5001)