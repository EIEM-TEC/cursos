"""Genera los gráficos curriculares PDF usados por el documento base."""

from pathlib import Path

import pandas as pd

import funciones_graficos as fun


ROOT = Path(__file__).resolve().parent.parent
SABERES_INPUT = ROOT / "inputs" / "saberes" / "saberes.csv"
AREAS_OUTPUT = ROOT / "outputs" / "mallas" / "areas.csv"
GRAPH_OUTPUTS = ROOT / "outputs" / "graficos"
GENERATED_FILES = ("TRC.pdf", "porcTRC.pdf", "INS.pdf", "AER.pdf", "SCF.pdf", "ENF.pdf")


def generar_graficos() -> None:
    """Lee los datos de cursos y regenera los seis gráficos vectoriales."""
    if not AREAS_OUTPUT.exists():
        from proc_areas import generar_areas

        generar_areas()

    GRAPH_OUTPUTS.mkdir(parents=True, exist_ok=True)
    for nombre in GENERATED_FILES:
        archivo = GRAPH_OUTPUTS / nombre
        if archivo.exists():
            archivo.unlink()

    saberes = pd.read_csv(SABERES_INPUT)
    areas = pd.read_csv(AREAS_OUTPUT)

    lista_trc = ["CIB", "FPH", "CYD", "IEE", "IMM", "AUT", "ADD"]
    trc = areas[areas["codArea"].isin(lista_trc)]
    categorias_trc = trc["codArea"].to_list()
    valores_trc = trc["porcTRC"].to_list()

    lista_enfasis = ["CIB", "FPH", "CYD", "IEE", "IMM", "AUT", "ADD", "ENF"]
    enfasis = areas[areas["codArea"].isin(lista_enfasis)]
    categorias_enfasis = enfasis["codArea"].to_list()
    valores_enfasis = enfasis["porcENF"].to_list()

    fun.radar("TRC", areas, categorias_trc, valores_trc, "", 14, 18, 20, 5, 30, GRAPH_OUTPUTS)
    fun.multiradar(lista_trc, saberes, areas, "porcTRC", 10, 12, 12, 4, 20, GRAPH_OUTPUTS)
    fun.radar_saberes("INS", saberes, areas, "porcINS", 14, 18, 12, 3, 30, GRAPH_OUTPUTS)
    fun.radar_saberes("AER", saberes, areas, "porcAER", 14, 18, 12, 3, 30, GRAPH_OUTPUTS)
    fun.radar_saberes("SCF", saberes, areas, "porcSCF", 14, 18, 12, 3, 30, GRAPH_OUTPUTS)
    fun.radar("ENF", areas, categorias_enfasis, valores_enfasis, "", 14, 18, 25, 5, 30, GRAPH_OUTPUTS)

    print(f"Gráficos PDF vectoriales generados en: {GRAPH_OUTPUTS}")


if __name__ == "__main__":
    generar_graficos()
