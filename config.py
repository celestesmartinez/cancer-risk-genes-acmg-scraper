"""
Carga las variables de entorno desde .env y las deja disponibles como
constantes para el resto del proyecto.

Ningun otro archivo del proyecto deberia tener credenciales escritas
directamente -- todos importan estas constantes desde aca.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Carpeta del proyecto (donde esta este mismo archivo), y la carpeta
# de datos dentro de ella. Calcularlo asi -- en vez de escribir una
# ruta fija -- hace que funcione sin importar desde que carpeta se
# ejecute el script.
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "genes_cr_acmg")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB = os.getenv("MONGO_DB", "maestria")
