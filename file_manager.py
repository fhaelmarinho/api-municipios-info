import csv
import os
import tempfile
from typing import Any, Dict, List

PASTA_MUNICIPIOS_LOCAL = os.path.join(os.path.dirname(__file__), "Municipios")


def obter_pasta_saida() -> str:
    """
    Retorna o diretório onde os arquivos gerados devem ser salvos.
    Tenta primeiro a pasta 'Municipios' no diretório do projeto; se for somente-leitura
    (como no ambiente Serverless da Vercel / AWS Lambda), utiliza a pasta temporária '/tmp'.
    """
    try:
        os.makedirs(PASTA_MUNICIPIOS_LOCAL, exist_ok=True)
        # Testar permissão de escrita
        teste_path = os.path.join(PASTA_MUNICIPIOS_LOCAL, ".write_test")
        with open(teste_path, "w", encoding="utf-8") as f:
            f.write("test")
        os.remove(teste_path)
        return PASTA_MUNICIPIOS_LOCAL
    except (OSError, PermissionError):
        pasta_tmp = os.path.join(tempfile.gettempdir(), "Municipios")
        os.makedirs(pasta_tmp, exist_ok=True)
        return pasta_tmp


def extrair_dados_municipio(municipio: Dict[str, Any]) -> Dict[str, str]:
    """
    Normaliza a extração dos dados do município independente do formato
    (seja o dicionário cru da API do IBGE ou um dicionário simplificado).
    """
    nome = municipio.get("nome", "N/A")

    # Microrregião
    micro_raw = municipio.get("microrregiao")
    if isinstance(micro_raw, dict):
        microrregiao = micro_raw.get("nome", "N/A")
        meso_raw = micro_raw.get("mesorregiao")
        mesorregiao = meso_raw.get("nome", "N/A") if isinstance(meso_raw, dict) else "N/A"
    elif isinstance(micro_raw, str):
        microrregiao = micro_raw
        mesorregiao = str(municipio.get("mesorregiao", "N/A"))
    else:
        microrregiao = "N/A"
        mesorregiao = "N/A"

    return {
        "nome": nome,
        "microrregiao": microrregiao,
        "mesorregiao": mesorregiao,
    }


def salvar_em_txt(uf: str, municipios: List[Dict[str, Any]]) -> str:
    """
    Gera um relatório formatado em TXT com os municípios da UF informada.
    Retorna o caminho absoluto do arquivo gerado.
    """
    pasta_destino = obter_pasta_saida()
    nome_arquivo = f"municipios_{uf.upper()}.txt"
    caminho_arquivo = os.path.join(pasta_destino, nome_arquivo)

    with open(caminho_arquivo, "w", encoding="utf-8") as arquivo:
        arquivo.write(f"Municípios do Estado {uf.upper()}\n\n")

        for municipio in municipios:
            dados = extrair_dados_municipio(municipio)
            conteudo = (
                f"📍 Município: {dados['nome']}\n"
                f"   Microrregião: {dados['microrregiao']}\n"
                f"   Mesorregião: {dados['mesorregiao']}\n"
                f"{'-' * 30}\n"
            )
            arquivo.write(conteudo)

    return caminho_arquivo


def salvar_em_csv(uf: str, municipios: List[Dict[str, Any]]) -> str:
    """
    Gera uma planilha em CSV com os municípios da UF informada.
    Retorna o caminho absoluto do arquivo gerado.
    """
    pasta_destino = obter_pasta_saida()
    nome_arquivo = f"municipios_{uf.upper()}.csv"
    caminho_arquivo = os.path.join(pasta_destino, nome_arquivo)

    cabecalho = ["Município", "Microrregião", "Mesorregião"]

    with open(caminho_arquivo, "w", encoding="utf-8", newline="") as arquivo:
        escritor_csv = csv.writer(arquivo)
        escritor_csv.writerow(cabecalho)

        for municipio in municipios:
            dados = extrair_dados_municipio(municipio)
            escritor_csv.writerow([
                dados["nome"],
                dados["microrregiao"],
                dados["mesorregiao"],
            ])

    return caminho_arquivo


def ler_municipios_do_txt(uf: str) -> List[Dict[str, Any]]:
    """
    Lê os municípios de um arquivo TXT previamente gerado.
    Procura tanto na pasta do projeto quanto na pasta temporária.
    Útil como fallback caso os serviços externos do IBGE estejam temporariamente indisponíveis.
    """
    nome_arquivo = f"municipios_{uf.upper()}.txt"
    caminho_arquivo = os.path.join(PASTA_MUNICIPIOS_LOCAL, nome_arquivo)

    # Se não estiver no diretório local, verifica se está em /tmp
    if not os.path.exists(caminho_arquivo):
        caminho_tmp = os.path.join(tempfile.gettempdir(), "Municipios", nome_arquivo)
        if os.path.exists(caminho_tmp):
            caminho_arquivo = caminho_tmp
        else:
            return []

    municipios = []
    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        linhas = f.readlines()

    nome_atual = None
    micro_atual = "N/A"
    meso_atual = "N/A"

    for linha in linhas:
        linha_strip = linha.strip()
        if linha_strip.startswith("📍 Município:"):
            nome_atual = linha_strip.replace("📍 Município:", "").strip()
        elif linha_strip.startswith("Microrregião:"):
            micro_atual = linha_strip.replace("Microrregião:", "").strip()
        elif linha_strip.startswith("Mesorregião:"):
            meso_atual = linha_strip.replace("Mesorregião:", "").strip()
        elif linha_strip.startswith("---") and nome_atual:
            municipios.append({
                "id": len(municipios) + 1,
                "nome": nome_atual,
                "microrregiao": micro_atual,
                "mesorregiao": meso_atual,
            })
            nome_atual = None
            micro_atual = "N/A"
            meso_atual = "N/A"

    return municipios
