"""
Paso 6: ejecuta las 6 consultas acordadas sobre la coleccion "genes"
de Mongo, imprimiendo sentencia + resultado de cada una.
"""

from pymongo import MongoClient

from config import MONGO_URI, MONGO_DB


def _mostrar(titulo, sentencia_legible, resultado):
    print(f"\n{titulo}")
    print(f"Sentencia: {sentencia_legible}")
    print(f"Resultado: {resultado}")


def ejecutar_consultas():
    conexion = MongoClient(MONGO_URI)
    db = conexion[MONGO_DB]
    coleccion = db["genes"]

    # a. Listar todos los genes
    filtro_a = {}
    resultado_a = [g["gene_symbol"] for g in coleccion.find(filtro_a, {"gene_symbol": 1, "_id": 0})]
    _mostrar("a. Listar todos los genes", "coleccion.find({})", resultado_a)

    # b. Cantidad de genes con mas de 10 variantes de splice
    filtro_b = {"$expr": {"$gt": [{"$size": "$splice_variants"}, 10]}}
    resultado_b = coleccion.count_documents(filtro_b)
    _mostrar(
        "b. Cantidad de genes con mas de 10 variantes de splice",
        f"coleccion.count_documents({filtro_b})",
        resultado_b,
    )

    # c. Genes del cromosoma 21
    filtro_c = {"chromosome": "21"}
    resultado_c = [g["gene_symbol"] for g in coleccion.find(filtro_c, {"gene_symbol": 1, "_id": 0})]
    _mostrar("c. Genes del cromosoma 21", f"coleccion.find({filtro_c})", resultado_c)

    # d. Cromosomas involucrados en los genes de riesgo de cancer
    resultado_d = sorted(coleccion.distinct("chromosome"), key=lambda c: (len(c), c))
    _mostrar(
        "d. Cromosomas involucrados en los genes de riesgo de cancer",
        "coleccion.distinct('chromosome')",
        resultado_d,
    )

    # e. Numero de genes con ubicacion exclusivamente intracelular
    filtro_e = {"predicted_location": "Intracellular"}
    resultado_e = coleccion.count_documents(filtro_e)
    _mostrar(
        "e. Numero de genes con ubicacion exclusivamente intracelular",
        f"coleccion.count_documents({filtro_e})",
        resultado_e,
    )

    # f. Genes sin variantes de splice
    filtro_f = {"estado": "sin variantes"}
    resultado_f = [g["gene_symbol"] for g in coleccion.find(filtro_f, {"gene_symbol": 1, "_id": 0})]
    _mostrar("f. Genes sin variantes de splice", f"coleccion.find({filtro_f})", resultado_f)
