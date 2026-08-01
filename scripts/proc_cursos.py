"""Reconstruye los identificadores de curso desde el área, semestre y fila para generar una tabla de control."""

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COURSE_INPUTS = ROOT / "inputs" / "cursos"
TABLE_OUTPUTS = ROOT / "outputs" / "tablas"
TABLE_OUTPUTS.mkdir(parents=True, exist_ok=True)

cursos = pd.read_csv(COURSE_INPUTS / "cursos_malla.csv").drop(columns="id")

cursos.insert(0,'id',cursos["area"] + cursos["semestre"].astype(str).str.zfill(2) + cursos["fila"].astype(str).str.zfill(2))

cursos.to_csv(TABLE_OUTPUTS / "cursos_id.csv",index=False)
