"""Actualiza en cursos_rasgos.csv los nombres de curso usando los identificadores de la malla."""

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COURSE_INPUTS = ROOT / "inputs" / "cursos"

cursosrasgos = pd.read_csv(COURSE_INPUTS / "cursos_rasgos.csv")
cursos = pd.read_csv(COURSE_INPUTS / "cursos_malla.csv")


nombres = cursosrasgos["id"].apply(lambda x: cursos[cursos["id"] == x]["nombre"].item())
if "nombre" in cursosrasgos.columns:
    cursosrasgos["nombre"] = nombres
else:
    cursosrasgos.insert(1, "nombre", nombres)

cursosrasgos.to_csv(COURSE_INPUTS / "cursos_rasgos.csv",index=False)
