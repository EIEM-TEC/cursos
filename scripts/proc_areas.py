"""Calcula los porcentajes de cada área curricular por plan y los guarda como salida de la malla."""

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MALLA_OUTPUTS = ROOT / "outputs" / "mallas"


def generar_areas():
    """Calcula, guarda y devuelve la tabla de porcentajes por área curricular."""
    saberes = pd.read_csv(ROOT / "inputs" / "saberes" / "saberes.csv")
    MALLA_OUTPUTS.mkdir(parents=True, exist_ok=True)

    areas = saberes[
        ['codArea', 'porcTRC', 'porcINS', 'porcAER', 'porcSCF']
    ].groupby("codArea", as_index=True).sum().round(2)
    areas['porcENF'] = areas['porcTRC']
    areas.loc["ENF"] = [0, 0, 0, 0, 25]
    areas.loc["TOT"] = areas.sum().round(2)
    areas.insert(0, "nombre", [
        "Analisís de datos",
        "Aeronáutica",
        "Automática",
        "Ciencias básicas",
        "Comunicación y dibujo",
        "Formación profesional y habilidades interpersonales",
        "Ingeniería eléctrica y electrónica",
        "Ingeniería mecánica y de materiales",
        "Instalaciones electromecánicas",
        "Sistemas ciberfísicos",
        "Énfasis",
        "Total",
    ])
    areas.to_csv(MALLA_OUTPUTS / 'areas.csv')
    return areas


if __name__ == "__main__":
    print(generar_areas())

