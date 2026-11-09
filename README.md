# 📍 API de Consulta de Municípios do Brasil (IBGE)

API RESTful desenvolvida em Python com **FastAPI** e documentação interativa **Swagger (OpenAPI)** para consulta online de municípios brasileiros através da API de Localidades do IBGE.

A ferramenta foi atualizada para rodar como um servidor web com interface gráfica interativa no navegador, **eliminando a dependência do uso do terminal** para realizar consultas, além de permitir o download direto de relatórios em **TXT** e planilhas em **CSV**.

---

## 🚀 Principais Novidades & Funcionalidades

- **Interface Swagger UI Interativa**: Consulte dados diretamente pelo navegador em `http://localhost:8000/docs`.
- **Independência de Terminal**: Qualquer usuário pode consultar, filtrar e baixar dados via navegador ou integração HTTP.
- **Consulta por UF**: Busca completa de municípios pelo código de 2 letras do estado (ex: `SP`, `RJ`, `MG`, `BA`).
- **Filtro por Nome de Município**: Permite pesquisar cidades específicas dentro de um estado.
- **Exportação Direta**: Download instantâneo de arquivos `.txt` formatados e `.csv` direto pelo Swagger ou URL.
- **Listagem de Estados**: Endpoint com todas as 27 Unidades Federativas do Brasil (sigla, nome, região e código IBGE).
- **Contingência Automática (Cache Local)**: Se os servidores do IBGE apresentarem instabilidade ou conexão lenta, a API aciona automaticamente os dados locais de contingência.
- **Compatibilidade Terminal**: Modo CLI legado ainda disponível com `python main.py --cli`.

---

## 📁 Estrutura do Projeto

```text
api-municipios-info/
├── Municipios/             # Armazenamento de arquivos gerados (.txt e .csv)
├── tests/
│   └── test_api.py         # Testes automatizados da API
├── api_service.py          # Consulta ao IBGE, contingência e dados de estados
├── file_manager.py         # Leitura, escrita e exportação de TXT e CSV
├── schemas.py              # Modelos Pydantic para validação e documentação OpenAPI
├── main.py                 # Aplicação FastAPI, rotas HTTP e inicialização
├── requirements.txt        # Dependências do projeto
└── README.md               # Documentação completa
```

---

## 🛠️ Pré-requisitos e Instalação

1. Clone ou acesse a pasta do repositório:
```bash
cd api-municipios-info
```

2. Crie e ative um ambiente virtual (recomendado):
```bash
python3 -m venv venv
source venv/bin/activate  # No Linux/macOS
# ou no Windows:
# venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

---

## 🌐 Como Executar e Consultar Online

### 1. Iniciar o Servidor Web

Execute o comando:
```bash
python main.py
```
*Ou usando o uvicorn diretamente:*
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Acessar a Consulta Online (Swagger UI)

Abra o seu navegador web e acesse:
👉 **[http://localhost:8000/docs](http://localhost:8000/docs)**

*(O acesso à raiz `http://localhost:8000/` também redireciona automaticamente para o Swagger).*

Também está disponível a documentação alternativa ReDoc em:
👉 **[http://localhost:8000/redoc](http://localhost:8000/redoc)**

---

## 📖 Como Usar o Swagger sem Terminal

1. Acesse **[http://localhost:8000/docs](http://localhost:8000/docs)** no seu navegador.
2. Na seção **Municípios**, clique no endpoint `GET /api/v1/municipios/{uf}`.
3. Clique no botão **Try it out** no canto superior direito do bloco.
4. Digite a sigla da UF desejada (exemplo: `SP`, `RJ`, `MG`, `PR`).
5. (Opcional) Digite um termo de busca no campo `termo` (ex: `Campinas`).
6. Clique no botão azul **Execute**.
7. O resultado será exibido em JSON na mesma tela com todos os municípios, microrregiões e mesorregiões.

### Baixando Arquivos pelo Navegador:
- **Download do TXT**: Clique em `GET /api/v1/municipios/{uf}/exportar/txt` ➔ informe a UF ➔ clique em **Execute** ➔ clique em **Download file**.
- **Download do CSV**: Clique em `GET /api/v1/municipios/{uf}/exportar/csv` ➔ informe a UF ➔ clique em **Execute** ➔ clique em **Download file**.

---

## 🔌 Endpoints da API

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/` | Redireciona automaticamente para a documentação Swagger (`/docs`) |
| `GET` | `/docs` | Interface gráfica interativa Swagger UI |
| `GET` | `/redoc` | Documentação técnica ReDoc |
| `GET` | `/api/v1/status` | Verifica a saúde e versão da API |
| `GET` | `/api/v1/estados` | Lista todas as 27 Unidades Federativas do Brasil |
| `GET` | `/api/v1/municipios/{uf}` | Retorna a lista de municípios da UF (com suporte a filtro por termo) |
| `GET` | `/api/v1/municipios/{uf}/exportar/txt` | Faz o download direto do relatório em formato TXT |
| `GET` | `/api/v1/municipios/{uf}/exportar/csv` | Faz o download direto da planilha em formato CSV |

---

## ☁️ Como Fazer Deploy e Rodar na Vercel

O projeto já conta com [`vercel.json`](file:///home/fhael/Documentos/Workspace/api-municipios-info/vercel.json) e o ponto de entrada serverless [`api/index.py`](file:///home/fhael/Documentos/Workspace/api-municipios-info/api/index.py) pré-configurados.

### Opção 1: Via GitHub (Recomendado)

1. Envie as alterações para o seu repositório no GitHub:
   ```bash
   git add .
   git commit -m "feat: suporte para Swagger e deploy na Vercel"
   git push origin main
   ```
2. Acesse o painel da **[Vercel](https://vercel.com)** e faça login.
3. Clique em **"Add New..."** ➔ **"Project"**.
4. Conecte sua conta do GitHub e selecione o repositório **`api-municipios-info`**.
5. Não é necessário alterar nenhuma variável ou comando (a Vercel detecta automaticamente o Python e o `requirements.txt`).
6. Clique no botão **"Deploy"**.
7. Ao término do deploy, clique na URL gerada pela Vercel (ex: `https://seu-projeto.vercel.app/docs`) e o Swagger UI estará disponível publicamente online na nuvem!

### Opção 2: Pelo Terminal via Vercel CLI

1. Instale o Vercel CLI globalmente (caso ainda não tenha):
   ```bash
   npm install -g vercel
   ```
2. Na pasta do projeto, faça login:
   ```bash
   vercel login
   ```
3. Execute o deploy:
   ```bash
   vercel
   ```
4. Para publicar em produção:
   ```bash
   vercel --prod
   ```

---

## 🐳 Como Rodar com Docker

Se preferir rodar em contêiner localmente ou em outra nuvem:

```bash
docker compose up -d
```
Acesse `http://localhost:8000/docs`.

---

## 🧪 Executando os Testes Automatizados

Para rodar os testes unitários da aplicação:

```bash
python -m unittest tests/test_api.py
```

---

## 🖥️ Modo Terminal (Opcional)

Se em algum momento você ainda quiser rodar a versão interativa de terminal, utilize:

```bash
python main.py --cli
```

---

## 🔗 Fontes de Dados

- **IBGE - API de Localidades**: [https://servicodados.ibge.gov.br/api/docs/localidades](https://servicodados.ibge.gov.br/api/docs/localidades)

## ⚖️ Licença

Este projeto está sob a licença MIT.
