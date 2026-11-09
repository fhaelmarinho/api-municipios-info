from typing import List, Optional
from pydantic import BaseModel, Field


class MunicipioModel(BaseModel):
    id: Optional[int] = Field(None, description="Código IBGE do município", example=3550308)
    nome: str = Field(..., description="Nome do município", example="São Paulo")
    microrregiao: Optional[str] = Field("N/A", description="Nome da microrregião", example="São Paulo")
    mesorregiao: Optional[str] = Field("N/A", description="Nome da mesorregião", example="Metropolitana de São Paulo")
    regiao_imediata: Optional[str] = Field(None, description="Região Geográfica Imediata", example="São Paulo")
    regiao_intermediaria: Optional[str] = Field(None, description="Região Geográfica Intermediária", example="São Paulo")


class EstadoModel(BaseModel):
    id: int = Field(..., description="Código IBGE do estado", example=35)
    sigla: str = Field(..., description="Sigla da UF com 2 letras", example="SP")
    nome: str = Field(..., description="Nome do estado", example="São Paulo")
    regiao: str = Field(..., description="Região do Brasil", example="Sudeste")


class ConsultaMunicipiosResponse(BaseModel):
    uf: str = Field(..., description="Sigla da Unidade Federativa pesquisada", example="SP")
    estado_nome: str = Field(..., description="Nome completo do estado", example="São Paulo")
    regiao: str = Field(..., description="Região do Brasil", example="Sudeste")
    total: int = Field(..., description="Quantidade total de municípios retornados", example=645)
    origem_dados: str = Field(..., description="Origem dos dados (API IBGE ou Cache Local)", example="API IBGE")
    municipios: List[MunicipioModel] = Field(..., description="Lista de municípios")


class MensagemResponse(BaseModel):
    mensagem: str = Field(..., description="Mensagem informativa", example="Operação realizada com sucesso")
    detalhes: Optional[str] = Field(None, description="Detalhes adicionais")


class StatusResponse(BaseModel):
    status: str = Field(..., example="online")
    versao: str = Field(..., example="2.0.0")
    documentacao_swagger: str = Field(..., example="/docs")
    documentacao_redoc: str = Field(..., example="/redoc")
