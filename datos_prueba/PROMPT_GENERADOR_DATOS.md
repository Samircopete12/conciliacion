# Prompt reutilizable: generador de archivos Excel de prueba con errores controlados

Copia este prompt y pégalo a un agente de código. **Ya trae parámetros
predeterminados**: si no cambias nada, genera un archivo listo para el proyecto
de conciliación bancaria. Para cada nueva corrida, ajusta solo los valores que
quieras variar (marca cada ajuste con 🔄 o simplemente edita el valor).

---

Actúa como un ingeniero de pruebas de datos. Genera un archivo Excel de DATOS DE
PRUEBA REALISTAS con errores controlados, para probar una aplicación de
validación/cruce de datos.

PARÁMETROS (valores predeterminados; cámbialos para variar cada corrida)
- Identificador de corrida: 01                          (🔄 cambia: 02, 03...)
- Carpeta de salida: datos_prueba/
- Archivo de salida: Datos_Prueba_01.xlsx               (🔄 usa el ID nuevo)
- Hojas y columnas EXACTAS esperadas por la aplicación:
  * Hoja 1 "Libro_Auxiliar": Fecha, Referencia, Concepto, Monto
  * Hoja 2 "Extracto_Bancario": Fecha, Referencia, Descripcion_Banco, Monto
- Columna de cruce entre hojas: Referencia
- Volumen: 120 filas en Libro_Auxiliar y 120 en Extracto_Bancario   (🔄 ajustable)
- Rango de fechas: 2026-10-01 a 2026-10-31              (🔄 ajustable)
- Contexto de realismo: empresa comercial colombiana ("Comercial Andina SAS");
  referencias con prefijos CHQ-###, FAC-###, TRF-###, NOM-###, IMP-###,
  NC-###, ND-###, GMF-###, INT-###, DEV-###, DOM-###, TRAN-#####; conceptos
  típicos (proveedores, clientes, nómina, DIAN, servicios, intereses,
  comisiones); montos entre -25.000.000 y 25.000.000, coherentes con cada
  concepto, con y sin decimales.
- Tipos de datos a preservar: Fecha como fecha, Monto como número,
  Referencia como texto.
- Errores a plantar:
  * 4 filas duplicadas solo en Libro_Auxiliar
  * 4 filas duplicadas solo en Extracto_Bancario
  * 2 duplicadas en ambas hojas
  * 8 referencias con errores de formato (espacios al inicio/final,
    minúsculas, guiones omitidos o de más, ceros de más) que NO coincidan
    por texto exacto con su contraparte
  * 8 pares con montos diferentes
  * 15 filas legítimas solo en Libro_Auxiliar y 15 solo en Extracto_Bancario
  * 2 referencias inválidas (formato roto) sin contrapartida
  (🔄 todas las cantidades son ajustables)
- Reglas específicas adicionales (OPCIONAL — solo si tu aplicación evalúa reglas
  propias no contempladas arriba). Por cada regla, describe qué valida y pide
  datos que la cumplan Y que la violen. Ejemplos:
  * "Los montos se comparan con tolerancia de ±0,5: planta 4 pares con
    diferencias de centavos que deban tratarse como coincidentes."
  * "La fecha del banco no puede ser anterior a la del libro: planta 3 casos
    con fechas invertidas."
  * "El GMF debe ser menor a $100: planta 1 caso fuera de rango."
  * "Ciertos prefijos (IMP-, NOM-) deben existir siempre en ambas hojas:
    planta 2 casos donde falten en un lado."
  * "La suma de débitos debe coincidir con la suma de créditos: planta 1
    desbalance."
  Si no hay reglas específicas, omite este bloque por completo.

TAREA
1. Crea la carpeta de salida si no existe y genera Datos_Prueba_{ID}.xlsx con
   las hojas y columnas exactas del bloque de parámetros. Sin fórmulas y sin
   columnas extra.
2. Planta TODOS los errores indicados. El resto de las filas debe ser
   coherente y realista. Preserva los errores de texto tal cual (espacios,
   mayúsculas) y los tipos de datos definidos.
3. Genera además un archivo de control Control_{ID}.xlsx con UNA FILA POR CADA
   ERROR PLANTADO: hoja, referencia, tipo de error y estado esperado según la
   aplicación. Incluye también los casos de reglas específicas (si las hay),
   indicando la regla asociada y el resultado esperado. Anota la semilla
   aleatoria usada.
4. Varía entre generaciones: referencias distintas, cantidades distintas y
   semilla distinta, para que cada archivo sea un caso de prueba diferente.
5. Al terminar, reporta: filas por hoja, errores plantados por tipo, semilla
   usada y ruta de los archivos generados.

REGLA DE ORO
Cada generación debe ser autocontenida y reproducible: usando la tabla de
control se debe poder comprobar que la aplicación detectó exactamente los
errores planteados.
