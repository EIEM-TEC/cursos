# Contexto del mantenimiento curricular

Este repositorio es la fuente de verdad de los datos curriculares y los programas de curso vigentes de Ingeniería Electromecánica. Alimenta el documento curricular actualizado de `EIEM-TEC/base`.

## Relación entre repositorios

- `EIEM-TEC/CLIE` conserva el documento original de creación de la carrera, ya aprobado. No lo modifique ni use sus archivos históricos para reemplazar datos vigentes.
- `cursos` mantiene los insumos y genera programas, mallas, gráficos y tablas. Respete la estructura `inputs`, `scripts` y `outputs`.
- `base` mantiene el documento curricular vivo. Todo cambio en un programa de curso o en la estructura general debe reflejarse en las partes y productos afectados de ambos repositorios.

## Al realizar modificaciones

1. Lea los insumos actuales de `cursos` y preserve los cambios locales del usuario. No importe copias antiguas desde `CLIE` o `base` sobre estos datos.
2. Edite la fuente correspondiente en `inputs` y regenere las salidas afectadas; no trate los PDF o las tablas generadas como insumos maestros. `outputs/mallas/areas.csv` y `datos_malla.csv` son salidas calculadas.
3. Mantenga los datos docentes como dependencia externa del repositorio `EIEM-TEC/profes`.
4. Revise el impacto en el documento de `base`: sus mallas y gráficos se descargan desde las salidas publicadas, pero su texto y sus tablas no se sincronizan automáticamente.
5. Actualice las partes relacionadas dentro del alcance del trabajo y señale lo que quede pendiente en el otro repositorio. Generar archivos locales no equivale a publicarlos ni a sincronizar el documento completo.
6. Describa qué cambió y por qué. No atribuya aprobación institucional a propuestas o ediciones sin respaldo; el original aprobado de `CLIE` conserva su carácter histórico.

Consulte `README.md` para los comandos de generación y la estructura del repositorio.
