"""
Paso 4: crea la base genes_cr_acmg en MySQL y carga la tabla genes
con los datos planos generados en el paso 3.
"""

import pandas as pd
from sqlalchemy import create_engine, text

from config import DB_USER, DB_PASSWORD, DB_HOST, DB_NAME, DATA_DIR

DDL_TABLA_GENES = """
CREATE TABLE IF NOT EXISTS genes (
    gene_symbol                VARCHAR(20) PRIMARY KEY,
    ensembl_id                 VARCHAR(20),
    entrez_id                  INT,
    synonyms                   VARCHAR(255),
    gene_description           VARCHAR(255),
    predicted_location         VARCHAR(100),
    chromosome                 VARCHAR(10),
    cytoband                   VARCHAR(20),
    chromosome_location        VARCHAR(50),
    posicion_inicio_bp         INT,
    number_of_transcripts      INT,
    estado                     VARCHAR(20),
    tiene_multiples_variantes  BOOLEAN,
    source_url                 VARCHAR(255)
)
"""


def cargar_mysql():
    """Crea la base y la tabla (recreandola con el esquema actual) y
    carga data/genes_sql.csv en MySQL."""
    motor_servidor = create_engine(f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}")
    with motor_servidor.connect() as conexion:
        conexion.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"))
        conexion.commit()

    motor = create_engine(f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")

    with motor.connect() as conexion:
        conexion.execute(text("DROP TABLE IF EXISTS genes"))
        conexion.execute(text(DDL_TABLA_GENES))
        conexion.commit()

    df_genes = pd.read_csv(DATA_DIR / "genes_sql.csv")
    df_genes.to_sql(name="genes", con=motor, if_exists="append", index=False)

    print(f"Listo: {len(df_genes)} genes cargados en la tabla 'genes' de la base '{DB_NAME}'.")
