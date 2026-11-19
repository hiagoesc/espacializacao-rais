"""Apoio a dados geográficos: tipos compatíveis com GeoPackage e conferência de CRS."""
import pandas as pd


def para_gpkg(df):
    """Converte colunas do pandas "novas" (string, Int32, boolean...) para tipos que o GeoPackage aceita.

    Inteiros sem nulos continuam inteiros (ano 2025, não 2025.0); com nulos viram decimais.
    Verdadeiro/falso vira 1/0. A geometria não é alterada.
    """
    out = df.copy()
    for col in out.columns:
        if col == "geometry":
            continue
        tipo = out[col].dtype
        if pd.api.types.is_bool_dtype(tipo):
            out[col] = out[col].astype("int8")
        elif pd.api.types.is_integer_dtype(tipo):
            out[col] = out[col].astype("int64") if not out[col].isna().any() else out[col].astype("float64")
        elif pd.api.types.is_numeric_dtype(tipo):
            out[col] = out[col].astype("float64")
        elif not pd.api.types.is_object_dtype(tipo):
            out[col] = out[col].astype(object).where(out[col].notna(), None)
    return out


def checar_crs(gdf, esperado: str, nome: str = "camada"):
    """Para com erro claro se o CRS da camada não for o esperado (ex.: 'EPSG:31983')."""
    atual = gdf.crs.to_string() if gdf.crs is not None else None
    if atual != esperado:
        raise ValueError(f"CRS inesperado em {nome}: {atual} (esperado {esperado})")
