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
    description: str
    image_url: str
    seller: str  # Novo campo

# Lista de vendedores fictícios
SELLERS = ["Loja do Duds", "TechMais", "GamerCenter"]

# Banco de dados em memória para simulação
# Em uma aplicação real, isso viria de um banco de dados (ex: PostgreSQL, MySQL)
PRODUCTS_DB = {
    # Loja do Duds
    1: Product(1, "Mouse Gamer Sem Fio", 180.75, "Alta precisão e resposta rápida.", "https://m.media-amazon.com/images/I/61mpMH5TzkL._AC_SL1500_.jpg", SELLERS[0]),
    2: Product(2, "Teclado Mecânico RGB", 350.00, "Switches mecânicos e iluminação customizável.", "https://m.media-amazon.com/images/I/71LZTxxNVxL._AC_SX679_.jpg", SELLERS[0]),
    3: Product(3, "Headset Gamer Redragon Zeus X", 299.90, "Som 7.1 e cancelamento de ruído.", "https://m.media-amazon.com/images/I/61Lm9hBJQhL._AC_UL480_FMwebp_QL65_.jpg", SELLERS[0]),
    4: Product(4, "Monitor LG Ultrawide 34\"", 2100.00, "Alta resolução para produtividade.", "https://m.media-amazon.com/images/I/81wfdDTIjHS.__AC_SY300_SX300_QL70_ML2_.jpg", SELLERS[0]),
    5: Product(5, "Cadeira Gamer ThunderX3", 899.99, "Design ergonômico com apoio lombar.", "https://m.media-amazon.com/images/I/517FV7zibCL._AC_SX679_.jpg", SELLERS[0]),

    # TechMais
    6: Product(6, "Livro Design Patterns", 120.50, "Padrões de projeto em software.", "https://m.media-amazon.com/images/I/41l2KFHRcFL._SY445_SX342_.jpg", SELLERS[1]),
    7: Product(7, "HD Externo Seagate 2TB", 479.00, "Armazenamento portátil e confiável.", "https://m.media-amazon.com/images/I/81o5zJ+FcPL._AC_SY300_SX300_.jpg", SELLERS[1]),
    8: Product(8, "Webcam Logitech C920s", 389.00, "Full HD com tampa de privacidade.", "https://m.media-amazon.com/images/I/61SCZyiMSNL.__AC_SX300_SY300_QL70_ML2_.jpg", SELLERS[1]),
    9: Product(9, "Roteador TP-Link AX1800", 349.90, "Wi-Fi 6 de alto desempenho.", "https://m.media-amazon.com/images/I/41QJnIHY48L._AC_SX679_.jpg", SELLERS[1]),
    10: Product(10, "Placa de Vídeo RTX 3060", 2399.90, "Ideal para jogos e criação.", "https://m.media-amazon.com/images/I/71tduSp8ooL._AC_SX679_.jpg", SELLERS[1]),

    # GamerCenter
    11: Product(11, "Controle Xbox Series", 399.90, "Conexão sem fio e USB-C.", "https://m.media-amazon.com/images/I/61qX3f8v5kL._AC_UL480_FMwebp_QL65_.jpg", SELLERS[2]),
    12: Product(12, "Fonte Corsair 650W", 529.90, "80 Plus Bronze e modular.", "https://m.media-amazon.com/images/I/81j8XMBwIwL._AC_UL480_FMwebp_QL65_.jpg", SELLERS[2]),
    13: Product(13, "SSD Kingston NV2 1TB", 449.00, "NVMe PCIe Gen4 de alta velocidade.", "https://m.media-amazon.com/images/I/71NfMZKkpQL._AC_UL480_FMwebp_QL65_.jpg", SELLERS[2]),
    14: Product(14, "Base Cooler para Notebook", 139.90, "Com LEDs e 5 ventoinhas.", "https://m.media-amazon.com/images/I/51L-D6a7EaL._AC_UL480_FMwebp_QL65_.jpg", SELLERS[2]),
    15: Product(15, "Echo Dot (5ª Geração)", 379.00, "Smart speaker com Alexa.", "https://m.media-amazon.com/images/I/71xoR4A6q-L._AC_UL480_FMwebp_QL65_.jpg", SELLERS[2]),
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
    if request.method == 'POST':
        selected_ids = request.form.getlist('product_ids')
        if not selected_ids:
            return redirect(url_for('index'))

        builder = OrderBuilder()
        new_order_id = len(ORDERS_DB) + 1
        builder.set_id(new_order_id)

        total_weight = 0
        for product_id in selected_ids:
            product = PRODUCTS_DB[int(product_id)]
            builder.add_product(product.name, product.price)
            total_weight += 0.5  # peso estimado

        shipping_strategy = SedexStrategy()
        shipping_context = ShippingContext(shipping_strategy)
        shipping_cost = shipping_context.execute_calculation(weight_kg=total_weight, distance_km=100)

        builder.apply_shipping(shipping_cost)
        new_order = builder.build()
        ORDERS_DB[new_order.id] = new_order

        return redirect(url_for('view_order', order_id=new_order.id))

    # --- GET: aplicar filtros ---
    products = list(PRODUCTS_DB.values())
    
    seller_filter = request.args.get("seller")
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)

    if seller_filter:
        products = [p for p in products if p.seller == seller_filter]

    if min_price is not None:
        products = [p for p in products if p.price >= min_price]

    if max_price is not None:
        products = [p for p in products if p.price <= max_price]

    return render_template(
        'index.html',
        products=products,
        sellers=SELLERS,
        selected_seller=seller_filter,
        min_price=min_price,
        max_price=max_price
    )



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

@app.route('/produto/<int:product_id>')
def product_page(product_id):
    product = PRODUCTS_DB.get(product_id)
    if not product:
        abort(404)
    return render_template('product.html', product=product)


if __name__ == '__main__':
    # Roda o servidor web no modo de desenvolvimento
    app.run(debug=True, port=5001)