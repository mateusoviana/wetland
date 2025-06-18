from flask import Flask, render_template, request, redirect, url_for, abort, session, jsonify, flash
from dataclasses import dataclass, asdict
import secrets
import json
import os
from datetime import datetime

# Importa toda a lógica de negócio que já criamos
from order_processing import OrderBuilder, Order
from shipping_calculator import ShippingContext, SedexStrategy, PacStrategy, LocalPickupStrategy
from notification_system import event_manager, EmailNotifier, SMSNotifier
from user_management import UserFactory, User

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Chave secreta para sessões

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

# Classe para representar usuários com dados completos
@dataclass
class UserProfile:
    id: int
    email: str
    password: str  # Em produção, seria hash da senha
    first_name: str
    last_name: str
    phone: str
    address: str
    user_type: str  # 'customer' ou 'seller'
    created_at: str
    _user_object: User = None  # Objeto criado pelo Factory Method
    
    def __post_init__(self):
        """Cria o objeto User usando o Factory Method após a inicialização"""
        if self._user_object is None:
            self._user_object = UserFactory.create_user(self.user_type)
    
    def get_permissions(self):
        """Retorna as permissões do usuário usando o Factory Method"""
        if self._user_object is None:
            self._user_object = UserFactory.create_user(self.user_type)
        return self._user_object.get_permissions()
    
    def has_permission(self, permission: str) -> bool:
        """Verifica se o usuário tem uma permissão específica"""
        return permission in self.get_permissions()
    
    def can_manage_products(self) -> bool:
        """Verifica se o usuário pode gerenciar produtos"""
        return self.has_permission("MANAGE_PRODUCTS")
    
    def can_view_sales(self) -> bool:
        """Verifica se o usuário pode ver vendas"""
        return self.has_permission("VIEW_SALES")
    
    def can_manage_coupons(self) -> bool:
        """Verifica se o usuário pode gerenciar cupons"""
        return self.has_permission("MANAGE_COUPONS")

# Lista de vendedores fictícios
SELLERS = ["Casd", "DepCult", "AAAITA"]

# Banco de dados em memória para simulação
# Em uma aplicação real, isso viria de um banco de dados (ex: PostgreSQL, MySQL)
PRODUCTS_DB = {
    # Casd
    1: Product(1, "Camiseta ITA Ondas", 50.00, "Camisa de qualidade com modelo incluso.", "static/images/casd1.png", SELLERS[0], 30),
    2: Product(2, "Moletom Think Outside the ITA", 120.00, "Para se aquecer nesse frio.", "static/images/casd2.png", SELLERS[0], 15),
    3: Product(3, "Camiseta Bruxita", 10.00, "Compra, por favor.", "static/images/casd3.png", SELLERS[0], 100),
    4: Product(4, "Camiseta ITA Engenharias", 40.00, "Camisa de qualidade com modelo não incluso.", "static/images/casd4.png", SELLERS[0], 30),
    5: Product(5, "Camiseta Brasão ITA", 60.00, "Mais uma camiseta do ITA.", "static/images/casd5.png", SELLERS[0], 15),
    6: Product(6, "Garrafa Térmica ITA", 50.00, "Importante se hidratar.", "static/images/casd6.png", SELLERS[0], 20),
    7: Product(7, "Boné ITA", 50.00, "Para esconder a calvície.", "static/images/casd7.png", SELLERS[0], 30),

    # DepCult
    8: Product(8, "Camiseta ITA Jordan", 50.00, "Michael Jordan, não processe, por favor.", "static/images/depcult1.png", SELLERS[1], 25),
    9: Product(9, "Camiseta Just Do ITA", 55.00, "Nike, não processe, por favor.", "static/images/depcult2.png", SELLERS[1], 18),
    10: Product(10, "Camiseta Leis de Maxwell", 70.00, "Bizu para prova de FIS-32.", "static/images/depcult3.png", SELLERS[1], 22),

    # AAAITA
    11: Product(11, "Jaqueta College Azul", 299.90, "Exclusivo para membros da Gurizada.", "static/images/aaaita1.png", SELLERS[2], 16),
    12: Product(12, "Casaco Moletom ITA", 159.90, "Para mostrar na sua cidade que você é do ITA.", "static/images/aaaita2.png", SELLERS[2], 10),
    13: Product(13, "Calça Moletom AAAITA", 129.00, "É uma calça, não tem muito o que falar.", "static/images/aaaita3.png", SELLERS[2], 24),
}

# Arquivos para persistência de dados
USERS_FILE = 'users.json'
ORDERS_FILE = 'orders.json'

# Banco de dados de usuários e pedidos
USERS_DB = {}
ORDERS_DB = {}  # Usaremos para armazenar os pedidos criados

# Sistema de notificação (Observer) configurado automaticamente no notification_system.py

# --- FUNÇÕES DE PERSISTÊNCIA ---

def load_users():
    """Carrega usuários do arquivo JSON"""
    global USERS_DB
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                users_data = json.load(f)
                USERS_DB = {}
                for user_id, user_data in users_data.items():
                    # Remove o campo _user_object se existir (não deve ser serializado)
                    user_data.pop('_user_object', None)
                    user_profile = UserProfile(**user_data)
                    USERS_DB[int(user_id)] = user_profile
        except Exception as e:
            print(f"Erro ao carregar usuários: {e}")
            USERS_DB = {}

def save_users():
    """Salva usuários no arquivo JSON"""
    try:
        users_data = {}
        for user_id, user in USERS_DB.items():
            user_dict = asdict(user)
            # Remove o campo _user_object para não serializar
            user_dict.pop('_user_object', None)
            users_data[str(user_id)] = user_dict
        
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar usuários: {e}")

# Carregar dados ao iniciar
load_users()

# Sistema de pedidos limpo - sem dados de teste
# Os pedidos serão criados apenas quando o usuário fizer compras reais

# --- FUNÇÕES AUXILIARES ---

def get_current_user():
    """Retorna o usuário logado ou None"""
    user_id = session.get('user_id')
    if user_id:
        return USERS_DB.get(user_id)
    return None

def require_login(f):
    """Decorator para proteger rotas que precisam de login"""
    def decorated_function(*args, **kwargs):
        if not get_current_user():
            flash('Você precisa estar logado para acessar esta página.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def require_permission(permission):
    """Decorator para proteger rotas que precisam de permissão específica"""
    def decorator(f):
        def decorated_function(*args, **kwargs):
            current_user = get_current_user()
            if not current_user:
                flash('Você precisa estar logado para acessar esta página.', 'error')
                return redirect(url_for('login'))
            
            if not current_user.has_permission(permission):
                flash('Você não tem permissão para acessar esta página.', 'error')
                return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function
    return decorator

def get_orders_by_seller(seller_name):
    """Retorna pedidos que contêm produtos de um vendedor específico"""
    seller_orders = []
    for order in ORDERS_DB.values():
        for product_name in order.products:
            # Verificar se o produto pertence ao vendedor
            for product in PRODUCTS_DB.values():
                if product.name == product_name and product.seller == seller_name:
                    # Evitar duplicatas
                    if order not in seller_orders:
                        seller_orders.append(order)
                    break
    return seller_orders

def get_user_orders(user_id):
    """Retorna pedidos de um usuário específico (para clientes)"""
    user_orders = []
    for order in ORDERS_DB.values():
        # Verificar se o pedido pertence ao usuário
        if hasattr(order, 'user_id') and order.user_id == user_id:
            user_orders.append(order)
    return user_orders

# --- ROTAS DE AUTENTICAÇÃO ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        user_type = request.form.get('user_type', 'customer')
        
        # Validar tipo de usuário
        if user_type not in ['customer', 'seller']:
            user_type = 'customer'  # Default para customer se inválido
        
        # Validações básicas
        if not all([email, password, first_name, last_name]):
            flash('Email, senha, nome e sobrenome são obrigatórios.', 'error')
            return render_template('register.html')
        
        # Validar email básico
        if '@' not in email or '.' not in email:
            flash('Por favor, insira um email válido.', 'error')
            return render_template('register.html')
        
        # Validar senha mínima
        if len(password) < 4:
            flash('A senha deve ter pelo menos 4 caracteres.', 'error')
            return render_template('register.html')
        
        # Verificar se email já existe
        for user in USERS_DB.values():
            if user.email.lower() == email:
                flash('Este email já está cadastrado.', 'error')
                return render_template('register.html')
        
        # Criar novo usuário
        new_user_id = max(USERS_DB.keys()) + 1 if USERS_DB else 1
        new_user = UserProfile(
            id=new_user_id,
            email=email,
            password=password,  # Para projeto de faculdade, sem hash
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            address=address,
            user_type=user_type,
            created_at=datetime.now().strftime('%d/%m/%Y às %H:%M')
        )
        
        USERS_DB[new_user_id] = new_user
        save_users()  # Salvar no arquivo
        
        # Fazer login automático
        session['user_id'] = new_user_id
        flash(f'Conta criada com sucesso! Bem-vindo(a), {first_name}!', 'success')
        return redirect(url_for('account'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        
        # Validações básicas
        if not email or not password:
            flash('Por favor, preencha email e senha.', 'error')
            return render_template('login.html')
        
        # Buscar usuário pelo email
        user = None
        for u in USERS_DB.values():
            if u.email.lower() == email and u.password == password:
                user = u
                break
        
        if user:
            session['user_id'] = user.id
            # Usar Factory Method para mostrar informações sobre o tipo de usuário
            permissions = user.get_permissions()
            user_type_msg = {
                'customer': 'Cliente',
                'seller': 'Vendedor'
            }.get(user.user_type, 'Usuário')
            
            flash(f'Bem-vindo(a) de volta, {user.first_name}! Você está logado como {user_type_msg}.', 'success')
            return redirect(url_for('account'))
        else:
            flash('Email ou senha incorretos.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('index'))

# --- ROTAS DA APLICAÇÃO WEB ---

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Verificar se o usuário está logado para fazer compras
        current_user = get_current_user()
        if not current_user:
            flash('Você precisa estar logado para fazer uma compra.', 'error')
            return redirect(url_for('login'))
            
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
        
        # Associar pedido ao usuário logado
        new_order.user_id = current_user.id
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
@require_login
def view_order(order_id):
    """Mostra os detalhes de um pedido específico."""
    order = ORDERS_DB.get(order_id)
    if not order:
        abort(404)  # Erro se o pedido não for encontrado
    
    current_user = get_current_user()
    
    # Verificar se o pedido pertence ao usuário logado
    if hasattr(order, 'user_id') and order.user_id != current_user.id:
        flash('Você não tem permissão para ver este pedido.', 'error')
        return redirect(url_for('account'))
    
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
@require_login
def account():
    current_user = get_current_user()
    
    # Usar Factory Method para obter permissões
    permissions = current_user.get_permissions()
    
    if current_user.can_manage_products():
        # Para vendedores, mostrar monitoramento de vendas
        seller_name = f"{current_user.first_name} {current_user.last_name}"
        seller_orders = get_orders_by_seller(seller_name)
        return render_template('seller_dashboard.html', 
                             user=current_user, 
                             orders=seller_orders,
                             permissions=permissions)
    else:
        # Para clientes, mostrar pedidos do usuário
        user_orders = get_user_orders(current_user.id)
        return render_template('account.html', 
                             user=current_user, 
                             orders=user_orders,
                             permissions=permissions)

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

# --- ROTAS PARA VENDEDORES (usando Factory Method) ---

@app.route('/seller/products')
@require_permission('MANAGE_PRODUCTS')
def seller_products():
    """Página para vendedores gerenciarem seus produtos"""
    current_user = get_current_user()
    seller_name = f"{current_user.first_name} {current_user.last_name}"
    
    # Filtrar produtos do vendedor atual
    seller_products = [p for p in PRODUCTS_DB.values() if p.seller == seller_name]
    
    return render_template('seller_products.html',
                         current_user=current_user,
                         products=seller_products,
                         permissions=current_user.get_permissions())

@app.route('/comprar/<int:product_id>', methods=['POST'])
@require_login
def comprar(product_id):
    product = PRODUCTS_DB.get(product_id)
    if not product:
        abort(404)

    current_user = get_current_user()
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
    
    # Associar pedido ao usuário logado
    new_order.user_id = current_user.id
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
    
    # Verificar se é requisição AJAX
    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = request.get_json()
        quantity = int(data.get('quantity', 1))
    else:
        quantity = int(request.form.get('quantity', 1))
    
    add_to_cart(product_id, quantity)
    
    # Retorna JSON para requisições AJAX
    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart_items, cart_total = get_cart_items()
        # Calcular quantidade total de itens (não apenas tipos diferentes)
        total_items = sum(item['quantity'] for item in cart_items)
        return jsonify({
            'success': True,
            'message': f'{product.name} adicionado ao carrinho!',
            'cart_count': total_items,
            'cart_total': cart_total,
            'items_count': len(cart_items)  # Tipos diferentes de produtos
        })
    
    # Redireciona com parâmetro para abrir carrinho (fallback para formulários tradicionais)
    referrer = request.referrer or url_for('index')
    if 'produto' in referrer:  # Se veio da página de produto individual
        return redirect(url_for('product_page', product_id=product_id) + '?added=true')
    else:  # Se veio da página inicial
        return redirect(url_for('index') + '?cart=open')

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
@require_login
def checkout():
    """Finaliza a compra com os itens do carrinho ou compra direta."""
    
    current_user = get_current_user()
    
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
        new_order.user_id = current_user.id  # Associar ao usuário
        ORDERS_DB[new_order.id] = new_order
        
        return redirect(url_for('view_order', order_id=new_order.id))
    
    # Compra normal com carrinho
    cart_items, cart_total = get_cart_items()
    
    if not cart_items:
        flash('Seu carrinho está vazio.', 'error')
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
    new_order.user_id = current_user.id  # Associar ao usuário
    ORDERS_DB[new_order.id] = new_order
    
    # Limpar carrinho após finalizar compra
    clear_cart()
    
    return redirect(url_for('view_order', order_id=new_order.id))

if __name__ == '__main__':
    # Roda o servidor web no modo de desenvolvimento
    app.run(debug=True, port=5001)