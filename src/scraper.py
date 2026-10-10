"""
Paso 2: scrapea la pagina de un gen en Human Protein Atlas y separa
la informacion en dos partes, siguiendo el diseno poliglota:

- datos_planos: para la tabla SQL "genes" (info general + gene info,
  mas los campos calculados: entrez_id, posicion_inicio_bp,
  number_of_transcripts, estado, tiene_multiples_variantes)
- variantes_splice: para el documento de Mongo (lista anidada)

Logica sin cambios respecto a la version original -- ya fue probada
contra el HTML real de BRCA1 y APC. Este archivo solo reubica las
funciones dentro del paquete src/.
"""

import requests
from bs4 import BeautifulSoup


def encontrar_tabla_por_titulo(soup, titulo):
    """Busca la tabla cuyo encabezado <th class="head"> contiene el
    texto indicado. Restringido a class="head" para no confundirse
    con el mismo texto en el menu lateral de la pagina."""
    for th in soup.find_all("th", class_="head"):
        if titulo in th.get_text():
            return th.find_parent("table")
    return None


def texto_visible_th(th):
    """Extrae solo la etiqueta visible de un <th>, ignorando el texto
    de ayuda oculto que HPA mete en un <div style="display:none">
    dentro del mismo <th>."""
    span = th.find("span", class_="hastip")
    if span:
        return next(span.stripped_strings)
    return th.get_text(strip=True)


def extraer_campo(tabla, etiqueta_buscada):
    """Busca, dentro de una tabla tipo 'etiqueta: valor', el <td>
    correspondiente a la etiqueta pedida."""
    for fila in tabla.find_all("tr"):
        th = fila.find("th")
        td = fila.find("td")
        if th and td:
            etiqueta = texto_visible_th(th)
            if etiqueta.strip().lower() == etiqueta_buscada.lower():
                return td.get_text(" ", strip=True)
    return None


def extraer_splice_variants(soup):
    """Recorre la tabla PROTEIN INFORMATION y arma una lista de
    diccionarios, uno por variante de splice del gen."""
    tabla = soup.find("table", class_="dark border")
    variantes = []
    for fila in tabla.find("tbody").find_all("tr"):
        celdas = fila.find_all("td")
        if len(celdas) < 8:
            continue
        variant_id = celdas[0].get_text(strip=True).split("ENSP")[0].strip()
        variantes.append({
            "variant_id": variant_id,
            "length_mass": celdas[5].get_text(" ", strip=True),
            "signal_peptide": celdas[6].get_text(strip=True),
            "transmembrane_regions": celdas[7].get_text(strip=True),
        })
    return variantes


def scrapear_gen(simbolo, ensembl_id):
    """Scrapea un gen puntual de HPA y devuelve (datos_planos, variantes_splice)."""
    url = f"https://www.proteinatlas.org/{ensembl_id}-{simbolo}/summary/gene"
    respuesta = requests.get(url)
    soup = BeautifulSoup(respuesta.content, "html.parser")

    tabla_general = encontrar_tabla_por_titulo(soup, "GENERAL INFORMATION")
    tabla_gen = encontrar_tabla_por_titulo(soup, "GENE INFORMATION")

    entrez_id_raw = extraer_campo(tabla_gen, "Entrez gene")
    transcritos_raw = extraer_campo(tabla_gen, "Number of transcripts")
    ubicacion_raw = extraer_campo(tabla_gen, "Chromosome location (bp)")

    variantes_splice = extraer_splice_variants(soup)

    datos_planos = {
        "gene_symbol": simbolo,
        "ensembl_id": ensembl_id,
        "entrez_id": int(entrez_id_raw) if entrez_id_raw else None,
        "synonyms": extraer_campo(tabla_general, "Synonyms"),
        "gene_description": extraer_campo(tabla_general, "Gene description"),
        "predicted_location": extraer_campo(tabla_general, "Predicted location"),
        "chromosome": extraer_campo(tabla_gen, "Chromosome"),
        "cytoband": extraer_campo(tabla_gen, "Cytoband"),
        "chromosome_location": ubicacion_raw,
        "posicion_inicio_bp": int(ubicacion_raw.split("-")[0].strip()) if ubicacion_raw else None,
        "number_of_transcripts": int(transcritos_raw) if transcritos_raw else None,
        "estado": "con variantes" if len(variantes_splice) > 0 else "sin variantes",
        "tiene_multiples_variantes": len(variantes_splice) > 1,
        "source_url": url,
    }

    return datos_planos, variantes_splice
