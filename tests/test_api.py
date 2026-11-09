import os
import sys
import unittest
from fastapi.testclient import TestClient

# Adicionar raiz do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app


class TestMunicipiosAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        # Limpar arquivos criados durante os testes
        csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Municipios", "municipios_AC.csv")
        if os.path.exists(csv_path):
            try:
                os.remove(csv_path)
            except OSError:
                pass

    def test_raiz_redireciona_para_swagger(self):
        """Verifica se a rota raiz '/' redireciona para a documentação Swagger '/docs'"""
        response = self.client.get("/", follow_redirects=False)
        self.assertIn(response.status_code, [307, 308, 302, 301])
        self.assertEqual(response.headers["location"], "/docs")

    def test_swagger_docs_acessivel(self):
        """Verifica se a documentação do Swagger UI (/docs) está respondendo 200"""
        response = self.client.get("/docs")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])

    def test_openapi_json(self):
        """Verifica se o esquema OpenAPI está sendo gerado corretamente"""
        response = self.client.get("/openapi.json")
        self.assertEqual(response.status_code, 200)
        dados = response.json()
        self.assertIn("openapi", dados)
        self.assertEqual(dados["info"]["title"], "API de Consulta de Municípios do Brasil")

    def test_status_endpoint(self):
        """Verifica o endpoint de status operacional"""
        response = self.client.get("/api/v1/status")
        self.assertEqual(response.status_code, 200)
        dados = response.json()
        self.assertEqual(dados["status"], "online")
        self.assertEqual(dados["versao"], "2.0.0")

    def test_listar_estados(self):
        """Verifica se a listagem de estados retorna todos os 27 estados da federação"""
        response = self.client.get("/api/v1/estados")
        self.assertEqual(response.status_code, 200)
        estados = response.json()
        self.assertEqual(len(estados), 27)
        siglas = [e["sigla"] for e in estados]
        self.assertIn("SP", siglas)
        self.assertIn("RJ", siglas)
        self.assertIn("MG", siglas)

    def test_consultar_municipios_sp(self):
        """Verifica a consulta dos municípios de SP"""
        response = self.client.get("/api/v1/municipios/SP")
        self.assertEqual(response.status_code, 200)
        dados = response.json()
        self.assertEqual(dados["uf"], "SP")
        self.assertEqual(dados["estado_nome"], "São Paulo")
        self.assertGreater(dados["total"], 0)
        self.assertIsInstance(dados["municipios"], list)

    def test_consultar_municipios_com_filtro(self):
        """Verifica se a filtragem por termo funciona"""
        response = self.client.get("/api/v1/municipios/SP?termo=campinas")
        self.assertEqual(response.status_code, 200)
        dados = response.json()
        self.assertGreater(dados["total"], 0)
        nomes = [m["nome"].lower() for m in dados["municipios"]]
        for nome in nomes:
            self.assertIn("campinas", nome)

    def test_uf_invalida(self):
        """Verifica se o retorno de UF inexistente resulta em erro 404 apropriado"""
        response = self.client.get("/api/v1/municipios/ZZ")
        self.assertEqual(response.status_code, 404)

    def test_exportar_txt(self):
        """Verifica o download direto do relatório em formato TXT"""
        response = self.client.get("/api/v1/municipios/AC/exportar/txt")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/plain", response.headers["content-type"])
        self.assertIn("Acrelândia", response.text)

    def test_exportar_csv(self):
        """Verifica o download direto da planilha em formato CSV"""
        response = self.client.get("/api/v1/municipios/AC/exportar/csv")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/csv", response.headers["content-type"])
        self.assertIn("Município", response.text)
        self.assertIn("Acrelândia", response.text)


if __name__ == "__main__":
    unittest.main()
