# Genes ACMG SF — Scraper y persistencia poliglota

Pipeline en Python que captura información de los **28 genes de predisposición a cáncer** incluidos en la lista de hallazgos secundarios del ACMG (**ACMG SF v3.3**) a partir de la web de [Human Protein Atlas](https://www.proteinatlas.org/), y la almacena de forma **poliglota**: datos planos en **MySQL** y documentos con estructura anidada en **MongoDB**.

Trabajo final de la materia *Captura de la Información* — Maestría en Ciencia de Datos, UNAJ.

## ¿Qué hace?

Para cada uno de los 28 genes de la subcategoría "Cancer Risk" de ACMG SF v3.3:

1. Obtiene su Ensembl Gene ID desde la API REST de HGNC.
2. Scrapea su ficha en Human Protein Atlas (HTML) con `requests` + `BeautifulSoup`.
3. Transforma los datos (casteo a `int` / `bool`, campos calculados) y separa la información en dos estructuras: datos planos y variantes de splice anidadas.
4. Carga los datos planos en una tabla de MySQL y los documentos completos en una colección de MongoDB.
5. Ejecuta 6 consultas de ejemplo sobre MongoDB.

## Pipeline

| Paso | Módulo | Qué hace | Salida |
|---|---|---|---|
| 1 | `src/resolver_ids.py` | Consulta la API de HGNC para resolver el Ensembl Gene ID de cada símbolo | `data/genes_ensembl_ids.csv` |
| 2 y 3 | `src/scraper.py`, `src/pipeline.py` | Scrapea la ficha de cada gen, tipa los campos y separa datos planos de variantes de splice | `data/genes_sql.csv`, `data/genes_mongo.json` |
| 4 | `src/carga_sql.py` | Crea la base y la tabla en MySQL y carga los datos planos | Tabla `genes` |
| 5 | `src/carga_mongo.py` | Carga los documentos (campos planos + variantes anidadas) en MongoDB | Colección `genes` |
| 6 | `src/consultas.py` | Ejecuta 6 consultas e imprime sentencia + resultado | Consola |

`main.py` ejecuta los seis pasos en orden.

## Modelo de datos

### MySQL — base `genes_cr_acmg`, tabla `genes`

| Columna | Tipo | Descripción |
|---|---|---|
| `gene_symbol` | VARCHAR(20), **PK** | Símbolo del gen (HGNC) |
| `ensembl_id` | VARCHAR(20) | Ensembl Gene ID |
| `entrez_id` | INT | Entrez Gene ID |
| `synonyms` | VARCHAR(255) | Sinónimos del gen |
| `gene_description` | VARCHAR(255) | Nombre completo del gen |
| `predicted_location` | VARCHAR(100) | Ubicación predicha de la proteína (HPA) |
| `chromosome` | VARCHAR(10) | Cromosoma |
| `cytoband` | VARCHAR(20) | Citobanda |
| `chromosome_location` | VARCHAR(50) | Rango "inicio - fin" en pares de bases |
| `posicion_inicio_bp` | INT | Posición de inicio en el cromosoma (bp) |
| `number_of_transcripts` | INT | Número de transcriptos codificantes de proteína (Ensembl) |
| `estado` | VARCHAR(20) | `"con variantes"` / `"sin variantes"` (calculado) |
| `tiene_multiples_variantes` | BOOLEAN | `True` si el gen tiene más de una variante de splice (calculado) |
| `source_url` | VARCHAR(255) | URL de HPA de la que se extrajo el dato |

### MongoDB — base `maestria`, colección `genes`

Un documento por gen: incluye los mismos campos planos que MySQL y, además, las variantes de splice como un **arreglo de subdocumentos embebidos**. Ejemplo (BRCA1, arreglo abreviado):

```json
{
  "gene_symbol": "BRCA1",
  "ensembl_id": "ENSG00000012048",
  "entrez_id": 672,
  "synonyms": "BRCC1, FANCS, PPP1R53, RNF53",
  "gene_description": "BRCA1 DNA repair associated",
  "predicted_location": "Intracellular",
  "chromosome": "17",
  "cytoband": "q21.31",
  "chromosome_location": "43044295 - 43170245",
  "posicion_inicio_bp": 43044295,
  "number_of_transcripts": 27,
  "estado": "con variantes",
  "tiene_multiples_variantes": true,
  "source_url": "https://www.proteinatlas.org/ENSG00000012048-BRCA1/summary/gene",
  "splice_variants": [
    {
      "variant_id": "BRCA1-201",
      "length_mass": "721 aa 80.6 kDa",
      "signal_peptide": "No",
      "transmembrane_regions": "0"
    },
    {
      "variant_id": "BRCA1-202",
      "length_mass": "1399 aa 156.3 kDa",
      "signal_peptide": "No",
      "transmembrane_regions": "0"
    }
  ]
}
```

La clave de correlación entre ambas bases es `gene_symbol` (y `ensembl_id`), presente en las dos.

## Decisiones de diseño

- **Persistencia poliglota.** Cada gen tiene un conjunto fijo de atributos generales (estructura tabular clásica, ideal para SQL) y un número variable de variantes de splice, cada una con sus propios subcampos (relación uno-a-muchos que en MongoDB se resuelve embebiendo un arreglo, sin tabla adicional ni JOIN).
- **Documentos de Mongo autosuficientes.** El documento incluye también los campos planos, de modo que las consultas pueden ejecutarse sobre la colección sin cruzar con MySQL.
- **Elección de la fuente.** Se evaluaron otras fuentes de variantes y genes. LOVD prohíbe explícitamente el scraping en sus páginas, y las páginas de anotaciones clínicas de PharmGKB que se revisaron cargan su contenido con JavaScript (no accesible con `requests` + `BeautifulSoup`). Human Protein Atlas publica su contenido bajo licencia CC BY-SA 4.0 y entrega el contenido en HTML estático.
- **Credenciales fuera del código.** Usuario, contraseña y cadenas de conexión viven en `.env` (excluido de Git) y se leen desde `config.py`. `.env.example` documenta qué variables hacen falta.

## Detalles de implementación del scraping

- El texto "GENE INFORMATION" aparece dos veces en cada página de HPA (menú lateral y título de tabla). Las tablas se localizan buscando solo entre los encabezados `<th class="head">`.
- Las etiquetas de algunas filas incluyen un texto de ayuda oculto (`display: none`) dentro del mismo `<th>`. Se extrae únicamente el texto visible de la etiqueta.
- Al unir fragmentos de texto se usa un separador explícito (`get_text(" ", strip=True)`) para no perder espacios entre un enlace y el texto que lo acompaña.
- Se espera 1 segundo entre pedidos a HPA.

## Requisitos

- Python 3 (probado con Python 3.14)
- MySQL y MongoDB corriendo en local
- Librerías de `requirements.txt`

## Instalación y uso

```bash
git clone https://github.com/celestesmartinez/cancer-risk-genes-acmg-scraper.git
cd cancer-risk-genes-acmg-scraper

pip install -r requirements.txt

# Crear el archivo .env a partir de la plantilla y completar tus credenciales
copy .env.example .env      # Windows
# cp .env.example .env      # Linux / macOS

python main.py
```

Ejecutar siempre `python main.py` **desde la carpeta raíz** del proyecto.

> **Atención:** el pipeline es repetible. Cada ejecución **elimina y recrea** la tabla `genes` en MySQL y **vacía** la colección `genes` en MongoDB antes de cargar. No lo apuntes a una base cuyos datos quieras conservar.

## Estructura del proyecto

```
genes_acmg_scraper/
├── README.md
├── requirements.txt
├── .gitignore
├── .env.example          (plantilla de variables de entorno)
├── config.py             (carga .env, define rutas y conexiones)
├── main.py               (punto de entrada: corre los 6 pasos)
├── data/                 (CSV/JSON generados por el pipeline)
└── src/
    ├── __init__.py
    ├── resolver_ids.py
    ├── scraper.py
    ├── pipeline.py
    ├── carga_sql.py
    ├── carga_mongo.py
    └── consultas.py
```

## Resultados de las consultas de ejemplo

| | Consulta | Resultado |
|---|---|---|
| a | Listar todos los genes | 28 genes |
| b | Cantidad de genes con más de 10 variantes de splice | 10 |
| c | Genes del cromosoma 21 | Ninguno |
| d | Cromosomas involucrados | 15: 1, 2, 3, 5, 7, 9, 10, 11, 13, 14, 16, 17, 18, 19, 22 |
| e | Genes con ubicación exclusivamente intracelular | 21 |
| f | Genes sin variantes de splice | Ninguno |

## Limitaciones

- Cubre solo los 28 genes de la subcategoría "Cancer Risk", no la lista ACMG SF completa (84 genes).
- El scraping depende de la estructura HTML actual de Human Protein Atlas: si el sitio cambia su maquetación, hay que ajustar `src/scraper.py`.
- Los campos de las variantes de splice (`length_mass`, `signal_peptide`, `transmembrane_regions`) se guardan como texto, tal como los publica HPA; solo los campos de nivel gen se castean a `int` / `bool`.

## Fuentes y atribución

- **Human Protein Atlas** — contenido bajo licencia Creative Commons Attribution-ShareAlike 4.0. Términos de licencia y cita: <https://www.proteinatlas.org/about/licence>
- **HGNC** (HUGO Gene Nomenclature Committee) — API REST usada para resolver identificadores: <https://www.genenames.org/>
- **ACMG SF v3.3** — lista de hallazgos secundarios del American College of Medical Genetics and Genomics. *Genet Med.* 2025;27(8):101454.

## Autora

Celeste Martinez
