# 📍 Consulta de Municípios IBGE

Este projeto é uma ferramenta em Python para consultar municípios brasileiros através da API de Localidades do IBGE. Ele permite visualizar os dados no terminal e gera automaticamente um relatório em arquivo `.txt`.

## 🚀 Funcionalidades

- Consulta municípios por UF.
- Exibe o nome da cidade, Microrregião e Mesorregião.
- Gera um arquivo de texto (`municipios_UF.txt`) com a lista completa.
- Código modularizado para fácil manutenção.

## 📁 Estrutura do Projeto

- `main.py`: Ponto de entrada do programa e interface com o usuário.
- `api_service.py`: Gerencia as requisições HTTP para a API do IBGE.
- `file_manager.py`: Responsável pela criação e escrita dos arquivos de saída.

## 🛠️ Pré-requisitos

Você precisará da biblioteca `requests` instalada:

```bash
pip install requests
```

## 📖 Como usar

-  Clone ou baixe este repositório.
-  No terminal, navegue até a pasta do projeto.
-  Execute o comando:

```bash
python main.py
```

-  Digite a sigla do estado desejado (ex: SP, MG, RJ, PR, BA, etc).

## 🔗 APIs Utilizadas

IBGE API de Localidades [https://servicodados.ibge.gov.br/api/docs/localidades]

## ⚖️ Licença

Este projeto está sob a licença MIT.