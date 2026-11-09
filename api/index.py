import os
import sys

# Adiciona a raiz do projeto ao path do Python
DIRETORIO_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if DIRETORIO_RAIZ not in sys.path:
    sys.path.insert(0, DIRETORIO_RAIZ)

from main import app

# Exporta a instância ASGI para o runtime da Vercel
app = app
