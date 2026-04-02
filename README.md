# BuscaMed - Dashboard Analítico (Frontend)

Bem-vindo ao repositório do Dashboard do BuscaMed. Esta aplicação é construída em Python utilizando o framework Streamlit e atua como a interface de avaliação e analytics do sistema, consumindo os endpoints do nosso serviço backend em Ktor.

## 🛠️ Configuração do Ambiente Local
Para rodar o projeto localmente, é necessário configurar o ambiente Python, as variáveis de ambiente e a autenticação com o Google Cloud.

**1. Clonando e Preparando o Repositório**
Após clonar o repositório, crie um ambiente virtual Python para isolar as dependências do projeto.

Exemplo prático no terminal:

```bash
# Criação do ambiente virtual
python -m venv venv

# Ativação do ambiente (Windows)
venv\Scripts\activate
# Ativação do ambiente (Linux/Mac)
source venv/bin/activate

# Instalação das dependências
pip install -r requirements.txt
```

**2. Configuração do Arquivo .env**
Atenção: O arquivo .env não é versionado por questões de segurança. Imediatamente após clonar o repositório, você deve criar um arquivo chamado .env na raiz do projeto. Sem ele, a aplicação Streamlit não conseguirá inicializar ou se comunicar com o backend Ktor.

Crie o arquivo .env com a seguinte estrutura de exemplo (ajuste os IPs/URLs conforme seu ambiente local):

```
API_BASE_URL=http://192.168.0.41:8080
OIDC_AUDIENCE=http://192.168.0.41:8080
APP_ENV=local
IMPERSONATE_SERVICE_ACCOUNT=conta_de_servico_de_testes
```
Substitua conta_de_servico_de_testes pelo valor correto que você pode obter acessando o GCP na área de contas de serviço.

## 🔐 Autenticação com o Backend (Google Cloud CLI)

A comunicação entre este Dashboard em Python e o serviço Ktor exige um Token OIDC (Google Service-to-Service). Como o sistema roda sobre a infraestrutura do GCP, utilizamos o gcloud para gerar as credenciais locais que a aplicação Python injetará nas requisições automaticamente.

1. Baixe e instale o [Google Cloud CLI](https://cloud.google.com/sdk/docs/install?hl=pt-br#windows).
2. Autentique sua conta do Google no terminal:
```bash
gcloud init
```
3. Configure as credenciais padrão de aplicação (ADC). A camada de rede do projeto Python interceptará as requisições para anexar o token Bearer gerado a partir desta credencial antes de enviá-las ao Ktor:
```bash
gcloud auth application-default login
```
Uma janela do navegador se abrirá para confirmar o acesso.

**Rodando a Aplicação**
Com o .env e o ADC do Google configurados, inicie a aplicação Streamlit executando:

```bash
streamlit run src/main.py
```

## 🏗️ Arquitetura do Projeto

O projeto segue a Clean Architecture, dividindo a responsabilidade do código para que as telas do Streamlit não conheçam regras de negócio complexas nem como a comunicação HTTP funciona por baixo dos panos. Isso garante que a aplicação seja fácil de manter e escalar.

**presentation** (Camada de Apresentação)

Responsável exclusivamente pela interface visual e interação com o usuário.

**pages / components:** Arquivos Streamlit puros que desenham os gráficos (ex: analytics_charts.py) e telas (ex: prescriptions_page.py).

**view_models:** Fazem a ponte entre a UI e a camada de domínio, gerenciando o estado da tela.

**Regra:** Nenhuma chamada HTTP ou regra de avaliação deve acontecer aqui. A tela apenas chama o ViewModel, que por sua vez aciona um Use Case.

**domain** (Camada de Domínio)

O coração da aplicação. Define as regras de negócio de analytics e estruturação das entidades.

**use_cases:** Contém a lógica central. Exemplo Prático: calculate_prescription_accuracy_use_case.py. Ele sabe como calcular a precisão de uma avaliação de receita, mas não sabe se os dados vieram de um arquivo, de uma API externa ou de um banco local.

**entities / ports:** Estruturas de dados limpas e interfaces que as outras camadas devem implementar.

**data** (Camada de Dados / Infraestrutura)

Lida com o mundo externo (APIs, leitura de arquivos e persistência local).

**remote:** Onde ocorre a comunicação HTTP. O http_client.py e o auth_interceptor.py são responsáveis por interceptar as requisições para anexar o Token OIDC gerado pelo gcloud antes de chamar o Ktor.

**local / queries:** Manipulação de bancos de dados locais (gerenciamento de estado, execuções offline e sincronismos de logs) e migrações (arquivos .sql).

**Regra:** Converte os JSONs que vêm da API do Ktor ou do banco de dados local para entidades puras do domain.

**di** (Camada de Injeção de Dependências)

Contém o container.py, responsável por amarrar todas as camadas: instanciar e injetar os repositórios corretos nos Use Cases, e os Use Cases nos ViewModels.

## 🛠️ Como realizar Incrementos e Correções

Para manter a consistência do código, siga este fluxo ao adicionar uma nova funcionalidade (por exemplo, exibir um novo gráfico de análise de métricas de cartelas de comprimidos):

1. Domain: Comece pelo Domínio. Crie o Caso de Uso, como get_nova_metrica_use_case.py. Defina a interface (Port) de que ele precisará para buscar os dados.
2. Data: Vá para a camada de Dados e implemente a interface definida no passo anterior (ex: no remote_datasource.py), buscando os dados do endpoint correspondente no Ktor. Garanta que o JSON retornado seja convertido para a Entidade do Domínio.
3. DI: Adicione a nova dependência no container.py para que a aplicação saiba como criá-la.
4. Presentation: Por fim, crie ou atualize o ViewModel para chamar o novo Use Case e atualize um componente no Streamlit dentro do diretório components/ ou pages/ para desenhar o gráfico na interface.
