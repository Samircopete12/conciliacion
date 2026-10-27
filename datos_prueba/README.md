# datos_prueba/

Carpeta para alojar los **archivos de datos de prueba generados** para probar el
proyecto de conciliación bancaria.

## Cómo generar un archivo nuevo

1. Abre [`PROMPT_GENERADOR_DATOS.md`](PROMPT_GENERADOR_DATOS.md).
2. Copia el prompt y pégalo tal cual (trae **parámetros predeterminados** listos
   para el proyecto). Opcionalmente, cambia los valores marcados con 🔄
   (cantidad de filas, errores, rango de fechas, ID de la corrida).
3. Pega el prompt como primer mensaje en una sesión nueva de un agente de código
   dentro de `/home/rimas/conciliacion`.
4. El agente creará aquí:
   - `Datos_Prueba_{ID}.xlsx`  → datos con errores plantados
   - `Control_{ID}.xlsx`       → tabla de control: qué error se plantó y qué
     debería detectar la aplicación

## Convenciones

- `{ID}` es un número o código de corrida: `01`, `02`, `03`...
- Cada generación debe usar **referencias y semilla distintas** para que cada
  archivo sea un caso de prueba diferente.
- La tabla de control permite validar que el notebook detecta exactamente los
  errores planteados.

## Probar el notebook con un archivo generado

El notebook lee `Datos_Prueba.xlsx` de la carpeta raíz. Para usar un archivo de
esta carpeta, cópialo (respalda antes el original):

```bash
cp Datos_Prueba.xlsx /tmp/opencode/Datos_Prueba_respaldo.xlsx
cp datos_prueba/Datos_Prueba_01.xlsx Datos_Prueba.xlsx
```

Luego en Jupyter: **Kernel → Restart & Run All**.
