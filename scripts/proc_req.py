"""Recalcula en cursos_malla.csv qué cursos dependen de cada requisito y correquisito."""

# Este archivo es para crear la columna esrequisito a partir de la columna requisitos de cada curso
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COURSE_INPUTS = ROOT / "inputs" / "cursos"
cursos = pd.read_csv(COURSE_INPUTS / "cursos_malla.csv")

cursos['esrequisito'] = None # borrar los datos de la columna

cursosreq = cursos[cursos['requisitos'].notna()]
for index, row in cursosreq.iterrows():
    id = row['id']
    print(f"\nCurso: {id}")
    reqs = row['requisitos'].split(';')
    for req in reqs:
        print(f"Requisito: {req}")
        curr_val = cursos.loc[cursos['id'] == req, 'esrequisito'].item()
        if curr_val == None:
            cursos.loc[cursos['id'] == req, 'esrequisito'] = id
        else:
            cursos.loc[cursos['id'] == req, 'esrequisito'] = cursos[cursos['id'] == req]['esrequisito'].item() + ';' + id

cursoscorreq = cursos[cursos['correquisitos'].notna()]
for index, row in cursoscorreq.iterrows():
    id = row['id']
    print(f"\nCurso: {id}")
    correqs = row['correquisitos'].split(';')
    for correq in correqs:
        print(f"Correquisito: {correq}")
        curr_val = cursos.loc[cursos['id'] == correq, 'esrequisito'].item()
        if curr_val == None:
            cursos.loc[cursos['id'] == correq, 'esrequisito'] = id
        else:
            cursos.loc[cursos['id'] == correq, 'esrequisito'] = cursos[cursos['id'] == correq]['esrequisito'].item() + ';' + id


print(cursos.head(50))

cursos.to_csv(COURSE_INPUTS / 'cursos_malla.csv',index=False)
