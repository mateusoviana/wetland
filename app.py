from flask import Flask, render_template, request, redirect, url_for, abort, session, jsonify
from dataclasses import dataclass

# Importa toda a lógica de negócio que já criamos
from order_processing import OrderBuilder
from shipping_calculator import ShippingContext, SedexStrategy, PacStrategy, LocalPickupStrategy
from notification_system import event_manager, EmailNotifier, SMSNotifier

app = Flask(__name__)
app.secret_key = 'wetland_ecommerce_secret_key_2024'  # Em produção, use uma chave mais segura


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
    stock: int = 10  # Adicionando controle de estoque

# Lista de vendedores fictícios
SELLERS = ["Loja do Duds", "TechMais", "GamerCenter"]

# Banco de dados em memória para simulação
# Em uma aplicação real, isso viria de um banco de dados (ex: PostgreSQL, MySQL)
PRODUCTS_DB = {
    # Loja do Duds
    1: Product(1, "Mouse Gamer Sem Fio", 180.75, "Alta precisão e resposta rápida.", "https://m.media-amazon.com/images/I/61mpMH5TzkL._AC_SL1500_.jpg", SELLERS[0], 30),
    2: Product(2, "Teclado Mecânico RGB", 350.00, "Switches mecânicos e iluminação customizável.", "https://m.media-amazon.com/images/I/71LZTxxNVxL._AC_SX679_.jpg", SELLERS[0], 15),
    3: Product(3, "Headset Gamer Redragon Zeus X", 299.90, "Som 7.1 e cancelamento de ruído.", "https://m.media-amazon.com/images/I/61Lm9hBJQhL._AC_UL480_FMwebp_QL65_.jpg", SELLERS[0], 20),
    4: Product(4, "Monitor LG Ultrawide 34\"", 2100.00, "Alta resolução para produtividade.", "https://m.media-amazon.com/images/I/81wfdDTIjHS.__AC_SY300_SX300_QL70_ML2_.jpg", SELLERS[0], 8),
    5: Product(5, "Cadeira Gamer ThunderX3", 899.99, "Design ergonômico com apoio lombar.", "https://m.media-amazon.com/images/I/517FV7zibCL._AC_SX679_.jpg", SELLERS[0], 12),

    # TechMais
    6: Product(6, "Livro Design Patterns", 120.50, "Padrões de projeto em software.", "https://m.media-amazon.com/images/I/41l2KFHRcFL._SY445_SX342_.jpg", SELLERS[1], 25),
    7: Product(7, "HD Externo Seagate 2TB", 479.00, "Armazenamento portátil e confiável.", "https://m.media-amazon.com/images/I/81o5zJ+FcPL._AC_SY300_SX300_.jpg", SELLERS[1], 18),
    8: Product(8, "Webcam Logitech C920s", 389.00, "Full HD com tampa de privacidade.", "https://m.media-amazon.com/images/I/61SCZyiMSNL.__AC_SX300_SY300_QL70_ML2_.jpg", SELLERS[1], 22),
    9: Product(9, "Roteador TP-Link AX1800", 349.90, "Wi-Fi 6 de alto desempenho.", "https://m.media-amazon.com/images/I/41QJnIHY48L._AC_SX679_.jpg", SELLERS[1], 14),
    10: Product(10, "Placa de Vídeo RTX 3060", 2399.90, "Ideal para jogos e criação.", "https://m.media-amazon.com/images/I/71tduSp8ooL._AC_SX679_.jpg", SELLERS[1], 6),

    # GamerCenter
    11: Product(11, "Controle Xbox Series", 399.90, "Conexão sem fio e USB-C.", "https://m.media-amazon.com/images/I/61qX3f8v5kL._AC_UL480_FMwebp_QL65_.jpg", SELLERS[2], 16),
    12: Product(12, "Fonte Corsair 650W", 529.90, "80 Plus Bronze e modular.", "https://m.media-amazon.com/images/I/81j8XMBwIwL._AC_UL480_FMwebp_QL65_.jpg", SELLERS[2], 10),
    13: Product(13, "SSD Kingston NV2 1TB", 449.00, "NVMe PCIe Gen4 de alta velocidade.", "https://m.media-amazon.com/images/I/71NfMZKkpQL._AC_UL480_FMwebp_QL65_.jpg", SELLERS[2], 24),
    14: Product(14, "Base Cooler para Notebook", 139.90, "Com LEDs e 5 ventoinhas.", "https://m.media-amazon.com/images/I/51L-D6a7EaL._AC_UL480_FMwebp_QL65_.jpg", SELLERS[2], 28),
    15: Product(15, "Echo Dot (5ª Geração)", 379.00, "Smart speaker com Alexa.", "https://m.media-amazon.com/images/I/71xoR4A6q-L._AC_UL480_FMwebp_QL65_.jpg", SELLERS[2], 19),
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

    # Adicionar dados do carrinho
    cart_items, cart_total = get_cart_items()
    
    return render_template(
        'index.html',
        products=products,
        sellers=SELLERS,
        selected_seller=seller_filter,
        min_price=min_price,
        max_price=max_price,
        cart_items=cart_items,
        cart_total=cart_total
    )



@app.route('/order/<int:order_id>')
def view_order(order_id):
    """Mostra os detalhes de um pedido específico."""
    order = ORDERS_DB.get(order_id)
    if not order:
        abort(404)  # Erro se o pedido não for encontrado
    
    # Calcular custos de frete para diferentes métodos
    total_weight = len(order.products) * 0.5  # Estimativa de 0.5kg por produto
    distance_km = 100  # Distância estimada

    # Calcular custos usando diferentes estratégias
    sedex_strategy = SedexStrategy()
    pac_strategy = PacStrategy()
    local_pickup_strategy = LocalPickupStrategy()

    shipping_context = ShippingContext(sedex_strategy)
    sedex_cost = shipping_context.execute_calculation(weight_kg=total_weight, distance_km=distance_km)

    shipping_context = ShippingContext(pac_strategy)
    pac_cost = shipping_context.execute_calculation(weight_kg=total_weight, distance_km=distance_km)

    shipping_context = ShippingContext(local_pickup_strategy)
    local_pickup_cost = shipping_context.execute_calculation(weight_kg=total_weight, distance_km=distance_km)
    
    cart_items, cart_total = get_cart_items()
    return render_template('order.html', 
                         order=order,
                         cart_items=cart_items,
                         cart_total=cart_total,
                         sedex_cost=sedex_cost,
                         pac_cost=pac_cost,
                         local_pickup_cost=local_pickup_cost)

@app.route('/order/<int:order_id>/update_shipping', methods=['POST'])
def update_shipping(order_id):
    """Atualiza o método de envio do pedido."""
    order = ORDERS_DB.get(order_id)
    if not order or order.status != 'Pending':
        abort(404)

    shipping_method = request.form.get('shipping_method')
    if not shipping_method:
        abort(400)

    # Calcular novo custo de frete
    total_weight = len(order.products) * 0.5
    distance_km = 100

    # Selecionar estratégia baseada no método escolhido
    if shipping_method == 'sedex':
        strategy = SedexStrategy()
    elif shipping_method == 'pac':
        strategy = PacStrategy()
    else:  # local_pickup
        strategy = LocalPickupStrategy()

    shipping_context = ShippingContext(strategy)
    new_shipping_cost = shipping_context.execute_calculation(weight_kg=total_weight, distance_km=distance_km)

    # Atualizar apenas o custo do frete
    order.shipping_cost = new_shipping_cost

    return redirect(url_for('view_order', order_id=order_id))

@app.route('/order/<int:order_id>/next_status', methods=['POST'])
def next_status(order_id):
    """Avança o status de um pedido (demonstra o Padrão State)."""
    order = ORDERS_DB.get(order_id)
    if order:
        order.proceed_to_next_status()
    return redirect(url_for('view_order', order_id=order_id))

@app.route('/account')
def account():
    # Get all orders stored in the ORDERS_DB
    # Assuming you have a global ORDERS_DB dictionary storing the orders
    orders = list(ORDERS_DB.values())
    return render_template('account.html', orders=orders)

@app.route('/produto/<int:product_id>')
def product_page(product_id):
    product = PRODUCTS_DB.get(product_id)
    if not product:
        abort(404)
    
    cart_items, cart_total = get_cart_items()
    return render_template('product.html', 
                         product=product,
                         cart_items=cart_items,
                         cart_total=cart_total)

@app.route('/comprar/<int:product_id>', methods=['POST'])
def comprar(product_id):
    product = PRODUCTS_DB.get(product_id)
    if not product:
        abort(404)

    builder = OrderBuilder()
    new_order_id = len(ORDERS_DB) + 1
    builder.set_id(new_order_id)
    builder.add_product(product.name, product.price)

    # Simula peso e envio
    total_weight = 0.5
    shipping_strategy = SedexStrategy()
    shipping_context = ShippingContext(shipping_strategy)
    shipping_cost = shipping_context.execute_calculation(weight_kg=total_weight, distance_km=100)

    builder.apply_shipping(shipping_cost)
    new_order = builder.build()
    ORDERS_DB[new_order.id] = new_order

    return redirect(url_for('view_order', order_id=new_order.id))

# --- SISTEMA DE CARRINHO ---

def get_cart():
    """Retorna o carrinho da sessão ou cria um novo."""
    if 'cart' not in session:
        session['cart'] = {}
    return session['cart']

def add_to_cart(product_id, quantity=1):
    """Adiciona um produto ao carrinho."""
    cart = get_cart()
    product_id = str(product_id)
    
    if product_id in cart:
        cart[product_id] += quantity
    else:
        cart[product_id] = quantity
    
    session['cart'] = cart
    session.modified = True

def remove_from_cart(product_id):
    """Remove um produto do carrinho."""
    cart = get_cart()
    product_id = str(product_id)
    
    if product_id in cart:
        del cart[product_id]
        session['cart'] = cart
        session.modified = True

def update_cart_quantity(product_id, quantity):
    """Atualiza a quantidade de um produto no carrinho."""
    cart = get_cart()
    product_id = str(product_id)
    
    if quantity <= 0:
        remove_from_cart(product_id)
    else:
        cart[product_id] = quantity
        session['cart'] = cart
        session.modified = True

def get_cart_items():
    """Retorna os itens do carrinho com detalhes dos produtos."""
    cart = get_cart()
    items = []
    total = 0
    
    for product_id, quantity in cart.items():
        product = PRODUCTS_DB.get(int(product_id))
        if product:
            item_total = product.price * quantity
            items.append({
                'product': product,
                'quantity': quantity,
                'item_total': item_total
            })
            total += item_total
    
    return items, total

def clear_cart():
    """Limpa o carrinho."""
    session['cart'] = {}
    session.modified = True

# --- ROTAS DO CARRINHO ---

@app.route('/carrinho/adicionar/<int:product_id>', methods=['POST'])
def add_to_cart_route(product_id):
    """Adiciona um produto ao carrinho."""
    product = PRODUCTS_DB.get(product_id)
    if not product:
        abort(404)
    
    quantity = int(request.form.get('quantity', 1))
    add_to_cart(product_id, quantity)
    
    # Retorna JSON para requisições AJAX ou redireciona
    if request.is_json or request.headers.get('Content-Type') == 'application/json':
        cart_items, cart_total = get_cart_items()
        return jsonify({
            'success': True,
            'message': f'{product.name} adicionado ao carrinho!',
            'cart_count': len(cart_items),
            'cart_total': cart_total
        })
    
    # Se foi chamado da página inicial, redireciona com parâmetro para abrir carrinho
    referrer = request.referrer or url_for('index')
    if 'produto' not in referrer:  # Se não veio da página de produto individual
        return redirect(url_for('index') + '?cart=open')
    
    return redirect(referrer)

@app.route('/carrinho/remover/<int:product_id>', methods=['POST'])
def remove_from_cart_route(product_id):
    """Remove um produto do carrinho."""
    remove_from_cart(product_id)
    
    if request.is_json or request.headers.get('Content-Type') == 'application/json':
        cart_items, cart_total = get_cart_items()
        return jsonify({
            'success': True,
            'message': 'Produto removido do carrinho!',
            'cart_count': len(cart_items),
            'cart_total': cart_total
        })
    
    return redirect(request.referrer or url_for('index'))

@app.route('/carrinho/atualizar/<int:product_id>', methods=['POST'])
def update_cart_route(product_id):
    """Atualiza a quantidade de um produto no carrinho."""
    quantity = int(request.form.get('quantity', 0))
    update_cart_quantity(product_id, quantity)
    
    if request.is_json or request.headers.get('Content-Type') == 'application/json':
        cart_items, cart_total = get_cart_items()
        return jsonify({
            'success': True,
            'message': 'Carrinho atualizado!',
            'cart_count': len(cart_items),
            'cart_total': cart_total
        })
    
    return redirect(request.referrer or url_for('index'))

@app.route('/carrinho/limpar', methods=['POST'])
def clear_cart_route():
    """Limpa o carrinho."""
    clear_cart()
    
    if request.is_json or request.headers.get('Content-Type') == 'application/json':
        return jsonify({
            'success': True,
            'message': 'Carrinho limpo!',
            'cart_count': 0,
            'cart_total': 0
        })
    
    return redirect(request.referrer or url_for('index'))

@app.route('/carrinho/finalizar', methods=['POST'])
def checkout():
    """Finaliza a compra com os itens do carrinho ou compra direta."""
    
    # Verifica se é uma compra direta
    direct_buy_id = request.form.get('direct_buy')
    if direct_buy_id:
        product = PRODUCTS_DB.get(int(direct_buy_id))
        if not product:
            abort(404)
        
        # Criar pedido com apenas este produto
        builder = OrderBuilder()
        new_order_id = len(ORDERS_DB) + 1
        builder.set_id(new_order_id)
        
        builder.add_product(product.name, product.price)
        total_weight = 0.5  # Simula 0.5kg por produto
        
        # Calcular frete
        shipping_strategy = SedexStrategy()
        shipping_context = ShippingContext(shipping_strategy)
        shipping_cost = shipping_context.execute_calculation(weight_kg=total_weight, distance_km=100)
        
        builder.apply_shipping(shipping_cost)
        
        # Criar pedido
        new_order = builder.build()
        ORDERS_DB[new_order.id] = new_order
        
        return redirect(url_for('view_order', order_id=new_order.id))
    
    # Compra normal com carrinho
    cart_items, cart_total = get_cart_items()
    
    if not cart_items:
        return redirect(url_for('index'))
    
    # Criar pedido com os itens do carrinho
    builder = OrderBuilder()
    new_order_id = len(ORDERS_DB) + 1
    builder.set_id(new_order_id)
    
    total_weight = 0
    for item in cart_items:
        product = item['product']
        quantity = item['quantity']
        for _ in range(quantity):
            builder.add_product(product.name, product.price)
            total_weight += 0.5  # Simula 0.5kg por produto
    
    # Calcular frete
    shipping_strategy = SedexStrategy()
    shipping_context = ShippingContext(shipping_strategy)
    shipping_cost = shipping_context.execute_calculation(weight_kg=total_weight, distance_km=100)
    
    builder.apply_shipping(shipping_cost)
    
    # Criar pedido
    new_order = builder.build()
    ORDERS_DB[new_order.id] = new_order
    
    # Limpar carrinho após finalizar compra
    clear_cart()
    
    return redirect(url_for('view_order', order_id=new_order.id))

if __name__ == '__main__':
    # Roda o servidor web no modo de desenvolvimento
    app.run(debug=True, port=5001)