"""Valida que el identificador de cada curso coincida con su área, semestre y posición en la malla."""

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
cursos = pd.read_csv(ROOT / "inputs" / "cursos" / "cursos_malla.csv")

for index, curso in cursos.iterrows():
    idtest = curso["area"] + str(curso["semestre"]).zfill(2) + str(curso["fila"]).zfill(2)
    if curso["id"] != idtest:
        print("Error en el id del curso", curso["id"], idtest)
