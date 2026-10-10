"""
Paso 5: carga los documentos con variantes de splice anidadas
(data/genes_mongo.json) a la coleccion "genes" de MongoDB.
"""

import json
from pymongo import MongoClient

from config import MONGO_URI, MONGO_DB, DATA_DIR


def cargar_mongo():
    """Carga data/genes_mongo.json en la coleccion 'genes' de Mongo."""
    with open(DATA_DIR / "genes_mongo.json", encoding="utf-8") as f:
        documentos = json.load(f)

    conexion = MongoClient(MONGO_URI)
    db = conexion[MONGO_DB]
    coleccion = db["genes"]

    coleccion.delete_many({})
    coleccion.insert_many(documentos)

    print(f"Listo: {len(documentos)} genes cargados en la coleccion 'genes' de la base '{MONGO_DB}'.")
