# Resumo do Merge Controlado: Main + Pablin

## Objetivo
Integrar apenas as funcionalidades de criação e visualização de perfis da branch `pablin` na branch `main`, mantendo o design e sistema de carrinho originais.

## Funcionalidades Integradas

### 1. Sistema de Autenticação
- **Registro de usuários** (`/register`)
  - Campos: nome, sobrenome, email, senha, telefone, endereço, tipo de conta
  - Validação de campos obrigatórios
  - Verificação de email duplicado
  - Login automático após registro

- **Login de usuários** (`/login`)
  - Autenticação por email e senha
  - Redirecionamento para conta após login

- **Logout** (`/logout`)
  - Limpeza da sessão
  - Redirecionamento para página inicial

### 2. Gerenciamento de Perfis
- **Classe UserProfile**: Estrutura de dados para usuários
- **Persistência**: Armazenamento em arquivo JSON (`users.json`)
- **Sessões**: Controle de usuário logado via Flask session

### 3. Páginas de Perfil
- **Conta do Cliente** (`/account`)
  - Informações pessoais
  - Histórico de pedidos
  - Interface adaptada para clientes

- **Dashboard do Vendedor** (`/seller_dashboard.html`)
  - Estatísticas de vendas
  - Pedidos dos produtos do vendedor
  - Interface específica para vendedores

### 4. Templates Criados/Atualizados
- `login.html`: Página de login com design moderno
- `register.html`: Página de registro com formulário completo
- `account.html`: Perfil do cliente atualizado
- `seller_dashboard.html`: Dashboard específico para vendedores
- `layout.html`: Links de autenticação no cabeçalho

### 5. Estilos CSS
- Adicionados estilos para autenticação e perfis em `static/style.css`
- Design responsivo e moderno
- Cores consistentes com o tema do projeto

## Funcionalidades Mantidas da Main
- ✅ Sistema de carrinho completo
- ✅ Design original com Tailwind CSS
- ✅ Sistema de pedidos e frete
- ✅ Padrões de projeto (Factory, Observer, etc.)
- ✅ Estrutura de produtos e vendedores

## Estrutura de Dados

### UserProfile
```python
@dataclass
class UserProfile:
    id: int
    email: str
    password: str
    first_name: str
    last_name: str
    phone: str
    address: str
    user_type: str  # 'customer' ou 'seller'
    created_at: str
```

### Rotas Adicionadas
- `GET/POST /register` - Registro de usuários
- `GET/POST /login` - Login de usuários
- `GET /logout` - Logout
- `GET /account` - Perfil do usuário (protegida)

## Segurança
- Decorator `@require_login` para proteger rotas
- Validação de dados de entrada
- Sessões seguras com chave secreta
- Verificação de usuário logado

## Como Usar

### Para Clientes
1. Acessar `/register` para criar conta
2. Fazer login em `/login`
3. Acessar `/account` para ver perfil e pedidos
4. Usar o carrinho normalmente

### Para Vendedores
1. Criar conta selecionando "Vendedor" no registro
2. Fazer login
3. Acessar `/account` para ver dashboard de vendas
4. Monitorar pedidos dos produtos

## Arquivos Modificados
- `app.py`: Adicionadas rotas e lógica de autenticação
- `templates/layout.html`: Links de autenticação
- `templates/account.html`: Perfil do cliente
- `templates/login.html`: Página de login
- `templates/register.html`: Página de registro
- `templates/seller_dashboard.html`: Dashboard do vendedor
- `static/style.css`: Estilos para autenticação e perfis

## Arquivos Criados
- `users.json`: Armazenamento de usuários
- `MERGE_SUMMARY.md`: Esta documentação

## Status
✅ **Merge concluído com sucesso**
- Funcionalidades de perfil integradas
- Design original preservado
- Sistema de carrinho mantido
- Aplicação funcionando corretamente 