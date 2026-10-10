"""
Punto de entrada unico del proyecto.

Corre el pipeline completo, de punta a punta: resuelve los Ensembl ID,
scrapea los 28 genes, carga MySQL y Mongo, y ejecuta las 6 consultas.

Correr SIEMPRE desde la raiz del proyecto:
    python main.py
"""

from src.resolver_ids import resolver_ensembl_ids
from src.pipeline import escalar_genes
from src.carga_sql import cargar_mysql
from src.carga_mongo import cargar_mongo
from src.consultas import ejecutar_consultas


def main():
    print("=== Paso 1: resolviendo Ensembl ID (HGNC) ===")
    resolver_ensembl_ids()

    print("\n=== Pasos 2 y 3: scrapeando los 28 genes (Human Protein Atlas) ===")
    escalar_genes()

    print("\n=== Paso 4: cargando a MySQL ===")
    cargar_mysql()

    print("\n=== Paso 5: cargando a MongoDB ===")
    cargar_mongo()

    print("\n=== Paso 6: ejecutando las 6 consultas ===")
    ejecutar_consultas()


if __name__ == "__main__":
    main()
