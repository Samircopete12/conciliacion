"""Conciliación bancaria automatizada con Python y Pandas.

Versión en script del notebook concilicacion.ipynb.

Flujo:
    1. Pide el nombre de un archivo Excel ubicado en la carpeta datos_prueba/.
    2. Lee las hojas Libro_Auxiliar y Extracto_Bancario y marca duplicados
       en cada hoja (antes del merge).
    3. Detecta referencias sospechosas (misma referencia normalizada,
       texto original distinto) y referencias sin contrapartida.
    4. Hace el merge outer por Referencia y clasifica cada transacción
       (Conciliado, Diferencia de Montos, Partida en Tránsito,
       Nota no Registrada) y el origen de los duplicados.
    5. Exporta un reporte Excel con 4 hojas a datos_prueba/Reporte_<nombre>.xlsx
       e imprime un resumen en pantalla.

Ejecutar:
    python conciliacion.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

# Carpeta donde se alojan los archivos de datos de prueba
# (anclada a la ubicacion del script, no al directorio de ejecucion)
CARPETA_DATOS = Path(__file__).resolve().parent / "datos_prueba"
ARCHIVO_POR_DEFECTO = "Datos_Prueba_01.xlsx"


def normalizar(ref):
    """Forma canonica de una referencia para comparar textos con errores
    de formato (espacios, mayusculas, guiones)."""
    return str(ref).strip().upper().replace(" ", "").replace("-", "")


def pedir_archivo() -> Path:
    """Pide al usuario el nombre del archivo y valida que exista."""
    CARPETA_DATOS.mkdir(exist_ok=True)
    disponibles = sorted(p.name for p in CARPETA_DATOS.glob("*.xlsx"))
    if not disponibles:
        raise SystemExit(
            f"No hay archivos .xlsx en {CARPETA_DATOS}. "
            "Coloca alli el archivo de datos de prueba y vuelve a ejecutar."
        )

    print("Archivos disponibles en datos_prueba/:")
    for nombre in disponibles:
        print(f"  - {nombre}")

    nombre = input(
        f"Nombre del archivo a procesar (Enter = {ARCHIVO_POR_DEFECTO}): "
    ).strip()
    nombre = nombre or ARCHIVO_POR_DEFECTO

    ruta = CARPETA_DATOS / nombre
    if not ruta.exists():
        raise SystemExit(f"No existe {ruta}. Revisa el nombre.")
    return ruta


def cargar_datos(ruta: Path):
    """Lee ambas hojas y marca los duplicados en cada hoja, antes del merge.

    keep=False marca TODAS las filas involucradas en un duplicado.
    """
    try:
        df1 = pd.read_excel(ruta, "Libro_Auxiliar")
        df2 = pd.read_excel(ruta, "Extracto_Bancario")
    except ValueError as e:
        raise SystemExit(f"No se pudo leer {ruta.name}: {e}") from e

    df1["Duplicado_Libro"] = np.where(df1["Referencia"].duplicated(keep=False), "SI", "")
    df2["Duplicado_Banco"] = np.where(df2["Referencia"].duplicated(keep=False), "SI", "")
    return df1, df2


def detectar_sospechosas(df1, df2):
    """Referencias sospechosas: misma normalizada, texto original distinto.
    Usa copias temporales para no modificar las fuentes."""
    tmp1 = df1[["Referencia"]].assign(Ref_Norm=df1["Referencia"].map(normalizar))
    tmp2 = df2[["Referencia"]].assign(Ref_Norm=df2["Referencia"].map(normalizar))

    sospechosas = tmp1.merge(tmp2, on="Ref_Norm", suffixes=("_libro", "_banco"))
    sospechosas = sospechosas[
        sospechosas["Referencia_libro"] != sospechosas["Referencia_banco"]
    ].drop_duplicates()

    # Referencias sin contrapartida ni siquiera normalizada
    # (partidas legitimas o errores)
    sin_libro = df1[~df1["Referencia"].map(normalizar).isin(df2["Referencia"].map(normalizar))]
    sin_banco = df2[~df2["Referencia"].map(normalizar).isin(df1["Referencia"].map(normalizar))]
    return sospechosas, sin_libro, sin_banco


def analizar(df1, df2):
    """Merge y clasificacion de transacciones. Devuelve (df, df_reporte)."""
    df = pd.merge(df1, df2, on="Referencia", how="outer")

    df["Coinciliado"] = np.where(df["Monto_x"] == df["Monto_y"], "SI", "NO")

    en_libro_sin_banco = df["Monto_x"].notna() & df["Monto_y"].isna()
    en_banco_sin_libro = df["Monto_x"].isna() & df["Monto_y"].notna()
    df["Partida en Tránsito / Nota no Registrada"] = np.select(
        [en_libro_sin_banco, en_banco_sin_libro],
        ["Partida en Tránsito", "Nota no Registrada"],
        default="",
    )

    df["Diferencia de Montos"] = np.where(
        df["Monto_x"] - df["Monto_y"] != 0,
        df["Monto_x"] - df["Monto_y"],
        np.nan,
    )

    # Unificamos todas las validaciones en una sola columna 'Estado_Final'
    condiciones = [
        df["Monto_x"] == df["Monto_y"],  # Conciliado perfecto
        df["Monto_x"].notna() & df["Monto_y"].notna() & (df["Monto_x"] != df["Monto_y"]),  # Diferencia
        df["Monto_x"].notna() & df["Monto_y"].isna(),  # Solo en libros
        df["Monto_x"].isna() & df["Monto_y"].notna(),  # Solo en banco
    ]
    opciones = ["Conciliado", "Diferencia de Montos", "Partida en Tránsito", "Nota no Registrada"]
    df["Estado_Final"] = np.select(condiciones, opciones, default="Revisión Manual")

    # Nombres legibles en vez de los sufijos _x/_y del merge
    df = df.rename(
        columns={
            "Fecha_x": "Fecha_Libro",
            "Concepto": "Concepto_Libro",
            "Monto_x": "Monto_Libro",
            "Fecha_y": "Fecha_Banco",
            "Descripcion_Banco": "Concepto_Banco",
            "Monto_y": "Monto_Banco",
        }
    )

    # Origen del duplicado segun en que hoja aparece repetido
    df["Origen_Duplicado"] = np.select(
        [
            df["Duplicado_Libro"].eq("SI") & df["Duplicado_Banco"].eq("SI"),
            df["Duplicado_Libro"].eq("SI"),
            df["Duplicado_Banco"].eq("SI"),
        ],
        ["Duplicado en ambos lados", "Duplicado solo en Libro", "Duplicado solo en Banco"],
        default="",
    )

    columnas_finales = [
        "Referencia", "Fecha_Libro", "Concepto_Libro", "Monto_Libro",
        "Fecha_Banco", "Concepto_Banco", "Monto_Banco",
        "Diferencia de Montos", "Estado_Final",
        "Duplicado_Libro", "Duplicado_Banco", "Origen_Duplicado",
    ]
    df_reporte = df[columnas_finales].fillna("-")
    return df, df_reporte


def exportar(ruta_entrada: Path, df_reporte, sospechosas, sin_libro, sin_banco) -> Path:
    """Exporta el reporte con 4 hojas a datos_prueba/Reporte_<nombre>.xlsx."""
    nombre_salida = CARPETA_DATOS / f"Reporte_{ruta_entrada.stem}.xlsx"

    with pd.ExcelWriter(nombre_salida, engine="openpyxl") as writer:
        # 1. Detalle (el DataFrame completo)
        df_reporte.to_excel(writer, sheet_name="Detalle_Conciliacion", index=False)

        # 2. Resumen ejecutivo
        resumen = df_reporte["Estado_Final"].value_counts().reset_index()
        resumen.columns = ["Estado", "Cantidad de Transacciones"]
        resumen.to_excel(writer, sheet_name="Resumen_Ejecutivo", index=False)

        # 3. Referencias sospechosas
        sospechosas.to_excel(writer, sheet_name="Referencias_Sospechosas", index=False)

        # 4. Sin contrapartida
        sin_libro_export = sin_libro[["Fecha", "Referencia", "Monto"]].assign(Origen="Libro_Auxiliar")
        sin_banco_export = sin_banco[["Fecha", "Referencia", "Monto"]].assign(Origen="Extracto_Bancario")
        sin_contrapartida = pd.concat([sin_libro_export, sin_banco_export], ignore_index=True)
        sin_contrapartida.to_excel(writer, sheet_name="Sin_Contrapartida", index=False)

    return nombre_salida


def resumen(df):
    """Imprime los indicadores principales."""
    print()
    print("Resumen por estado:")
    print(df["Estado_Final"].value_counts().to_string())
    print()
    print(
        f"{(df['Coinciliado'] == 'SI').sum()} Coinciliadas, "
        f"{(df['Partida en Tránsito / Nota no Registrada'] == 'Partida en Tránsito').sum()} en tránsito, "
        f"{(df['Diferencia de Montos'].notna() & (df['Diferencia de Montos'] != 0)).sum()} diferencias"
    )


def main():
    ruta = pedir_archivo()
    print(f"\nProcesando: {ruta.name}")

    df1, df2 = cargar_datos(ruta)

    sospechosas, sin_libro, sin_banco = detectar_sospechosas(df1, df2)
    print(f"Pares sospechosos detectados: {len(sospechosas)}")

    df, df_reporte = analizar(df1, df2)

    salida = exportar(ruta, df_reporte, sospechosas, sin_libro, sin_banco)
    print(f"¡Reporte generado con éxito! Archivo guardado como: {salida}")

    resumen(df)


if __name__ == "__main__":
    main()
