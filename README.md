# Generación de cursos y mallas

Este repositorio es la fuente de verdad para mantener actualizados los datos curriculares y los programas de curso de Ingeniería Electromecánica. Genera programas, mallas, gráficos y tablas auxiliares que alimentan el documento curricular vigente del repositorio `EIEM-TEC/base`.

## Origen y propósito

El repositorio `EIEM-TEC/CLIE` conserva el documento original con el que se creó la carrera. Ese documento ya fue aprobado y no debe modificarse: permanece como referencia histórica. `cursos` y `base` se mantienen por separado para reflejar la evolución del programa sin alterar el original aprobado.

Los datos vigentes se modifican en `cursos`, respetando la estructura `inputs`, `scripts` y `outputs`. `base` mantiene el documento que reúne la estructura curricular actualizada. Los archivos históricos de `CLIE` y las copias de recursos de `base` no sustituyen a los insumos de `cursos` como fuente de verdad.

## Alcance de cada actualización

Todo cambio en un programa de curso o en la estructura curricular general debe quedar registrado aquí y reflejarse en las salidas y en las partes afectadas del documento de `base`. Esto incluye, según corresponda, contenidos, objetivos, evaluación, bibliografía, requisitos, créditos, plan de estudios, saberes, rasgos, ejes y mallas.

Actualice primero los insumos de `cursos`, regenere las salidas afectadas y revise su impacto en `base`. Documente qué cambió y por qué, y distinga propuestas pendientes de cambios aprobados cuando corresponda. Modificar archivos no constituye por sí mismo una aprobación institucional.

La descarga de mallas y gráficos publicados está automatizada en `base`, pero el texto y las tablas del documento todavía requieren actualización explícita. Si queda trabajo pendiente en el otro repositorio, indíquelo al entregar el cambio; no dé por sincronizado todo el documento por haber regenerado los PDF.

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
- `outputs/graficos`: gráficos curriculares vectoriales usados por el documento base.
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

Generar los gráficos curriculares:

```powershell
python scripts/gen_graficos.py
```

Este comando usa `inputs/saberes/saberes.csv` y
`outputs/mallas/areas.csv`, y produce `TRC.pdf`, `porcTRC.pdf`, `INS.pdf`,
`AER.pdf`, `SCF.pdf` y `ENF.pdf` en `outputs/graficos`.

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
