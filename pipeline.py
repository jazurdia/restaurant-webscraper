import argparse
from typing import Optional
import pandas as pd
import numpy as np
import hashlib
from pathlib import Path

CANON_MAP = {
    "UWS": "Upper West Side",
    "UES": "Upper East Side",
    "U.E.S": "Upper East Side",
    "Midtown West": "Midtown",
    "Midtown East": "Midtown",
}

def _make_composite_key(row) -> str:
    parts = [
        str(row.get("review_id", "")),
        str(row.get("restaurant_name", "")),
        str(row.get("reviewer_name", "")),
        str(row.get("review_text", "")),
        str(row.get("published_timestamp", "")),
    ]
    return hashlib.md5("||".join(parts).encode("utf-8", errors="ignore")).hexdigest()

def _ts_to_datetime(series: pd.Series) -> pd.Series:
    ts = pd.to_numeric(series, errors="coerce")
    use_ms = (ts.dropna() > 10**12).mean() > 0.5  # heurística: ms si la mayoría > 1e12
    unit = "ms" if use_ms else "s"
    return pd.to_datetime(ts, unit=unit, utc=True, errors="coerce")

def clean_reviews(input_csv: str, output_csv: str, dict_md: Optional[str] = None) -> pd.DataFrame:
    df_raw = pd.read_csv(input_csv, low_memory=False)

    # --- Deduplicación por llave compuesta (robusta ante faltantes)
    key = df_raw.apply(_make_composite_key, axis=1)
    n_dupes = int(key.duplicated().sum())
    df = df_raw.loc[~key.duplicated()].copy()

    # --- Tipos numéricos/booleanos
    for col in ["rating", "likes_count", "reviewer_total_reviews"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "is_local_guide" in df.columns:
        df["is_local_guide"] = (
            df["is_local_guide"].astype(str).strip().str.lower().map({"true": True, "false": False})
        )

    # --- Fechas: timestamp -> UTC + derivadas
    if "published_timestamp" in df.columns:
        dt = _ts_to_datetime(df["published_timestamp"])
        df["review_datetime_utc"] = dt
        df["review_date"] = df["review_datetime_utc"].dt.date
        df["review_year"] = df["review_datetime_utc"].dt.year
        df["review_month"] = df["review_datetime_utc"].dt.month

    # --- Texto: limpieza básica
    if "review_text" in df.columns:
        df["review_text"] = df["review_text"].astype(str).str.replace(r"\s+", " ", regex=True).str.strip()

    # --- Barrio normalizado + canónico (opcional)
    if "neighborhood" in df.columns:
        df["neighborhood_norm"] = df["neighborhood"].astype(str).str.strip()
        df["neighborhood_canon"] = df["neighborhood_norm"].replace(CANON_MAP)

    # --- Guardado
    Path(output_csv).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False)

    # --- Diccionario de datos (opcional)
    if dict_md:
        _write_data_dictionary(df, dict_md)

    # --- Resumen consola
    print(f"Filas crudas: {len(df_raw)}")
    print(f"Duplicados removidos: {n_dupes}")
    print(f"Filas limpias: {len(df)}")
    return df

def _write_data_dictionary(df: pd.DataFrame, path_md: str) -> None:
    col_desc = {
        "restaurant_name": "Nombre del restaurante.",
        "neighborhood": "Barrio en Manhattan asociado al restaurante.",
        "cuisine_type": "Tipo de cocina (si está disponible).",
        "place_url": "URL del lugar en Google Maps.",
        "reviewer_name": "Nombre del usuario autor de la reseña.",
        "rating": "Calificación numérica de 1 a 5.",
        "review_text": "Texto libre de la reseña.",
        "review_text_translated": "Texto traducido, si se dispone.",
        "review_length": "Longitud del texto de la reseña en caracteres.",
        "published_date": "Fecha de publicación en formato relativo (si se extrajo).",
        "published_timestamp": "Marca de tiempo unix (s/ms).",
        "likes_count": "Cantidad de 'me gusta' de la reseña.",
        "reviewer_total_reviews": "Reseñas totales del autor.",
        "is_local_guide": "Indicador booleano si es Local Guide.",
        "owner_response": "Respuesta del propietario (si existe).",
        "review_id": "ID único de la reseña (si existe).",
        "review_url": "URL directa a la reseña.",
        "review_datetime_utc": "Fecha-hora en UTC derivada del timestamp.",
        "review_date": "Fecha (YYYY-MM-DD) derivada.",
        "review_year": "Año de la reseña (derivado).",
        "review_month": "Mes de la reseña (derivado).",
        "neighborhood_norm": "Barrio normalizado (trim).",
        "neighborhood_canon": "Barrio mapeado a una taxonomía canónica simple.",
    }
    lines = ["# Diccionario de Datos — Manhattan Reviews", "", "Columnas principales y derivadas:\n"]
    for c, d in col_desc.items():
        if c in df.columns:
            try:
                example = str(df[c].dropna().iloc[0]) if df[c].notna().any() else ""
            except Exception:
                example = ""
            lines.append(f"- **{c}**: {d}" + (f"\n  _Ejemplo_: {example}" if example else ""))

    Path(path_md).write_text("\n".join(lines), encoding="utf-8")
    print(f"Diccionario de datos escrito en: {path_md}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="input_csv", required=True)
    ap.add_argument("--out", dest="output_csv", required=True)
    ap.add_argument("--dict", dest="dict_md", default=None, help="Ruta para escribir data dictionary .md")
    args = ap.parse_args()
    clean_reviews(args.input_csv, args.output_csv, dict_md=args.dict_md)
