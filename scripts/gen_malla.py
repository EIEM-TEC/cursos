"""Genera la malla completa y cuatro PDF individuales, además de sus datos derivados."""

import pandas as pd
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from pylatex import Document, Package, Command, PageStyle, Head, Foot, NewPage,\
    TextColor, MiniPage, StandAloneGraphic, simple_page_number,\
    TikZ, TikZScope, TikZNode, TikZOptions, TikZCoordinate, TikZNodeAnchor, TikZPath,\
    UnsafeCommand,\
    VerticalSpace, HorizontalSpace, NewLine,\
    LongTable
from pylatex.base_classes import Environment, Arguments
from pylatex.utils import NoEscape, bold, italic
import funciones as fun

ROOT = Path(__file__).resolve().parent.parent
INPUTS = ROOT / "inputs"
MALLA_OUTPUTS = ROOT / "outputs" / "mallas"
MALLA_OUTPUTS.mkdir(parents=True, exist_ok=True)

cursos = pd.read_csv(INPUTS / "cursos" / "cursos_malla.csv",
    dtype = {'id':str,'codigo':str,'nombre':str,'area':str,'semestre':int,'fila':int,'horasTeoria':int,'horasPractica':int,'creditos':int})
cursos['sevesreq'] = cursos['creditos'] * 0.0
cursos['sevreq'] = cursos['creditos'] * 0.0


AREAS_OUTPUT = MALLA_OUTPUTS / "areas.csv"
if AREAS_OUTPUT.exists():
    areas = pd.read_csv(AREAS_OUTPUT)
else:
    from proc_areas import generar_areas
    areas = generar_areas().reset_index()

TRC = ["CIB","FPH","CYD","IEE","IMM","AUT","ADD"]
INS = ["CIB","FPH","CYD","IEE","IMM","AUT","ADD","INS"]
AER = ["CIB","FPH","CYD","IEE","IMM","AUT","ADD","AER"]
SCF = ["CIB","FPH","CYD","IEE","IMM","AUT","ADD","SCF"]

# black, blue, brown, cyan, darkgray, gray, green, lightgray, lime, magenta, olive, orange, pink, purple, red, teal, violet, white, yellow.

area_colors = {
    "ADD": "blue!20!white",
    "AER": "brown!20!white",
    "AUT": "cyan!20!white",
    "CIB": "green!20!white",
    "CYD": "magenta!20!white",
    "FPH": "olive!20!white",
    "IEE": "orange!20!white",
    "IMM": "red!20!white",
    "INS": "teal!20!white",
    "SCF": "violet!20!white"
}

MALLAS_INDIVIDUALES = (
    ("mallaTRC.pdf", 0),
    ("mallaINS.pdf", 1),
    ("mallaAER.pdf", 2),
    ("mallaCIB.pdf", 3),
)


def generar_mallas_individuales(pdf_completo):
    """Separa las cuatro páginas del PDF completo en archivos de una página."""
    reader = PdfReader(pdf_completo)
    if len(reader.pages) != len(MALLAS_INDIVIDUALES):
        raise RuntimeError(
            f"Se esperaban {len(MALLAS_INDIVIDUALES)} páginas en {pdf_completo.name}, "
            f"pero se encontraron {len(reader.pages)}."
        )
    for nombre, pagina in MALLAS_INDIVIDUALES:
        writer = PdfWriter()
        writer.add_page(reader.pages[pagina])
        with (MALLA_OUTPUTS / nombre).open("wb") as stream:
            writer.write(stream)

def generar_malla():
    #Geometría
    geometry_options = { 
        "left": "0mm",
        "right": "0mm",
        "top": "1mm",
        "bottom": "0mm",
        "headheight": "1mm",
        "footskip": "1mm"
    }
    #Opciones del documento
    doc = Document(documentclass="article", \
                   fontenc=None, \
                   inputenc=None, \
                   lmodern=False, \
                   textcomp=False, \
                   page_numbers=True, \
                   indent=False, \
                   document_options=["letterpaper","landscape"],
                   geometry_options=geometry_options)
    #Paquetes
    doc.packages.append(Package(name="fontspec", options=None))
    doc.packages.append(Package(name="babel", options=['spanish',"activeacute"]))
    doc.packages.append(Package(name="graphicx"))
    doc.packages.append(Package(name="tikz"))
    doc.packages.append(Package(name="anyfontsize"))
    doc.packages.append(Package(name="xcolor",options="dvipsnames"))
    doc.packages.append(Package(name="colortbl"))
    doc.packages.append(Package(name="array"))
    doc.packages.append(Package(name="float"))
    doc.packages.append(Package(name="longtable"))
    doc.packages.append(Package(name="multirow"))
    doc.packages.append(Package(name="fancyhdr"))
    doc.preamble.append(NoEscape(r'\usetikzlibrary{arrows.meta}'))
    #Bloques
    bloqueTitulo = NoEscape(
    r'''\tikzset{
            pics/titulo/.style args={#1,#2}{
            code={
                \def\ancho{57}
                \def\alto{0.7}
                \draw[fill=#2] (-\ancho/2-2,2*\alto) rectangle (\ancho/2+2,-2*\alto) node[midway,align=center,text width=45cm]{\fontsize{30pt}{0pt}\selectfont \textbf{#1}};
            }
        }
    }'''
    )
    bloqueCurso = NoEscape(
    r'''\tikzset{
            pics/curso/.style args={#1,#2,#3,#4,#5,#6}{
            code={
                \def\ancho{5}
                \def\alto{0.8}
                \draw[fill=#6] (-\ancho/2,\alto) rectangle (\ancho/2,-\alto) node[midway,align=center,text width=\ancho cm]{\fontsize{16pt}{2pt}\selectfont {#2}};
                \draw[fill=#6] (-\ancho/2,\alto) rectangle (\ancho/2,\alto + \alto) node[midway]{\fontsize{14pt}{14pt}\selectfont #1};
                \draw[fill=#6] (-\ancho/2,-\alto) rectangle (-\ancho/2 + \ancho/3, -\alto - \alto) node[midway]{\fontsize{14pt}{14pt}\selectfont #3};
                \draw[fill=#6] (-\ancho/2 + \ancho/3,-\alto) rectangle (-\ancho/2 + 2*\ancho/3, -\alto - \alto) node[midway]{\fontsize{14pt}{14pt}\selectfont #4};
                \draw[fill=#6] (-\ancho/2 + 2*\ancho/3,-\alto) rectangle (-\ancho/2 + 3*\ancho/3, -\alto - \alto) node[midway]{\fontsize{14pt}{14pt}\selectfont #5};
            }
        }
    }''' 
    #1: codigo, #2: nombre, #3: horasteoria, #4: horaspractica, #5: creditos, #6: color
    )
    bloqueSemestre = NoEscape(
    r'''\tikzset{
            pics/semestre/.style args={#1,#2,#3,#4,#5}{
            code={
                \def\ancho{6}
                \def\alto{0.8}
                \draw[fill=#2] (-\ancho/2,1.5*\alto) rectangle (\ancho/2,-1.5*\alto) node[midway,align=center,text width=\ancho cm]{\fontsize{16pt}{12pt}\selectfont \textbf{#1}};
                \draw[fill=#2] (-\ancho/2,-\alto) rectangle (-\ancho/2 + \ancho/3, -\alto - \alto) node[midway]{\fontsize{12pt}{14pt}\selectfont #3};
                \draw[fill=#2] (-\ancho/2 + \ancho/3,-\alto) rectangle (-\ancho/2 + 2*\ancho/3, -\alto - \alto) node[midway]{\fontsize{12pt}{14pt}\selectfont #4};
                \draw[fill=#2] (-\ancho/2 + 2*\ancho/3,-\alto) rectangle (-\ancho/2 + 3*\ancho/3, -\alto - \alto) node[midway]{\fontsize{12pt}{14pt}\selectfont #5};
            }
        }
    }'''
    #1: semestre, #2: color, #3: horasteoria, #4: horaspractica, #5: creditos
    )
    
    doc.preamble.append(bloqueTitulo)        
    doc.preamble.append(bloqueCurso)
    doc.preamble.append(bloqueSemestre)

    doc.append(Command('centering'))
    sesgo = 0
    rango = range(0,9)
    with doc.create(TikZ(
            options=TikZOptions
                (    
                "scale = 0.45",
                "transform shape"
                )
        )) as malla_TRC:
        titulo = "Tronco común de Licenciatura en Ingeniería Electromecánica y salida lateral de Bachillerato en Ingeniería Electromecánica"
        fun.malla_enf(malla_TRC,cursos,sesgo,TRC,"TRC",area_colors,titulo,rango,False)
    doc.append(NoEscape(r"\newpage"))
    sesgo = 7
    rango = range(7,11)
    with doc.create(TikZ(
            options=TikZOptions
                (    
                "scale = 0.45",
                "transform shape"
                )
        )) as malla_INS:
        titulo = "Licenciatura en Ingeniería Electromecánica con énfasis en Instalaciones Electromecánicas"
        fun.malla_enf(malla_INS,cursos,sesgo,INS,"INS",area_colors,titulo,rango,True)
    doc.append(NoEscape(r"\newpage"))
    with doc.create(TikZ(
            options=TikZOptions
                (    
                "scale = 0.45",
                "transform shape"
                )
        )) as malla_AER:
        titulo = "Licenciatura en Ingeniería Electromecánica con énfasis en Aeronáutica"
        fun.malla_enf(malla_AER,cursos,sesgo,AER,"AER",area_colors,titulo,rango,True)
    doc.append(NoEscape(r"\newpage"))
    with doc.create(TikZ(
            options=TikZOptions
                (    
                "scale = 0.45",
                "transform shape"
                )
        )) as malla_SCF:
        titulo = "Licenciatura en Ingeniería Electromecánica con énfasis en Sistemas Ciberfísicos"
        fun.malla_enf(malla_SCF,cursos,sesgo,SCF,"SCF",area_colors,titulo,rango,True)
    output_base = MALLA_OUTPUTS / "malla"
    doc.generate_pdf(str(output_base), clean=True, clean_tex=False, compiler='lualatex',silent=True)
    generar_mallas_individuales(output_base.with_suffix(".pdf"))
    


datos_malla = pd.DataFrame()
cursos_malla = cursos[cursos["semestre"]<=10]
datos_malla["cred_TRC"] = cursos_malla.groupby("area")["creditos"].sum(numeric_only=True)
datos_malla.loc[["INS","AER","SCF"],"cred_TRC"] = 0
datos_malla["pt_TRC"] = areas["porcTRC"].to_list()[:-2]
datos_malla["pm_TRC"] = round((datos_malla["cred_TRC"] / datos_malla["cred_TRC"].sum())*100,1)
datos_malla["cred_INS"] = cursos_malla.groupby("area")["creditos"].sum(numeric_only=True)
datos_malla.loc[["AER","SCF"],"cred_INS"] = 0
datos_malla["pt_INS"] = areas["porcINS"].to_list()[:-2]
datos_malla["pm_INS"] = round(((datos_malla["cred_INS"]/180)*100),1)
datos_malla["cred_AER"] = cursos_malla.groupby("area")["creditos"].sum(numeric_only=True)
datos_malla.loc[["INS","SCF"],"cred_AER"] = 0
datos_malla["pt_AER"] = areas["porcAER"].to_list()[:-2]
datos_malla["pm_AER"] = round(((datos_malla["cred_AER"]/180)*100),1)
datos_malla["cred_SCF"] = cursos_malla.groupby("area")["creditos"].sum(numeric_only=True)
datos_malla.loc[["AER","INS"],"cred_SCF"] = 0
datos_malla["pt_SCF"] = areas["porcSCF"].to_list()[:-2]
datos_malla["pm_SCF"] = round(((datos_malla["cred_SCF"]/180)*100),1)
datos_malla.loc["TOT"] = datos_malla.sum(numeric_only=True)
datos_malla.to_csv(MALLA_OUTPUTS / 'datos_malla.csv')
print(datos_malla)

generar_malla()
