"""
Paso 3: escala el scraping de un gen (scraper.py) a los 28 genes de
riesgo de cancer, usando los Ensembl ID resueltos en el paso 1.
"""

import time
import json
import pandas as pd

from config import DATA_DIR
from src.scraper import scrapear_gen


def escalar_genes():
    """Scrapea los 28 genes y guarda data/genes_sql.csv y
    data/genes_mongo.json. Devuelve (df_sql, documentos_mongo)."""
    df_ids = pd.read_csv(DATA_DIR / "genes_ensembl_ids.csv")

    filas_sql = []
    documentos_mongo = []

    for _, fila in df_ids.iterrows():
        simbolo = fila["gene_symbol"]
        ensembl_id = fila["ensembl_id"]

        if pd.isna(ensembl_id):
            print(f"Aviso: {simbolo} no tiene Ensembl ID, se omite")
            continue

        try:
            datos_planos, variantes = scrapear_gen(simbolo, ensembl_id)
        except Exception as error:
            print(f"Aviso: fallo al scrapear {simbolo}: {error}")
            continue

        filas_sql.append(datos_planos)

        # El documento de Mongo incluye tambien los campos planos
        # (no solo las variantes), para que la coleccion sea
        # autosuficiente para las 6 consultas del paso 6
        documento_mongo = dict(datos_planos)
        documento_mongo["splice_variants"] = variantes
        documentos_mongo.append(documento_mongo)

        print(f"OK: {simbolo} ({len(variantes)} variantes de splice)")
        time.sleep(1)

    df_sql = pd.DataFrame(filas_sql)
    df_sql.to_csv(DATA_DIR / "genes_sql.csv", index=False)

    with open(DATA_DIR / "genes_mongo.json", "w", encoding="utf-8") as f:
        json.dump(documentos_mongo, f, indent=2, ensure_ascii=False)

    print(f"\nListo: {len(filas_sql)} de {len(df_ids)} genes procesados correctamente.")
    return df_sql, documentos_mongo
