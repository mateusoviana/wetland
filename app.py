from flask import Flask, render_template, request, redirect, url_for, abort, session, flash
from dataclasses import dataclass, asdict
import secrets
import json
import os
from datetime import datetime

# Importa toda a lógica de negócio que já criamos
from order_processing import OrderBuilder
from shipping_calculator import ShippingContext, SedexStrategy
from notification_system import event_manager, EmailNotifier, SMSNotifier
from user_management import UserFactory, Customer, Seller

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

# Lista de vendedores fictícios
SELLERS = ["Loja do Duds", "TechMais", "GamerCenter"]

# Banco de dados em memória para simulação
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

# Arquivos para persistência de dados
USERS_FILE = 'users.json'
ORDERS_FILE = 'orders.json'

# Banco de dados de usuários e pedidos
USERS_DB = {}
ORDERS_DB = {}

# Configurando o sistema de notificação (Observer)
email_notifier = EmailNotifier()
sms_notifier = SMSNotifier()
event_manager.subscribe("order:created", email_notifier)
event_manager.subscribe("order:paid", email_notifier)
event_manager.subscribe("order:paid", sms_notifier)
event_manager.subscribe("order:shipped", email_notifier)

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
                    USERS_DB[int(user_id)] = UserProfile(**user_data)
        except Exception as e:
            print(f"Erro ao carregar usuários: {e}")
            USERS_DB = {}

def save_users():
    """Salva usuários no arquivo JSON"""
    try:
        users_data = {}
        for user_id, user in USERS_DB.items():
            users_data[str(user_id)] = asdict(user)
        
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar usuários: {e}")

def load_orders():
    """Carrega pedidos do arquivo JSON"""
    global ORDERS_DB
    if os.path.exists(ORDERS_FILE):
        try:
            with open(ORDERS_FILE, 'r', encoding='utf-8') as f:
                orders_data = json.load(f)
                # Aqui você precisaria recriar os objetos Order
                # Por simplicidade, vamos manter em memória por enquanto
                ORDERS_DB = {}
        except Exception as e:
            print(f"Erro ao carregar pedidos: {e}")
            ORDERS_DB = {}

def save_orders():
    """Salva pedidos no arquivo JSON"""
    try:
        orders_data = {}
        for order_id, order in ORDERS_DB.items():
            orders_data[str(order_id)] = {
                'id': order.id,
                'products': list(order.products),
                'total_price': order.total_price,
                'status': order.status
            }
        
        with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(orders_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar pedidos: {e}")

# Carregar dados ao iniciar
load_users()
load_orders()

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

def get_orders_by_seller(seller_name):
    """Retorna pedidos que contêm produtos de um vendedor específico"""
    seller_orders = []
    for order in ORDERS_DB.values():
        for product_name in order.products:
            # Verificar se o produto pertence ao vendedor
            for product in PRODUCTS_DB.values():
                if product.name == product_name and product.seller == seller_name:
                    seller_orders.append(order)
                    break
    return seller_orders

# --- ROTAS DE AUTENTICAÇÃO ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        user_type = request.form.get('user_type', 'customer')
        
        # Validações básicas
        if not all([email, password, first_name, last_name]):
            flash('Todos os campos obrigatórios devem ser preenchidos.', 'error')
            return render_template('register.html')
        
        # Verificar se email já existe
        for user in USERS_DB.values():
            if user.email == email:
                flash('Este email já está cadastrado.', 'error')
                return render_template('register.html')
        
        # Criar novo usuário
        new_user_id = max(USERS_DB.keys()) + 1 if USERS_DB else 1
        new_user = UserProfile(
            id=new_user_id,
            email=email,
            password=password,  # Em produção, usar hash
            first_name=first_name,
            last_name=last_name,
            phone=phone or '',
            address=address or '',
            user_type=user_type,
            created_at=datetime.now().strftime('%d/%m/%Y')
        )
        
        USERS_DB[new_user_id] = new_user
        save_users()  # Salvar no arquivo
        
        # Fazer login automático
        session['user_id'] = new_user_id
        flash('Conta criada com sucesso! Bem-vindo ao Wetland!', 'success')
        return redirect(url_for('account'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Buscar usuário pelo email
        user = None
        for u in USERS_DB.values():
            if u.email == email and u.password == password:
                user = u
                break
        
        if user:
            session['user_id'] = user.id
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
        selected_ids = request.form.getlist('product_ids')
        if not selected_ids:
            return redirect(url_for('index'))

        builder = OrderBuilder()
        new_order_id = max(ORDERS_DB.keys()) + 1 if ORDERS_DB else 1
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
        save_orders()  # Salvar no arquivo

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
        max_price=max_price,
        current_user=get_current_user()
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
        save_orders()  # Salvar no arquivo
    return redirect(url_for('view_order', order_id=order_id))

@app.route('/account')
@require_login
def account():
    current_user = get_current_user()
    
    if current_user.user_type == 'seller':
        # Para vendedores, mostrar monitoramento de vendas
        seller_name = f"{current_user.first_name} {current_user.last_name}"
        seller_orders = get_orders_by_seller(seller_name)
        return render_template('seller_dashboard.html', user=current_user, orders=seller_orders)
    else:
        # Para clientes, mostrar pedidos normais
        orders = list(ORDERS_DB.values())
        return render_template('account.html', user=current_user, orders=orders)

@app.route('/produto/<int:product_id>')
def product_page(product_id):
    product = PRODUCTS_DB.get(product_id)
    if not product:
        abort(404)
    return render_template('product.html', product=product)

if __name__ == '__main__':
    # Roda o servidor web no modo de desenvolvimento
    app.run(debug=True, port=5001)