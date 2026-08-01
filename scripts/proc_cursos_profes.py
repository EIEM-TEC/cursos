"""Genera la tabla curso-profesor combinando asignaciones locales con los datos docentes publicados en GitHub."""

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COURSE_INPUTS = ROOT / "inputs" / "cursos"
TABLE_OUTPUTS = ROOT / "outputs" / "tablas"
TABLE_OUTPUTS.mkdir(parents=True, exist_ok=True)

cursos_profes = pd.read_csv(COURSE_INPUTS / "cursos_profes.csv")
datos_profes = pd.read_csv("https://raw.githubusercontent.com/EIEM-TEC/profes/refs/heads/main/00_datos.csv")
cursos_malla = pd.read_csv(COURSE_INPUTS / "cursos_malla.csv")

cursos_profes["profesores"] = cursos_profes["profesores"].str.split(";",expand=False)
cursos_profes = cursos_profes.explode("profesores")
cursos_profes = cursos_profes.merge(datos_profes[["codigo", "nombre"]], left_on="profesores", right_on="codigo", how="left").drop(columns=["codigo","profesores"]).copy()
cursos_profes = cursos_profes.merge(cursos_malla[["semestre","id","codigo","nombre"]],left_on="id", right_on="id", how="left").drop(columns="id").copy()
cursos_profes.rename(columns={"nombre_x":"profesor", "nombre_y":"curso"},inplace=True)
cursos_profes = cursos_profes[["semestre","codigo", "curso", "profesor"]]
cursos_profes.to_csv(TABLE_OUTPUTS / 'tabla_profes.csv',index=False)
print(cursos_profes)
