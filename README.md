# 🌿 Wetland E-commerce

Bem-vindo ao repositório do projeto Wetland! Uma plataforma de e-commerce inspirada na vasta biodiversidade do Pantanal brasileiro, fazendo uma alusão à diversidade de produtos que oferecemos.

## 📖 Descrição do Projeto

Este projeto é uma plataforma de marketplace digital, acessível e democrática. Inspirada em grandes players como Mercado Livre, OLX e Shopee, a Wetland visa permitir que qualquer pessoa, física ou jurídica, possa vender seus produtos de maneira simples e segura.

O sistema está sendo construído com uma arquitetura modular e escalável, utilizando Padrões de Projeto para garantir um código robusto, flexível e de fácil manutenção.

### ✨ Funcionalidades Planejadas

-   Painel público para compradores navegarem, buscarem e adquirirem produtos.
-   Painel do vendedor para cadastro de produtos, acompanhamento de pedidos e configuração de entrega.
-   Suporte a múltiplos métodos de pagamento e envio.
-   Sistema de promoções e cupons.
-   Sistema de notificações para status de pedidos.
-   Recomendações personalizadas de produtos.

## 🏗️ Arquitetura e Padrões de Projeto

A base do projeto utiliza Padrões de Projeto para garantir a reutilização e adaptabilidade do código.

-   **Factory Method**: Usado para gerenciar a criação de diferentes tipos de usuários (`Admin`, `Seller`, `Customer`) e suas permissões.
-   **Builder**: Utilizado para a construção de objetos complexos de Pedido, garantindo sua imutabilidade após a finalização.
-   **State**: Gerencia a lógica do ciclo de vida de um pedido, alterando seu comportamento conforme o status muda (`Pending` → `Paid` → `Shipped` → `Delivered`).
-   **Strategy**: Permite a implementação de diferentes algoritmos para o cálculo de frete, que podem ser trocados dinamicamente.
-   **Observer**: Utilizado para o sistema de notificações, permitindo que diferentes partes do sistema reajam a eventos, como a mudança de status de um pedido.

## 🔧 Tecnologias Utilizadas

-   **Backend**: Python
-   **Framework Web**: Flask
-   **Frontend**: HTML5, CSS3

## 🚀 Como Configurar o Ambiente

Siga os passos abaixo para configurar e rodar o projeto em sua máquina local.

### Pré-requisitos

-   Python 3.8 ou superior
-   Pip (gerenciador de pacotes do Python)

### Passos para Instalação

1.  **Clone o repositório:**
    ```bash
    git clone <URL_DO_SEU_REPOSITORIO>
    cd ecommerce
    ```

2.  **Crie e ative um ambiente virtual:**
    Um ambiente virtual (venv) isola as dependências do seu projeto.

    * No **macOS/Linux**:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

    * No **Windows**:
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```

3.  **Crie o arquivo de dependências:**
    Crie um arquivo chamado `requirements.txt` na raiz do projeto e adicione a seguinte linha:
    ```
    Flask
    ```

4.  **Instale as dependências:**
    Com o ambiente virtual ativado, execute o comando abaixo para instalar o Flask e outras futuras dependências.
    ```bash
    pip install -r requirements.txt
    ```

## ▶️ Como Executar a Aplicação

1.  Certifique-se de que seu ambiente virtual está ativado.
2.  Execute o servidor web com o seguinte comando:
    ```bash
    python app.py
    ```
3.  Abra seu navegador e acesse: [http://127.0.0.1:5001](http://127.0.0.1:5001)

## 👥 Autores

Este projeto foi concebido e estruturado por:

-   Enzo Mitsuo Tokushige Costa 
-   Fábio Leonardo Aguiar Rodrigues 
-   Mateus Oliveira Viana 
-   Pablo Carvalho do Nascimento dos Santos 
-   Paulo Cesar Façanha Silva Filho
