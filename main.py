import os
import sys
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Path, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse

from api_service import (
    consultar_municipios_por_uf,
    obter_estados,
    validar_uf,
    get_municipio_info,
)
from file_manager import salvar_em_csv, salvar_em_txt
from schemas import (
    ConsultaMunicipiosResponse,
    EstadoModel,
    MensagemResponse,
    MunicipioModel,
    StatusResponse,
)

# Configuração e Inicialização do FastAPI com documentação Swagger interativa
app = FastAPI(
    title="API de Consulta de Municípios do Brasil",
    description="""
API RESTful para consulta online de municípios brasileiros baseada nos dados do IBGE.

### Recursos disponíveis:
* **Consulta por Estado (UF)**: Obtenha a lista completa de cidades de qualquer estado brasileiro.
* **Filtro por nome**: Pesquise municípios específicos dentro de um estado.
* **Exportação**: Baixe relatórios formatados em **TXT** ou planilhas **CSV** diretamente pelo navegador/Swagger.
* **Documentação Interativa (Swagger)**: Teste todas as consultas diretamente nesta interface sem usar o terminal.
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "Municípios",
            "description": "Endpoints para consulta e filtragem de municípios por estado (UF).",
        },
        {
            "name": "Exportação",
            "description": "Download direto de relatórios em formatos TXT e CSV.",
        },
        {
            "name": "Estados",
            "description": "Consulta às Unidades Federativas do Brasil.",
        },
        {
            "name": "Sistema",
            "description": "Status de integridade e metadados da aplicação.",
        },
    ],
)

# Habilitar CORS para permitir consumo de qualquer origem (web, mobile, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/",
    include_in_schema=False,
    response_class=RedirectResponse,
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
)
def raiz_redirecionar_para_swagger():
    """Redireciona o acesso da raiz diretamente para o Swagger UI (/docs)."""
    return RedirectResponse(url="/docs")


@app.get(
    "/api/v1/status",
    response_model=StatusResponse,
    tags=["Sistema"],
    summary="Verificar status da API",
)
def verificar_status():
    """Retorna o estado operacional da API e os links da documentação interativa."""
    return {
        "status": "online",
        "versao": "2.0.0",
        "documentacao_swagger": "/docs",
        "documentacao_redoc": "/redoc",
    }


@app.get(
    "/api/v1/estados",
    response_model=List[EstadoModel],
    tags=["Estados"],
    summary="Listar todos os estados brasileiros",
)
def listar_estados():
    """Retorna a lista completa das 27 Unidades Federativas do Brasil."""
    return obter_estados()


@app.get(
    "/api/v1/municipios/{uf}",
    response_model=ConsultaMunicipiosResponse,
    tags=["Municípios"],
    summary="Consultar municípios de um estado por UF",
    responses={
        400: {"model": MensagemResponse, "description": "UF com formato inválido"},
        404: {"model": MensagemResponse, "description": "UF não encontrada ou sem dados"},
    },
)
def consultar_municipios(
    uf: str = Path(
        ...,
        description="Sigla da Unidade Federativa com 2 letras (ex: SP, RJ, MG, PR, BA)",
        min_length=2,
        max_length=2,
        examples=["SP"],
    ),
    termo: Optional[str] = Query(
        None,
        description="Filtro opcional para buscar municípios que contenham este termo no nome",
        examples=["Campinas"],
    ),
    salvar_txt: bool = Query(
        False,
        description="Se marcado como True, salva uma cópia do relatório em TXT no servidor",
    ),
    salvar_csv: bool = Query(
        False,
        description="Se marcado como True, salva uma cópia da planilha em CSV no servidor",
    ),
):
    """
    Consulta os municípios do estado informado pela sigla da UF.
    Os dados são obtidos diretamente dos serviços do IBGE (com contingência em cache local).
    """
    uf_normalizada = uf.strip().upper()
    info_estado = validar_uf(uf_normalizada)

    if not info_estado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"UF '{uf_normalizada}' não é válida. Utilize uma sigla oficial (ex: SP, RJ, MG).",
        )

    municipios, origem = consultar_municipios_por_uf(uf_normalizada)

    if not municipios:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nenhum município localizado para o estado '{uf_normalizada}'.",
        )

    # Filtrar por termo caso fornecido
    if termo:
        termo_lower = termo.strip().lower()
        municipios = [m for m in municipios if termo_lower in m.get("nome", "").lower()]

    # Opcional: salvar arquivos em disco se solicitado
    if salvar_txt:
        salvar_em_txt(uf_normalizada, municipios)
    if salvar_csv:
        salvar_em_csv(uf_normalizada, municipios)

    return {
        "uf": uf_normalizada,
        "estado_nome": info_estado["nome"],
        "regiao": info_estado["regiao"],
        "total": len(municipios),
        "origem_dados": origem,
        "municipios": municipios,
    }


@app.get(
    "/api/v1/municipios/{uf}/exportar/txt",
    tags=["Exportação"],
    summary="Baixar relatório formatado em TXT",
    response_class=FileResponse,
    responses={
        200: {
            "description": "Arquivo de texto baixado com sucesso",
            "content": {"text/plain": {}},
        },
        404: {"model": MensagemResponse, "description": "UF não encontrada"},
    },
)
def exportar_txt(
    uf: str = Path(..., min_length=2, max_length=2, description="Sigla da UF (ex: SP)", examples=["SP"]),
):
    """
    Gera dinamicamente e disponibiliza para download direto o arquivo `.txt`
    com a listagem formatada dos municípios da UF.
    """
    uf_normalizada = uf.strip().upper()
    info_estado = validar_uf(uf_normalizada)
    if not info_estado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"UF '{uf_normalizada}' inválida.",
        )

    municipios, _ = consultar_municipios_por_uf(uf_normalizada)
    if not municipios:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nenhum dado encontrado para gerar o arquivo do estado '{uf_normalizada}'.",
        )

    caminho_arquivo = salvar_em_txt(uf_normalizada, municipios)
    nome_download = f"municipios_{uf_normalizada}.txt"

    return FileResponse(
        path=caminho_arquivo,
        media_type="text/plain; charset=utf-8",
        filename=nome_download,
    )


@app.get(
    "/api/v1/municipios/{uf}/exportar/csv",
    tags=["Exportação"],
    summary="Baixar planilha em formato CSV",
    response_class=FileResponse,
    responses={
        200: {
            "description": "Planilha CSV baixada com sucesso",
            "content": {"text/csv": {}},
        },
        404: {"model": MensagemResponse, "description": "UF não encontrada"},
    },
)
def exportar_csv(
    uf: str = Path(..., min_length=2, max_length=2, description="Sigla da UF (ex: SP)", examples=["SP"]),
):
    """
    Gera dinamicamente e disponibiliza para download direto uma planilha `.csv`
    com os municípios, microrregião e mesorregião da UF.
    """
    uf_normalizada = uf.strip().upper()
    info_estado = validar_uf(uf_normalizada)
    if not info_estado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"UF '{uf_normalizada}' inválida.",
        )

    municipios, _ = consultar_municipios_por_uf(uf_normalizada)
    if not municipios:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nenhum dado encontrado para gerar a planilha do estado '{uf_normalizada}'.",
        )

    caminho_arquivo = salvar_em_csv(uf_normalizada, municipios)
    nome_download = f"municipios_{uf_normalizada}.csv"

    return FileResponse(
        path=caminho_arquivo,
        media_type="text/csv; charset=utf-8",
        filename=nome_download,
    )


def executar_modo_terminal():
    """Modo legado para execução interativa diretamente no terminal caso desejado."""
    print("=" * 50)
    print("📍 MODO TERMINAL - CONSULTA DE MUNICÍPIOS IBGE")
    print("=" * 50)
    uf = input("Digite a UF do estado (ex: SP, RJ, MG, PR, BA, etc): ").upper().strip()

    if len(uf) != 2 or not validar_uf(uf):
        print("❌ Por favor, digite uma UF válida com apenas 2 letras.")
        return

    municipios, origem = consultar_municipios_por_uf(uf)

    if not municipios:
        print(f"❌ Nenhum município encontrado para a UF: {uf}.")
        return

    print(f"\n✅ {len(municipios)} Municípios encontrados para o Estado {uf} (Origem: {origem})\n")

    for municipio in municipios[:10]:
        nome = municipio.get("nome")
        microrregiao = municipio.get("microrregiao", "N/A")
        mesorregiao = municipio.get("mesorregiao", "N/A")
        print(
            f"📍 Município: {nome}\n"
            f"   Microrregião: {microrregiao}\n"
            f"   Mesorregião: {mesorregiao}\n"
            f"{'-' * 30}"
        )

    if len(municipios) > 10:
        print(f"... e mais {len(municipios) - 10} municípios.")

    caminho_txt = salvar_em_txt(uf, municipios)
    print(f"\n📄 Relatório completo salvo em: {caminho_txt}\n")


if __name__ == "__main__":
    # Se o usuário passar a flag --cli, executa no terminal; caso contrário, inicia a API com Swagger
    if "--cli" in sys.argv:
        executar_modo_terminal()
    else:
        print("=" * 60)
        print("🚀 Servidor da API iniciado com sucesso!")
        print("📖 Swagger UI disponível em: http://127.0.0.1:8000/docs")
        print("📖 ReDoc disponível em:      http://127.0.0.1:8000/redoc")
        print("🌐 Acesso à API:            http://127.0.0.1:8000/")
        print("=" * 60)
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
