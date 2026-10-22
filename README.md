# Conciliación Bancaria Automatizada con Python y Pandas

Notebook que automatiza la **conciliación bancaria**: cruza el libro auxiliar de la empresa con el extracto bancario, clasifica cada transacción y genera un reporte en Excel listo para revisión manual.

## Características

- 📥 Lee `Datos_Prueba.xlsx` (hojas `Libro_Auxiliar` y `Extracto_Bancario`).
- 🔁 Marca los **duplicados en cada hoja por separado** (antes del merge) y clasifica su origen.
- 🔍 Detecta **referencias sospechosas**: pares que casi coinciden pero difieren por espacios, mayúsculas o guiones (normalización con `strip`/`upper`).
- ⚖️ Clasifica cada transacción en `Estado_Final`: `Conciliado`, `Diferencia de Montos`, `Partida en Tránsito`, `Nota no Registrada` o `Revisión Manual`.
- 📤 Exporta un reporte Excel con **4 hojas**: detalle, resumen ejecutivo, referencias sospechosas y partidas sin contrapartida.

## Flujo del proceso

```
Datos_Prueba.xlsx
   │
   ├─ 1) Lee ambas hojas y marca duplicados por hoja (Duplicado_Libro / Duplicado_Banco)
   │
   ├─ 2) Detecta referencias sospechosas (normalización strip/upper)
   │
   ├─ 3) Merge outer por Referencia
   │
   ├─ 4) Columnas de análisis:
   │      Coinciliado, Partida en Tránsito / Nota no Registrada,
   │      Diferencia de Montos, Estado_Final, Origen_Duplicado
   │
   ├─ 5) Exporta Reporte_Conciliacion_Automatizada.xlsx (4 hojas)
   │
   └─ 6) Imprime el resumen en pantalla
```

## Estructura del proyecto

```
conciliacion/
├── concilicacion.ipynb            # Notebook principal
├── Datos_Prueba.xlsx              # Datos de prueba (2 hojas)
├── Guia_Estudio_Conciliacion_Bancaria.pdf   # Guía de estudio completa
├── README.md
└── conciliacion/                  # Entorno virtual (venv)
```

El notebook genera al ejecutarse: `Reporte_Conciliacion_Automatizada.xlsx`.

## Requisitos

- Python **3.12+** (una celda usa comillas anidadas en f-strings, disponibles desde Python 3.12)
- [pandas](https://pandas.pydata.org/) (DataFrames, lectura de Excel, merge)
- [numpy](https://numpy.org/) (`np.where`, `np.select`, valores `NaN`)
- [openpyxl](https://openpyxl.readthedocs.io/) (motor de escritura de Excel)

## Instalación

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install pandas openpyxl     # numpy se instala automáticamente con pandas
```

## Uso

```bash
jupyter notebook concilicacion.ipynb
```

Dentro del notebook: **Kernel → Restart & Run All**.

Al terminar se genera `Reporte_Conciliacion_Automatizada.xlsx` con estas hojas:

| Hoja | Contenido |
|---|---|
| `Detalle_Conciliacion` | Todas las transacciones con su estado, diferencias y duplicados |
| `Resumen_Ejecutivo` | Cantidad de transacciones por estado |
| `Referencias_Sospechosas` | Pares con errores de formato (espacios, mayúsculas, guiones) |
| `Sin_Contrapartida` | Referencias que no existen en el otro lado, con su origen |

## Datos de prueba (`Datos_Prueba.xlsx`)

- `Libro_Auxiliar` — 25 filas: `Fecha`, `Referencia`, `Concepto`, `Monto`
- `Extracto_Bancario` — 30 filas: `Fecha`, `Referencia`, `Descripcion_Banco`, `Monto`

Incluye casos reales de conciliación:
- Duplicados en el libro (`CHQ-005`, `CHQ-006`) y en el banco (`TRF-102`, `NOM-1002`, `COM-202`)
- Referencias con errores de formato: `CHQ-007 ` (espacio), `fac-1009` (minúsculas), `TRF103` (sin guion), `CHQ-00A` (formato inválido)
- Diferencias de montos (`FAC-1003`, `FAC-1006`, `FAC-1008`)
- Partidas en tránsito y notas no registradas

## Resultado actual con los datos de prueba

```
18 Conciliadas, 6 en tránsito, 3 diferencias
```

| Estado | Cantidad |
|---|---|
| Conciliado | 18 |
| Nota no Registrada | 11 |
| Partida en Tránsito | 6 |
| Diferencia de Montos | 3 |

## Documentación

La explicación completa (conceptos contables, librerías, funciones utilizadas y su porqué, errores comunes y buenas prácticas) está en **[Guia_Estudio_Conciliacion_Bancaria.pdf](Guia_Estudio_Conciliacion_Bancaria.pdf)**.

## Limitaciones y próximos pasos

- El notebook **detecta y reporta**, pero no corrige los datos automáticamente: la corrección se hace en el Excel de origen y se re-ejecuta.
- Posibles mejoras: comparar montos con tolerancia de decimales, detectar duplicados "parciales" (misma referencia, distinto monto), agregar gráficos de resumen y exportar también el `df` completo con `duplicados`.
