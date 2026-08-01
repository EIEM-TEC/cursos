"""Genera la tabla del plan de estudios con tipo de curso, requisitos, correquisitos, créditos y horas."""

# Este archivo es para crear la columna esrequisito a partir de la columna requisitos de cada curso
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COURSE_INPUTS = ROOT / "inputs" / "cursos"
TABLE_OUTPUTS = ROOT / "outputs" / "tablas"
TABLE_OUTPUTS.mkdir(parents=True, exist_ok=True)

cursos = pd.read_csv(COURSE_INPUTS / "cursos_malla.csv")

tipCursoDic = {
    0: "No aplica",
    1: "Teórico",
    2: "Práctico",
    3: "Teórico - Práctico"
}

# Semestre, codigo, tipo, requ, corre, cred, horas totales pres, horas trabajo ind
planestudios = pd.DataFrame()
planestudios['id'] = cursos['id']
planestudios['semestre'] = cursos['semestre']
planestudios['codigo'] = cursos['codigo']
planestudios['nombre'] = cursos['nombre']
planestudios['tiponum'] = cursos['horasTeoria'].apply(lambda x: 0 if x == 0 else 1)\
                     + cursos['horasPractica'].apply(lambda x: 0 if x == 0 else 2)
planestudios['tipo'] = planestudios['tiponum'].apply(lambda x: tipCursoDic.get(x))
planestudios.drop('tiponum', axis=1, inplace=True)
planestudios['requisitos'] = cursos['requisitos']
planestudiosreq =planestudios[planestudios['requisitos'].notna()]
for index, row in planestudiosreq.iterrows():
    id = row['id']
    reqs = row['requisitos'].split(';')
    codigos = ''
    counter = 0
    for req in reqs:
        if counter >= 1:
            codigos += '; '
        codigos += planestudios.loc[planestudios['id'] == req, 'codigo'].item()
        counter += 1
    planestudios.loc[planestudios['id'] == id, 'requisitos'] = codigos
planestudios['correquisitos'] = cursos['correquisitos']
planestudioscoreq =planestudios[planestudios['correquisitos'].notna()]
for index, row in planestudioscoreq.iterrows():
    id = row['id']
    coreqs = row['correquisitos'].split(';')
    codigos = ''
    counter = 0
    for coreq in coreqs:
        if counter >= 1:
            codigos += '; '
        codigos += planestudios.loc[planestudios['id'] == coreq, 'codigo'].item()
        counter += 1
    planestudios.loc[planestudios['id'] == id, 'correquisitos'] = codigos
planestudios['creditos'] = cursos['creditos']
planestudios['HC'] = cursos['horasTeoria'] + cursos['horasPractica']
planestudios['HE'] = (planestudios['creditos'] * 3) - planestudios['HC']
planestudios['HE'] = planestudios['HE'].apply(lambda x: 0 if x < 0 else x)

print(planestudios.head())

planestudios.to_csv(TABLE_OUTPUTS / 'plan_de_estudios.csv',index=False)
