import requests

def get_municipio_info(estado_uf):

    url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{estado_uf}/municipios?orderBy=nome"
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status() # Lança um erro para status codes 4xx ou 5xx
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao consultar API do IBGE: {e}")
        return []