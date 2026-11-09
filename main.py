import os
import sys
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Path, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse

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
from web_interface import HTML_INTERFACE

# Configuração e Inicialização do FastAPI com documentação Swagger interativa
app = FastAPI(
    title="API de Consulta de Municípios do Brasil",
    description="""
API RESTful para consulta online de municípios brasileiros baseada nos dados do IBGE.

### Recursos disponíveis:
* **Interface Visual**: Acesse a interface web interativa em [`/app`](/app).
* **Consulta por Estado (UF)**: Obtenha a lista completa de cidades de qualquer estado brasileiro.
* **Filtro por nome**: Pesquise municípios específicos dentro de um estado.
* **Exportação**: Baixe relatórios formatados em **TXT** ou planilhas **CSV** diretamente pelo navegador ou Swagger.
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
            "name": "Interface Web",
            "description": "Interface gráfica para consulta no navegador.",
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


# ==========================================
# Rotas Raiz e Redirecionamentos de Conveniência
# ==========================================

@app.get("/", include_in_schema=False)
@app.get("", include_in_schema=False)
@app.get("/api", include_in_schema=False)
@app.get("/api/", include_in_schema=False)
@app.get("/api/v1", include_in_schema=False)
@app.get("/api/v1/", include_in_schema=False)
@app.get("/api/index.py", include_in_schema=False)
def redirecionar_para_swagger():
    """Redireciona qualquer chamada às rotas raízes para a documentação interativa Swagger (/docs)."""
    return RedirectResponse(url="/docs", status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@app.get("/app", response_class=HTMLResponse, tags=["Interface Web"], summary="Interface web de consulta")
@app.get("/web", response_class=HTMLResponse, include_in_schema=False)
@app.get("/consulta", response_class=HTMLResponse, include_in_schema=False)
def interface_web():
    """Abre o painel visual interativo no navegador para consulta de municípios."""
    return HTMLResponse(content=HTML_INTERFACE, status_code=200)


# Suporte a rotas alternativas para o Swagger no Vercel (/api/docs e /api/redoc)
@app.get("/api/docs", include_in_schema=False)
@app.get("/api/docs/", include_in_schema=False)
def swagger_ui_alternativo():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url or "/openapi.json",
        title=f"{app.title} - Swagger UI",
    )


@app.get("/api/redoc", include_in_schema=False)
@app.get("/api/redoc/", include_in_schema=False)
def redoc_alternativo():
    return get_redoc_html(
        openapi_url=app.openapi_url or "/openapi.json",
        title=f"{app.title} - ReDoc",
    )


# ==========================================
# Endpoints do Sistema
# ==========================================

@app.get(
    "/api/v1/status",
    response_model=StatusResponse,
    tags=["Sistema"],
    summary="Verificar status da API",
)
@app.get("/status", response_model=StatusResponse, include_in_schema=False)
@app.get("/api/status", response_model=StatusResponse, include_in_schema=False)
def verificar_status():
    """Retorna o estado operacional da API e os links da documentação interativa."""
    return {
        "status": "online",
        "versao": "2.0.0",
        "documentacao_swagger": "/docs",
        "documentacao_redoc": "/redoc",
    }


# ==========================================
# Endpoints de Estados
# ==========================================

@app.get(
    "/api/v1/estados",
    response_model=List[EstadoModel],
    tags=["Estados"],
    summary="Listar todos os estados brasileiros",
)
@app.get("/estados", response_model=List[EstadoModel], include_in_schema=False)
@app.get("/api/estados", response_model=List[EstadoModel], include_in_schema=False)
def listar_estados():
    """Retorna a lista completa das 27 Unidades Federativas do Brasil."""
    return obter_estados()


# ==========================================
# Endpoints de Municípios
# ==========================================

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
@app.get("/municipios/{uf}", response_model=ConsultaMunicipiosResponse, include_in_schema=False)
@app.get("/api/municipios/{uf}", response_model=ConsultaMunicipiosResponse, include_in_schema=False)
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


# ==========================================
# Endpoints de Exportação
# ==========================================

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
@app.get("/municipios/{uf}/exportar/txt", include_in_schema=False)
@app.get("/api/municipios/{uf}/exportar/txt", include_in_schema=False)
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
@app.get("/municipios/{uf}/exportar/csv", include_in_schema=False)
@app.get("/api/municipios/{uf}/exportar/csv", include_in_schema=False)
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
    if "--cli" in sys.argv:
        executar_modo_terminal()
    else:
        print("=" * 60)
        print("🚀 Servidor da API iniciado com sucesso!")
        print("📖 Swagger UI disponível em: http://127.0.0.1:8000/docs")
        print("💻 Interface Web em:         http://127.0.0.1:8000/app")
        print("📖 ReDoc disponível em:      http://127.0.0.1:8000/redoc")
        print("🌐 Acesso à API:            http://127.0.0.1:8000/")
        print("=" * 60)
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
