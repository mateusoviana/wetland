# 🌿 Wetland E-commerce

Bem-vindo ao repositório do projeto Wetland! Uma plataforma de e-commerce inspirada na vasta biodiversidade do Pantanal brasileiro, fazendo uma alusão à diversidade de produtos que oferecemos.

## 📖 Descrição do Projeto

Este projeto é uma plataforma de marketplace digital, acessível e democrática. Inspirada em grandes players como Mercado Livre, OLX e Shopee , a Wetland visa permitir que qualquer pessoa, física ou jurídica, possa vender seus produtos de maneira simples e segura.

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

## 📁 Estrutura do Projeto

Com certeza! Criar um bom README.md é essencial para a colaboração em equipe. Ele serve como o portão de entrada do projeto, garantindo que qualquer pessoa consiga entender, configurar e rodar a aplicação sem dificuldades.

Primeiro, veja como criar o arquivo no PyCharm e, em seguida, o conteúdo completo que você pode copiar e colar.

Como Criar o Arquivo README.md no PyCharm
Na janela de projeto do PyCharm (geralmente à esquerda), clique com o botão direito do mouse na pasta raiz do seu projeto (a pasta ecommerce).
Vá em New -> File.
Digite o nome exato do arquivo: README.md e pressione Enter.
O PyCharm irá criar o arquivo e provavelmente abrirá um editor com duas abas: uma para escrever o texto em Markdown e outra para visualizar como ele ficará.
Agora, copie o conteúdo abaixo e cole no seu arquivo README.md recém-criado.
Conteúdo para o seu README.md
Markdown

# 🌿 Wetland E-commerce

Bem-vindo ao repositório do projeto Wetland! Uma plataforma de e-commerce inspirada na vasta biodiversidade do Pantanal brasileiro, fazendo uma alusão à diversidade de produtos que oferecemos.

## 📖 Descrição do Projeto

[cite_start]Este projeto é uma plataforma de marketplace digital, acessível e democrática[cite: 2]. [cite_start]Inspirada em grandes players como Mercado Livre, OLX e Shopee [cite: 3][cite_start], a Wetland visa permitir que qualquer pessoa, física ou jurídica, possa vender seus produtos de maneira simples e segura.

[cite_start]O sistema está sendo construído com uma arquitetura modular e escalável, utilizando Padrões de Projeto para garantir um código robusto, flexível e de fácil manutenção.

### ✨ Funcionalidades Planejadas

-   [cite_start]Painel público para compradores navegarem, buscarem e adquirirem produtos.
-   [cite_start]Painel do vendedor para cadastro de produtos, acompanhamento de pedidos e configuração de entrega.
-   [cite_start]Suporte a múltiplos métodos de pagamento e envio.
-   [cite_start]Sistema de promoções e cupons.
-   [cite_start]Sistema de notificações para status de pedidos.
-   [cite_start]Recomendações personalizadas de produtos.

## 🏗️ Arquitetura e Padrões de Projeto

[cite_start]A base do projeto utiliza Padrões de Projeto para garantir a reutilização e adaptabilidade do código.

-   [cite_start]**Factory Method**: Usado para gerenciar a criação de diferentes tipos de usuários (`Admin`, `Seller`, `Customer`) e suas permissões.
-   [cite_start]**Builder**: Utilizado para a construção de objetos complexos de Pedido, garantindo sua imutabilidade após a finalização.
-   [cite_start]**State**: Gerencia a lógica do ciclo de vida de um pedido, alterando seu comportamento conforme o status muda (`Pending` → `Paid` → `Shipped` → `Delivered`).
-   [cite_start]**Strategy**: Permite a implementação de diferentes algoritmos para o cálculo de frete, que podem ser trocados dinamicamente.
-   [cite_start]**Observer**: Utilizado para o sistema de notificações, permitindo que diferentes partes do sistema reajam a eventos, como a mudança de status de um pedido.

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

-   Pablo Carvalho do Nascimento dos Santos 
-   Enzo Mitsuo Tokushige Costa 
-   Mateus Oliveira Viana 
-   Paulo Cesar Façanha Silva Filho 
-   Fábio Leonardo Aguiar Rodrigues 