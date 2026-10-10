"""
Paso 1: resuelve el Ensembl Gene ID de cada uno de los 28 genes de
riesgo de cancer (ACMG SF v3.3) usando la API REST de HGNC.
"""

import time
import requests
import pandas as pd

from config import DATA_DIR

GENES_RIESGO_CANCER = [
    "APC", "BMPR1A", "BRCA1", "BRCA2", "MAX", "MEN1", "MLH1",
    "MSH2", "MSH6", "MUTYH", "NF2", "PALB2", "PMS2", "PTEN",
    "RB1", "RET", "SDHAF2", "SDHB", "SDHC", "SDHD", "SMAD4",
    "STK11", "TMEM127", "TP53", "TSC1", "TSC2", "VHL", "WT1",
]


def resolver_ensembl_ids():
    """Resuelve los Ensembl ID de GENES_RIESGO_CANCER y guarda el
    resultado en data/genes_ensembl_ids.csv. Devuelve el DataFrame."""
    headers = {"Accept": "application/json"}
    resultados = []

    for simbolo in GENES_RIESGO_CANCER:
        url = f"https://rest.genenames.org/fetch/symbol/{simbolo}"
        respuesta = requests.get(url, headers=headers)
        datos = respuesta.json()
        docs = datos["response"]["docs"]

        if len(docs) > 0:
            ensembl_id = docs[0].get("ensembl_gene_id")
            resultados.append({"gene_symbol": simbolo, "ensembl_id": ensembl_id})
        else:
            print(f"Aviso: no se encontro registro en HGNC para {simbolo}")
            resultados.append({"gene_symbol": simbolo, "ensembl_id": None})

        time.sleep(0.15)

    df_ids = pd.DataFrame(resultados)
    df_ids.to_csv(DATA_DIR / "genes_ensembl_ids.csv", index=False)
    print(f"Listo: {len(df_ids)} genes resueltos -> {DATA_DIR / 'genes_ensembl_ids.csv'}")
    return df_ids
