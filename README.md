# Generación de cursos y mallas

Repositorio autocontenido para mantener los datos de cursos y generar programas,
mallas y tablas auxiliares.

## Estructura

- `inputs/cursos`: tablas fuente de cursos. En `cursos_malla.csv`, la columna
  `propio` indica con `1` cuáles cursos tienen programa curricular y con `0`
  cuáles pertenecen a la malla pero no se generan localmente.
- `inputs/bibliografias`: bibliografías por área curricular.
- `inputs/saberes`: definiciones de saberes y rasgos.
- `inputs/figuras`: imágenes de portada, encabezado y pie.
- `outputs/mallas/areas.csv`: porcentajes calculados de cada área curricular en la malla.
- `outputs/mallas/datos_malla.csv`: datos calculados durante la generación de la malla.
- `scripts`: generadores y procesos de mantenimiento.
- `outputs/programas`: programas de curso generados.
- `outputs/mallas`: malla EM, datos y exportaciones visuales.
- `outputs/tablas`: tablas consolidadas generadas por los procesos.

## Instalación

```powershell
python -m pip install -r requirements.txt
```

La generación de PDF requiere una instalación de LaTeX con `lualatex` y
`biber`.

Los datos y grados docentes se consultan directamente desde los CSV oficiales
del repositorio `EIEM-TEC/profes` en GitHub.

## Comandos principales

Calcular los porcentajes por área curricular:

```powershell
python scripts/proc_areas.py
```

Este proceso genera `outputs/mallas/areas.csv`. Debe ejecutarse nuevamente
cuando cambien las definiciones contenidas en `inputs/saberes`. Si el archivo
no existe, el generador de la malla lo crea automáticamente.

Generar uno o más programas:

```powershell
python scripts/gen_programa.py SCF1002
python scripts/gen_programa.py SCF1002 AER0901
```

Generar todos los programas:

```powershell
python scripts/gen_programa.py --all
```

Generar la malla curricular completa y sus cuatro PDF individuales:

```powershell
python scripts/gen_malla.py
```

Este comando produce `malla.pdf`, `mallaTRC.pdf`, `mallaINS.pdf`,
`mallaAER.pdf` y `mallaCIB.pdf` en `outputs/mallas`.

Generar tablas consolidadas:

```powershell
python scripts/proc_plan_est.py
python scripts/proc_rasgos.py
python scripts/proc_cursos_profes.py
python scripts/proc_cursos.py
```

## Archivos excluidos de la migración

- La carpeta histórica `programas`, porque contiene salidas generadas.
- `gen_programa_resumen.py` y los CSV de resumen.
- `malla_MI.*`, `cursos_malla_MI.csv` y `proc_req_MI.py`.
- `proc_descrip.py`, porque depende de un archivo inexistente y no tiene salidas activas.
