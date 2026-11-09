import logging
from typing import Any, Dict, List, Optional, Tuple
import requests

from file_manager import ler_municipios_do_txt

logger = logging.getLogger(__name__)

# Informações estáticas oficiais das 27 Unidades Federativas do Brasil
ESTADOS_BRASIL: Dict[str, Dict[str, Any]] = {
    "AC": {"id": 12, "sigla": "AC", "nome": "Acre", "regiao": "Norte"},
    "AL": {"id": 27, "sigla": "AL", "nome": "Alagoas", "regiao": "Nordeste"},
    "AP": {"id": 16, "sigla": "AP", "nome": "Amapá", "regiao": "Norte"},
    "AM": {"id": 13, "sigla": "AM", "nome": "Amazonas", "regiao": "Norte"},
    "BA": {"id": 29, "sigla": "BA", "nome": "Bahia", "regiao": "Nordeste"},
    "CE": {"id": 23, "sigla": "CE", "nome": "Ceará", "regiao": "Nordeste"},
    "DF": {"id": 53, "sigla": "DF", "nome": "Distrito Federal", "regiao": "Centro-Oeste"},
    "ES": {"id": 32, "sigla": "ES", "nome": "Espírito Santo", "regiao": "Sudeste"},
    "GO": {"id": 52, "sigla": "GO", "nome": "Goiás", "regiao": "Centro-Oeste"},
    "MA": {"id": 21, "sigla": "MA", "nome": "Maranhão", "regiao": "Nordeste"},
    "MT": {"id": 51, "sigla": "MT", "nome": "Mato Grosso", "regiao": "Centro-Oeste"},
    "MS": {"id": 50, "sigla": "MS", "nome": "Mato Grosso do Sul", "regiao": "Centro-Oeste"},
    "MG": {"id": 31, "sigla": "MG", "nome": "Minas Gerais", "regiao": "Sudeste"},
    "PA": {"id": 15, "sigla": "PA", "nome": "Pará", "regiao": "Norte"},
    "PB": {"id": 25, "sigla": "PB", "nome": "Paraíba", "regiao": "Nordeste"},
    "PR": {"id": 41, "sigla": "PR", "nome": "Paraná", "regiao": "Sul"},
    "PE": {"id": 26, "sigla": "PE", "nome": "Pernambuco", "regiao": "Nordeste"},
    "PI": {"id": 22, "sigla": "PI", "nome": "Piauí", "regiao": "Nordeste"},
    "RJ": {"id": 33, "sigla": "RJ", "nome": "Rio de Janeiro", "regiao": "Sudeste"},
    "RN": {"id": 24, "sigla": "RN", "nome": "Rio Grande do Norte", "regiao": "Nordeste"},
    "RS": {"id": 43, "sigla": "RS", "nome": "Rio Grande do Sul", "regiao": "Sul"},
    "RO": {"id": 11, "sigla": "RO", "nome": "Rondônia", "regiao": "Norte"},
    "RR": {"id": 14, "sigla": "RR", "nome": "Roraima", "regiao": "Norte"},
    "SC": {"id": 42, "sigla": "SC", "nome": "Santa Catarina", "regiao": "Sul"},
    "SP": {"id": 35, "sigla": "SP", "nome": "São Paulo", "regiao": "Sudeste"},
    "SE": {"id": 28, "sigla": "SE", "nome": "Sergipe", "regiao": "Nordeste"},
    "TO": {"id": 17, "sigla": "TO", "nome": "Tocantins", "regiao": "Norte"},
}


def obter_estados() -> List[Dict[str, Any]]:
    """Retorna a lista de todos os estados brasileiros ordenados por nome."""
    return sorted(list(ESTADOS_BRASIL.values()), key=lambda e: e["nome"])


def validar_uf(uf: str) -> Optional[Dict[str, Any]]:
    """Valida se a UF fornecida pertence ao Brasil. Retorna os dados do estado ou None."""
    return ESTADOS_BRASIL.get(uf.strip().upper())


def normalizar_municipio(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normaliza a estrutura dos dados do município vinda do IBGE ou do cache local
    para um formato padronizado.
    """
    nome = item.get("nome", "N/A")
    id_ibge = item.get("id")

    micro_dict = item.get("microrregiao")
    if isinstance(micro_dict, dict):
        microrregiao = micro_dict.get("nome", "N/A")
        meso_dict = micro_dict.get("mesorregiao")
        mesorregiao = meso_dict.get("nome", "N/A") if isinstance(meso_dict, dict) else "N/A"
    else:
        microrregiao = str(micro_dict) if micro_dict is not None else "N/A"
        mesorregiao = str(item.get("mesorregiao", "N/A"))

    # Regiões imediatas e intermediárias (se disponíveis no IBGE)
    regiao_imediata = None
    regiao_intermediaria = None
    imediata_dict = item.get("regiao-imediata")
    if isinstance(imediata_dict, dict):
        regiao_imediata = imediata_dict.get("nome")
        intermediaria_dict = imediata_dict.get("regiao-intermediaria")
        if isinstance(intermediaria_dict, dict):
            regiao_intermediaria = intermediaria_dict.get("nome")

    return {
        "id": id_ibge,
        "nome": nome,
        "microrregiao": microrregiao,
        "mesorregiao": mesorregiao,
        "regiao_imediata": regiao_imediata,
        "regiao_intermediaria": regiao_intermediaria,
    }


def consultar_municipios_por_uf(estado_uf: str) -> Tuple[List[Dict[str, Any]], str]:
    """
    Consulta os municípios de uma determinada UF diretamente na API do IBGE.
    Em caso de falha de conexão com a API externa, utiliza o cache local pré-gerado como contingência.
    Retorna uma tupla: (lista_municipios_normalizados, origem_dados).
    """
    uf_upper = estado_uf.strip().upper()
    url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf_upper}/municipios?orderBy=nome"
    headers = {
        "User-Agent": "MunicipiosInfoAPI/2.0 (FastAPI-Swagger; +https://servicodados.ibge.gov.br)",
        "Accept": "application/json",
    }

    try:
        response = requests.get(url, headers=headers, timeout=8)
        response.raise_for_status()
        dados_ibge = response.json()
        if isinstance(dados_ibge, list) and len(dados_ibge) > 0:
            municipios = [normalizar_municipio(m) for m in dados_ibge]
            return municipios, "API IBGE"
    except Exception as e:
        logger.warning("Falha ao consultar API online do IBGE (%s). Acionando cache de contingência...", e)

    # Fallback: Tenta obter os dados já existentes em disco
    dados_locais = ler_municipios_do_txt(uf_upper)
    if dados_locais:
        return dados_locais, "Cache Local (Contingência)"

    return [], "Nenhum dado encontrado"


def get_municipio_info(estado_uf: str) -> List[Dict[str, Any]]:
    """
    Função de compatibilidade mantida para chamadas legadas.
    Retorna a lista de municípios da UF informada.
    """
    municipios, _ = consultar_municipios_por_uf(estado_uf)
    return municipios
