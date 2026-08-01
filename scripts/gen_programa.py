"""Genera en PDF los programas de curso a partir de los CSV curriculares y datos docentes externos."""

import subprocess
import argparse
from pathlib import Path
import pandas as pd
from pylatex import Document, Package, Command, PageStyle, Head, Foot, NewPage, NewLine,\
    TextColor, MiniPage, StandAloneGraphic, simple_page_number,\
    TikZ, TikZNode, TikZOptions, TikZCoordinate,\
    VerticalSpace, HorizontalSpace,\
    LongTabularx, Tabularx,\
    config
from pylatex.base_classes import Arguments
from pylatex.utils import NoEscape, bold
import funciones as fun

ROOT = Path(__file__).resolve().parent.parent
INPUTS = ROOT / "inputs"
COURSE_INPUTS = INPUTS / "cursos"
PROGRAM_OUTPUTS = ROOT / "outputs" / "programas"
PROGRAM_OUTPUTS.mkdir(parents=True, exist_ok=True)

cursos = pd.read_csv(COURSE_INPUTS / "cursos_malla.csv")
detall = pd.read_csv(COURSE_INPUTS / "cursos_detalles.csv")
progra = pd.read_csv(COURSE_INPUTS / "cursos_programas.csv")
objeti = pd.read_csv(COURSE_INPUTS / "cursos_obj.csv")
conten = pd.read_csv(COURSE_INPUTS / "cursos_conten.csv")
metodo = pd.read_csv(COURSE_INPUTS / "cursos_metodo.csv")
metdes = pd.read_csv(COURSE_INPUTS / "descri_metodo.csv")
evalua = pd.read_csv(COURSE_INPUTS / "cursos_evalua.csv")
evades = pd.read_csv(COURSE_INPUTS / "descri_evalua.csv")
evatip = pd.read_csv(COURSE_INPUTS / "tipos_evalua.csv")
bibtex = pd.read_csv(COURSE_INPUTS / "cursos_bibtex.csv")
rasgos = pd.read_csv(INPUTS / "saberes" / "rasgos.csv")
profes = pd.read_csv(COURSE_INPUTS / "cursos_profes.csv")
datpro = pd.read_csv("https://raw.githubusercontent.com/EIEM-TEC/profes/refs/heads/main/00_datos.csv")
grapro = pd.read_csv("https://raw.githubusercontent.com/EIEM-TEC/profes/refs/heads/main/01_grados.csv")
TRClist = ["ADD","AUT","CIB","CYD","FPH","IEE","IMM"]


rasgos["codSaber"] = rasgos["codSaber"].str.split(';', expand=False) #convertir los valores separados por ; en una lista por fila
rasgos = rasgos.explode("codSaber") #expadir la lista
curras = pd.read_csv(COURSE_INPUTS / "cursos_rasgos.csv")
curras["codSaber"] = curras["codSaber"].str.split(';', expand=False) #convertir los valores separados por ; en una lista por fila
curcur = pd.read_csv(COURSE_INPUTS / "cursos_cursos.csv")
curAntes = pd.DataFrame()
curAntes = curcur[["id","antes"]].copy()
curAntes["antes"] = curAntes["antes"].str.split(';', expand=False) #convertir los valores separados por ; en una lista por fila
curAntes = curAntes.explode("antes")
curDespues = pd.DataFrame()
curDespues = curcur[["id","despues"]].copy()
curDespues["despues"] = curDespues["despues"].str.split(';', expand=False)#convertir los valores separados por ; en una lista por fila
curDespues = curDespues.explode("despues")

tipCursoDic = {
    0: "Teórico",
    1: "Práctico",
    2: "Teórico - Práctico"
}

eleCursoDic = {
    0: "Obligatorio",
    1: "Electivo"
}

tipAsistDic = {
    0: "Libre",
    1: "Obligatoria" 
}

sinoDic = {
    0: "No",
    1: "Sí" 
}


def textcolor(size,vspace,color,bold,text,hspace="0",par=True):
    dump = NoEscape(r"")
    if par==True:
        dump = NoEscape(r"\par")
    if hspace!="0":
        dump += NoEscape(HorizontalSpace(hspace,star=True).dumps())
    dump += NoEscape(Command("fontsize",arguments=Arguments(size,vspace)).dumps())
    dump += NoEscape(Command("selectfont").dumps()) + NoEscape(" ")
    if bold==True:
        dump += NoEscape(Command("textbf", NoEscape(Command("textcolor",arguments=Arguments(color,text)).dumps())).dumps())
    else:
        dump += NoEscape(Command("textcolor",arguments=Arguments(color,text)).dumps())
    return dump

def fontselect(size,vspace):
    dump = NoEscape(r"")
    dump += NoEscape(Command("fontsize",arguments=Arguments(size,vspace)).dumps())
    dump += NoEscape(Command("selectfont").dumps()) + NoEscape(" ")
    return dump


def validate_program_data(course_ids):
    """Comprueba que cada curso tenga los insumos necesarios antes de generar PDF."""
    valid_course_ids = set(cursos["id"].dropna())

    def missing_references(value):
        if pd.isna(value):
            return []
        references = [reference.strip() for reference in str(value).split(";") if reference.strip()]
        return [reference for reference in references if reference not in valid_course_ids]

    single_row_sources = {
        "cursos_malla.csv": cursos,
        "cursos_detalles.csv": detall,
        "cursos_programas.csv": progra,
        "cursos_conten.csv": conten,
        "cursos_evalua.csv": evalua,
        "cursos_bibtex.csv": bibtex,
        "cursos_profes.csv": profes,
        "cursos_cursos.csv": curcur,
    }
    multiple_row_sources = {
        "cursos_obj.csv": objeti,
        "cursos_metodo.csv": metodo,
    }
    issues = []
    for course_id in course_ids:
        for source_name, data in single_row_sources.items():
            row_count = int((data["id"] == course_id).sum())
            if row_count != 1:
                issues.append(f"{course_id}: {source_name} tiene {row_count} filas; se esperaba 1")
        for source_name, data in multiple_row_sources.items():
            row_count = int((data["id"] == course_id).sum())
            if row_count == 0:
                issues.append(f"{course_id}: no tiene datos en {source_name}")

        course_rows = cursos[cursos["id"] == course_id]
        if len(course_rows) == 1:
            course_row = course_rows.iloc[0]
            if int(course_row["propio"]) != 1:
                issues.append(f"{course_id}: no está marcado como curso propio en cursos_malla.csv")
            for column_name in ("requisitos", "correquisitos", "esrequisito"):
                missing = missing_references(course_row[column_name])
                if missing:
                    issues.append(
                        f"{course_id}: {column_name} contiene identificadores inexistentes: "
                        + ", ".join(missing)
                    )
            if int(course_row["semestre"]) <= 10:
                trait_count = int((curras["id"] == course_id).sum())
                if trait_count != 1:
                    issues.append(
                        f"{course_id}: cursos_rasgos.csv tiene {trait_count} filas; se esperaba 1"
                    )

        relation_rows = curcur[curcur["id"] == course_id]
        if len(relation_rows) == 1:
            relation_row = relation_rows.iloc[0]
            for column_name in ("antes", "despues"):
                missing = missing_references(relation_row[column_name])
                if missing:
                    issues.append(
                        f"{course_id}: cursos_cursos.csv/{column_name} contiene "
                        f"identificadores inexistentes: {', '.join(missing)}"
                    )
    return issues

def generar_programa(id):
    professor_value = profes.loc[profes.id == id, "profesores"].item()
    listProf = [] if pd.isna(professor_value) else professor_value.split(';')
    codCurso = cursos[cursos.id == id].codigo.item()
    areCurso = cursos[cursos.id == id].area.item()
    nomEscue = "Escuela de Ingeniería Electromecánica"
    lisProgr = progra[progra.id == id].drop('id',axis=1)
    numProgr = len(lisProgr.programa)
    counter = 0
    if numProgr > 1:
        strProgr = "Carreras de: "
    else:
        strProgr = "Carrera de "
    for programa in lisProgr.programa:
        counter += 1
        strProgr += programa
        if counter < numProgr:
            if numProgr == 2:
                strProgr += " y "
            else:
                strProgr += ", "  
    nomCurso = cursos[cursos.id == id].nombre.item()
    print(f'Curso: {nomCurso}')
    tipo = detall[detall.id == id].tipo.item()
    tipCurso = tipCursoDic.get(detall[detall.id == id].tipo.item())
    eleCurso = eleCursoDic.get(detall[detall.id == id].electivo.item())
    numCredi = cursos[cursos.id == id].creditos.item()
    horClass = cursos[cursos.id == id].horasTeoria.item() + cursos[cursos.id == id].horasPractica.item()
    horExtra = (numCredi * 3) - horClass
    semCurso = cursos[cursos.id == id].semestre.item()
    ubiPlane = ""
    counter = 0
    for programa in lisProgr.programa:
        counter +=1
        semestre = lisProgr[lisProgr['programa'] == programa].semestre.item()
        if semestre <= 10:
            ubiPlane += "Curso de " + fun.number_to_ordinals(str(int(semestre))) + " semestre en " + programa
        elif semestre > 10:
            ubiPlane += "Curso electivo en " + programa
        if counter > 1:
            ubiPlane += " "
    susRequi = ""
    lisRequi = cursos[cursos.id == id].requisitos.item()
    if str(lisRequi) != "nan":
        lisRequi = cursos[cursos.id == id].requisitos.str.split(';').explode().reset_index(drop=True)
        numRequi = len(lisRequi)
        counter = 0
        for requisito in lisRequi:
            counter += 1
            susRequi += cursos[cursos.id == requisito].codigo.item()[:2] + "-" + cursos[cursos.id == requisito].codigo.item()[2:]
            susRequi += " "
            susRequi += cursos[cursos.id == requisito].nombre.item()
            if counter < numRequi:
                susRequi += "; "
            else:
                susRequi += " "
    else:
        susRequi += "Ninguno"
    corRequi = ""
    lisCorre = cursos[cursos.id == id].correquisitos.item()
    if str(lisCorre) != "nan":
        lisCorre = cursos[cursos.id == id].correquisitos.str.split(';').explode().reset_index(drop=True)
        numCorre = len(lisCorre)
        counter = 0
        for correquisito in lisCorre:
            counter += 1
            corRequi += cursos[cursos.id == correquisito].codigo.item()[:2] + "-" + cursos[cursos.id == correquisito].codigo.item()[2:]
            corRequi += " "
            corRequi += cursos[cursos.id == correquisito].nombre.item()
            if counter < numCorre:
                corRequi += "; "
            else:  
                corRequi += " "
    else:
        corRequi += "Ninguno"
    essRequi = NoEscape("")
    lisEsreq = cursos[cursos.id == id].esrequisito.item()
    if str(lisEsreq) != "nan":
        lisEsreq = cursos[cursos.id == id].esrequisito.str.split(';').explode().reset_index(drop=True)
        cTRC = 0
        trcRequi = ""
        cINS = 0
        insRequi = ""
        cAER = 0
        aerRequi = ""
        cSCF = 0
        scfRequi = ""
        for esrequisito in lisEsreq:      
            areaEsreq = cursos[cursos.id == esrequisito].area.item()
            if (areaEsreq not in ["INS","AER","SCF"]):
                if cTRC != 0:
                    trcRequi += "; "
                trcRequi += cursos[cursos.id == esrequisito].codigo.item()[:2] + "-" + cursos[cursos.id == esrequisito].codigo.item()[2:]
                trcRequi += " "
                trcRequi += cursos[cursos.id == esrequisito].nombre.item()
                cTRC += 1  
        for esrequisito in lisEsreq:      
            areaEsreq = cursos[cursos.id == esrequisito].area.item()        
            if areaEsreq == "INS":   
                if cINS == 0:
                    if cTRC != 0:                        
                        insRequi += ". "
                    insRequi += r"\emph{Énfasis en Instalaciones Electromecánicas:} "
                else:
                    insRequi += "; "  
                insRequi += cursos[cursos.id == esrequisito].codigo.item()[:2] + "-" + cursos[cursos.id == esrequisito].codigo.item()[2:]
                insRequi += " "
                insRequi += cursos[cursos.id == esrequisito].nombre.item()
                cINS += 1
            elif areaEsreq == "AER":
                if cAER == 0:
                    if cTRC != 0:
                       aerRequi += ". "
                    aerRequi += r"\emph{Énfasis en Aeronáutica:} "
                else:
                    aerRequi += "; " 
                aerRequi += cursos[cursos.id == esrequisito].codigo.item()[:2] + "-" + cursos[cursos.id == esrequisito].codigo.item()[2:]
                aerRequi += " "
                aerRequi += cursos[cursos.id == esrequisito].nombre.item()             
                cAER += 1
            elif areaEsreq == "SCF":
                if cSCF == 0:
                    if cTRC != 0:
                       scfRequi += ". "
                    scfRequi += r"\emph{Énfasis en Sistemas Ciberfísicos:} "
                else:
                    scfRequi += "; "
                scfRequi += cursos[cursos.id == esrequisito].codigo.item()[:2] + "-" + cursos[cursos.id == esrequisito].codigo.item()[2:]
                scfRequi += " "
                scfRequi += cursos[cursos.id == esrequisito].nombre.item()
                cSCF += 1
        essRequi = NoEscape(trcRequi) + NoEscape(insRequi) + NoEscape(aerRequi) + NoEscape(scfRequi)
    else:
        essRequi += NoEscape("Ninguno")
    tipAsist = tipAsistDic.get(detall[detall.id == id].asistencia.item())
    posSufic = sinoDic.get(detall[detall.id == id].suficiencia.item())
    posRecon = sinoDic.get(detall[detall.id == id].reconocimiento.item())
    aprCurso = detall[detall.id == id].aprobacion.str.split(';').explode().reset_index(drop=True)
    aprCurso = aprCurso[0] + "/" + aprCurso[1] + "/" + aprCurso[2] + " en sesión de Consejo de Escuela " + aprCurso[3]
    if semCurso <= 10:
        codSaber = curras[curras["id"]==id]["codSaber"].item()
        codRasgos = rasgos[rasgos["codSaber"].isin(codSaber)]["rasgo"].unique()
        desGener = NoEscape(r"El curso de " + r"\emph{" + f"{nomCurso}" + r"}" + r" aporta en el desarrollo ")
        if len(codRasgos) > 1:
            desGener += NoEscape(r"de los siguientes rasgos del plan de estudios: ")
        else:
            desGener += NoEscape(r"del siguiente rasgo del plan de estudios: ")
        for index, rasgo in enumerate(codRasgos):
            desGener += NoEscape(f"{rasgo[0].lower() + rasgo[1:]}")
            if index == len(codRasgos) - 2:
                desGener += NoEscape(f"; y ")
            elif index < len(codRasgos) - 2:
                desGener += NoEscape(f"; ")
    else:
        codSaber = ""
        codRasgos = ""
        desGener = NoEscape(r"El curso de " + r"\emph{" + f"{nomCurso}" + r"}" + r" es del tipo electivo y por esta razón no se incluye en los rasgos del plan de estudios")
    desGener += NoEscape(r". \newline\newline ")
    desGener += NoEscape(r"Los aprendizajes que los estudiantes desarrollarán en el curso son: ")
    lisObjet = objeti[objeti.id == id].reset_index(drop=True).objetivo
    for index, objetivo in lisObjet.items():
        if index > 0:
            if (index == len(lisObjet) - 1):
                if (objetivo[0].lower() == "i"):
                    desGener += NoEscape(f"e ")
                else:
                    desGener += NoEscape(f"y ")
            desGener += NoEscape(f"{objetivo[0].lower() + objetivo[1:]}")
            if index <= len(lisObjet) - 2:
                desGener += NoEscape(f"; ")
    desGener += NoEscape(r". \newline\newline ")
    curAntess = curAntes[curAntes["id"]==id]["antes"]
    if codCurso not in ["EE0108"]:
        desGener += NoEscape(r"Para desempeñarse adecuadamente en este curso, los estudiantes deben poner en práctica lo aprendido en ")
        if len(curAntess) > 1:
            desGener += NoEscape(r"los cursos de: ")
        else:
            desGener += NoEscape(r"el curso de: ")
        for index, curAnte in enumerate(curAntess):
            cursoAntes = cursos[cursos["id"]==curAnte].nombre.item()
            if index != 0:
                if index == len(curAntess) - 1:
                    if cursoAntes[0].lower() == "i":
                        desGener += NoEscape(f", e ")
                    else:
                        desGener += NoEscape(f", y ")                
                elif index < len(curAntess) - 1:
                    desGener += NoEscape(f", ")
            desGener += NoEscape(cursoAntes)
        desGener += NoEscape(r".")
    if int(id[3:5]) < 10:
        curDespuess = curDespues[curDespues["id"]==id]["despues"]
        desGener += NoEscape(r" \newline\newline Una vez aprobado este curso, los estudiantes podrán emplear algunos de los aprendizajes adquiridos en ")
        if len(curDespuess) > 1:
            desGener += NoEscape(r"los cursos de: ")
        else:
            desGener += NoEscape(r"el curso de: ")
        for index, curDespue in enumerate(curDespuess):
            cursoDespues = cursos[cursos["id"]==curDespue].nombre.item()
            if index != 0:
                if index == len(curDespuess) - 1:
                    if cursoDespues[0].lower() == "i":
                        desGener += NoEscape(f", e ")
                    else:
                        desGener += NoEscape(f", y ")
                elif index < len(curDespuess) - 1:
                    desGener += NoEscape(f", ")
            desGener += NoEscape(cursoDespues)
        desGener += NoEscape(r". ")
    for consecutivo, objetivo in lisObjet.items():
        if consecutivo == 0:
            objGener = NoEscape(objetivo)
            objEspec = NoEscape(r"\begin{itemize}")
        else:
            objEspec += NoEscape(r"\item ") + NoEscape(objetivo) + NoEscape(r".")
    objEspec += NoEscape(r"\end{itemize}")
    objCurso = NoEscape(r"Al final del curso la persona estudiante será capaz de:") 
    objCurso += NoEscape(r"\newline\newline ")
    objCurso += NoEscape(Command("textbf", "Objetivo general").dumps())
    objCurso += NoEscape(r"\begin{itemize}\item ")
    objCurso += objGener + NoEscape(r".")
    objCurso += NoEscape(r"\end{itemize} \vspace{2mm}")
    objCurso += NoEscape(Command("textbf", "Objetivos específicos").dumps())
    objCurso += objEspec
    if tipo == 1:
        if codCurso not in ["EE9001","EE1102"]:
            conDescr = "En el curso se desarrollaran los siguientes laboratorios:"
        else:
            conDescr = "En el curso se desarrollarán los siguientes temas:"
    else:
        conDescr = "En el curso se desarrollaran los siguientes temas:"
    conCurso = NoEscape(r"\par \setlength{\leftskip}{4cm} ")
    conCurso += NoEscape(r"\begin{easylist} \ListProperties(Progressive*=3ex)")
    conCurso += NoEscape(conten[conten.id == id].contenidos.item())
    conCurso += NoEscape(r"\end{easylist} ")
    conCurso += NoEscape(r"\setlength{\leftskip}{0cm} ")
    lisMetod = metodo[metodo.id == id].reset_index(drop=True).metodologia
    for consecutivo, metodos in lisMetod.items():
        if consecutivo == 0:
            metGener = NoEscape(metdes[metdes["tipo"]==tipo].descripcion.item())
            metEspec = NoEscape(r"\begin{itemize}")
            metEspec += NoEscape(r"\item ") + NoEscape(metodos)
        else:
            metEspec += NoEscape(r"\item ") + NoEscape(metodos)
    metEspec += NoEscape(r"\end{itemize}")
    metCurso = metGener
    metCurso += NoEscape(r"\newline\newline ")
    metCurso += NoEscape(Command("textbf", "Las personas estudiantes podrán desarrollar actividades en las que:").dumps() + r" \newline")
    metCurso += metEspec
    metCurso += NoEscape(r"\vspace*{2mm}")
    metCurso += NoEscape(f"Este enfoque metodológico permitirá a la persona estudiante {objGener[0].lower() + objGener[1:]}")
    metCurso += NoEscape(r"\vspace*{2mm} \newline  ")
    metCurso += NoEscape(r"Si un estudiante requiere apoyos educativos, podrá solicitarlos a través del Departamento de Orientación y Psicología. \newline ")
    evaCurso = NoEscape(r"La evaluación se distribuye en los siguientes rubros:")
    evaCurso += NoEscape(r" \newline ")
    tipEvalu = evalua[evalua.id == id].tipoEval.item()
    lisEvalu = evatip[(evatip.tipo == tipo) & (evatip.tipoEval == tipEvalu)].reset_index(drop=True)
    for consecutivo, evaluas in lisEvalu.iterrows():
        if consecutivo == 0:
            descriEval = NoEscape(r"\begin{itemize} ")  
        descriEval += NoEscape(r"\item ") + NoEscape(f"{evaluas.evaluacion}: {evades[evades["evaluacion"]==evaluas.evaluacion].descripcion.item()}")  
    descriEval += NoEscape(r"\end{itemize}") 
    evaCurso += descriEval
    evaTabla = NoEscape(r" \begin{minipage}{\linewidth} ")
    evaTabla += NoEscape(r" \centering ") 
    evaTabla += NoEscape(r" \begin{tabular}{ p{4.5cm}  p{1.5cm} } ")
    evaTabla += NoEscape(r" \toprule ") 
    total = 0
    for consecutivo, evaluas in lisEvalu.iterrows():
        evaTabla += NoEscape(f" {evaluas.evaluacion} ({evaluas.cantidad}) & {evaluas.porcentaje} \\%") + NoEscape(r" \\ ")
        evaTabla += NoEscape(r" \midrule ")
        total += evaluas.porcentaje
        if consecutivo == len(lisEvalu)-1:
            evaTabla += NoEscape(f"Total & {total} \\%") + NoEscape(r" \\ ")
            evaTabla += NoEscape(r" \bottomrule ")
    evaTabla += NoEscape(r" \end{tabular} \end{minipage}")
    evaRepo = NoEscape(r"De conformidad con el artículo 78 del Reglamento del Régimen Enseñanza-Aprendizaje del Instituto Tecnológico de Costa Rica y sus Reformas, en este curso la persona estudiante ")
    if tipCurso != "Teórico":
        evaRepo += NoEscape(Command("textbf", "no").dumps())
    evaRepo += NoEscape(r" tiene derecho a presentar un examen de reposición")
    if tipCurso == "Teórico":
        evaRepo += NoEscape(r" si su nota luego de redondeo es 60 o 65.")
    else:
        evaRepo += NoEscape(r".")
    bibCurso = NoEscape(r'\nocite{' + ('} '+r'\nocite{').join(bibtex[bibtex.id == id].bibtex.item().split(';')) + '} ')
    bibPrint = NoEscape(r'\vspace*{-8mm}\printbibliography[heading=none]')
    dataProf = datpro[datpro.codigo.isin(listProf)]
    proImpar = NoEscape(r"El curso será impartido por:")
    proCurso = NoEscape(r'\vspace*{-4mm}\begin{textoMargen}')
    for consecutivo, profe in dataProf.iterrows():
        print(f'Profesor: {profe.nombre}')
        match profe.titulo:
            case "M.Sc." | "Lic." | "Máster" | "Dr.-Ing." | "Mag.":
                proCurso += NoEscape(Command("textbf", f"{profe.titulo} {profe.nombre}").dumps())
            case "Ph.D.":
                proCurso += NoEscape(Command("textbf", f"{profe.nombre}, {profe.titulo}").dumps())
        proCurso += NoEscape(r" \newline ")
        gradProf = grapro[grapro.codigo == profe.codigo]
        for consecutivo, grado in gradProf.iterrows():
            proCurso += NoEscape(Command("textbf", f"{grado.grado} en {grado.campo}, {grado.institucion}, {grado.pais}").dumps())
            proCurso += NoEscape(r" \newline \newline ") 
        proCurso += NoEscape(Command("emph", "Correo:").dumps())               
        proCurso += NoEscape(f" {profe.correo}")
        proCurso += NoEscape(Command("emph", "  Teléfono:").dumps())     
        proCurso += NoEscape(f" {int(profe.telefono)}")
        proCurso += NoEscape(r" \vspace*{1mm} \newline ")
        proCurso += NoEscape(Command("emph", "  Oficina:").dumps())    
        proCurso += NoEscape(f" {int(profe.oficina)}")
        proCurso += NoEscape(Command("emph", "  Escuela:").dumps())  
        proCurso += NoEscape(f" {profe.escuela}")
        proCurso += NoEscape(Command("emph", "  Sede:").dumps())  
        proCurso += NoEscape(f" {profe.sede}")
        proCurso += NoEscape(r" \vspace*{4mm} \newline ")             
    proCurso += NoEscape(r"\end{textoMargen}")
    #Config
    config.active = config.Version1(row_heigth=1.5)
    #Geometry
    geometry_options = { 
        "left": "22.5mm",
        "right": "16.1mm",
        "top": "48mm",
        "bottom": "25mm",
        "headheight": "12.5mm",
        "footskip": "12.5mm"
    }
    #Document options
    doc = Document(documentclass="article", \
                   fontenc=None, \
                   inputenc=None, \
                   lmodern=False, \
                   textcomp=False, \
                   page_numbers=True, \
                   indent=False, \
                   document_options=["letterpaper"],
                   geometry_options=geometry_options)
    #Packages
    doc.packages.append(Package(name="fontspec", options=None))
    doc.packages.append(Package(name="babel", options=['spanish','activeacute']))
    doc.packages.append(Package(name="anyfontsize"))
    doc.packages.append(Package(name="fancyhdr"))
    doc.packages.append(Package(name="csquotes"))
    doc.packages.append(Package(name="easylist", options=['ampersand']))
    doc.packages.append(Package(name="biblatex", options=['style=ieee','backend=biber']))
    doc.packages.append(Package(name="tcolorbox",options=['skins','breakable']))
    doc.packages.append(Package(name="booktabs"))
    #Package options
    doc.preamble.append(Command('setmainfont','Arial'))
    doc.preamble.append(Command('addbibresource', '../../inputs/bibliografias/bibFPH.bib'))
    doc.preamble.append(Command('addbibresource', '../../inputs/bibliografias/bibADD.bib'))
    doc.preamble.append(Command('addbibresource', '../../inputs/bibliografias/bibAUT.bib'))
    doc.preamble.append(Command('addbibresource', '../../inputs/bibliografias/bibCYD.bib'))
    doc.preamble.append(Command('addbibresource', '../../inputs/bibliografias/bibIEE.bib'))
    doc.preamble.append(Command('addbibresource', '../../inputs/bibliografias/bibIMM.bib'))
    doc.preamble.append(Command('addbibresource', '../../inputs/bibliografias/bibINS.bib'))
    doc.preamble.append(Command('addbibresource', '../../inputs/bibliografias/bibAER.bib'))
    doc.preamble.append(Command('addbibresource', '../../inputs/bibliografias/bibSCF.bib'))
    doc.preamble.append(NoEscape(r'\renewcommand*{\bibfont}{\fontsize{10}{14}\selectfont}'))
    doc.preamble.append(NoEscape(r'''
\defbibenvironment{bibliography}
    {\list
    {\printfield[labelnumberwidth]{labelnumber}}
    {\setlength{\leftmargin}{4cm}
    \setlength{\rightmargin}{1.1cm}
    \setlength{\itemindent}{0pt}
    \setlength{\itemsep}{\bibitemsep}
    \setlength{\parsep}{\bibparsep}}}
    {\endlist}
{\item}
'''))
    doc.preamble.append(NoEscape(r'''
\newenvironment{textoMargen}
    {%
    \begin{list}{}{%
        \setlength{\leftmargin}{3.6cm}%
        \setlength{\rightmargin}{1.1cm}%
    }%
    \item[]%
  }
  {%
    \end{list}%
  }
'''))
    doc.add_color('gris','rgb','0.27,0.27,0.27') #70,70,70
    doc.add_color('parte','rgb','0.02,0.204,0.404') #5,52,103
    doc.add_color('azulsuaveTEC','rgb','0.02,0.455,0.773') #5,116,197
    doc.add_color('fila','rgb','0.929,0.929,0.929') #237,237,237
    doc.add_color('linea','rgb','0.749,0.749,0.749') #191,191,191

    headerfooter = PageStyle("headfoot")

    #Left header
    with headerfooter.create(Head("L")) as header_left:
        with header_left.create(MiniPage(width=r"0.5\textwidth",align="l")) as logobox:
            logobox.append(StandAloneGraphic(image_options="width=62.5mm", filename='../../inputs/figuras/Logo.png'))
    #Right foot
    with headerfooter.create(Foot("R")) as footer_right:
        footer_right.append(TextColor("black", NoEscape(r"Página \thepage \hspace{1pt} de \pageref*{LastPage}")))        
    #Add header and footer 
    doc.preamble.append(headerfooter)
    doc.change_page_style("empty")
    #Set logo in first page
    with doc.create(TikZ(
            options=TikZOptions
                (    
                "overlay",
                "remember picture"
                )
        )) as logo:
        logo.append(TikZNode(\
            options=TikZOptions
                (
                "inner sep = 0mm",
                "outer sep = 0mm",
                "anchor = north west",
                "xshift = -23mm",
                "yshift = 22mm"
                ),
            text=StandAloneGraphic(image_options="width=21cm", filename='../../inputs/figuras/Logo_portada.png').dumps(),\
            at=TikZCoordinate(0,0)
        ))
    doc.append(VerticalSpace("100mm", star=True))
    doc.append(textcolor
            (   
            size="14",
            vspace="0",
            color="black",
            bold=False,
            text=f"Programa del curso {str(codCurso)[:2]}-{str(codCurso)[2:]}"
            ))
    doc.append(textcolor
            (
            size="18",
            vspace="25",
            color="black",
            bold=True,
            text=f"{nomCurso}" 
            ))
    doc.append(VerticalSpace("15mm", star=True))
    doc.append(NewLine())
    with doc.create(Tabularx(table_spec=r"m{0.02\textwidth}m{0.98\textwidth}")) as table:
            table.add_row(["", textcolor
            (   
            par=False,
            hspace="0mm",
            size="12",
            vspace="0",
            color="gris",
            bold=True,
            text=f"{nomEscue}"
            )])
            table.append(NoEscape('[-12pt]'))
            table.add_row(["", textcolor
            (   
            par=False,
            hspace="0mm",
            size="12",
            vspace="0",
            color="gris",
            bold=True,
            text=f"{strProgr}" 
            )])
    doc.append(NewPage())
    doc.change_document_style("headfoot")
    doc.append(textcolor
            (   
            size="14",
            vspace="0",
            color="parte",
            bold=True,
            text="I parte: Aspectos relativos al plan de estudios"
            ))
    doc.append(textcolor
            (   
            hspace="2mm",
            size="12",
            vspace="14",
            color="parte",
            bold=True,
            text="1. Datos generales"
            ))
    doc.append(VerticalSpace("3mm", star=True))
    doc.append(NewLine())
    doc.append(fontselect
            (
            size="10",
            vspace="12"      
            ))
    with doc.create(Tabularx(table_spec=r"p{6cm}p{10cm}")) as table:
            table.add_row([bold("Nombre del curso:"), f"{nomCurso}"])
            table.append(NoEscape('[10pt]'))
            table.add_row([bold("Código:"), f"{str(codCurso)[:2]}-{str(codCurso)[2:]}"])
            table.append(NoEscape('[10pt]'))
            table.add_row([bold("Tipo de curso:"), f"{tipCurso}"])
            table.append(NoEscape('[10pt]'))
            table.add_row([bold("Obligatorio o electivo:"), f"{eleCurso}"])
            table.append(NoEscape('[10pt]'))
            table.add_row([bold("Nº de créditos:"), f"{numCredi}"])
            table.append(NoEscape('[10pt]'))
            table.add_row([bold("Nº horas de clase por semana:"), f"{horClass}"])
            table.append(NoEscape('[10pt]'))
            table.add_row([bold("Nº horas extraclase por semana:"), f"{horExtra}"])
            table.append(NoEscape('[10pt]'))
            table.add_row([bold("Ubicación en el plan de estudios:"), NoEscape(f"{ubiPlane}")])
            table.append(NoEscape('[10pt]'))
            table.add_row([bold("Requisitos:"), f"{susRequi}"])
            table.append(NoEscape('[10pt]'))
            table.add_row([bold("Correquisitos:"), f"{corRequi}"])
            table.append(NoEscape('[10pt]'))
            table.add_row([bold("El curso es requisito de:"), NoEscape(f"{essRequi}")])
            table.append(NoEscape('[10pt]'))
            table.add_row([bold("Asistencia:"), f"{tipAsist}"])
            table.append(NoEscape('[10pt]'))
            table.add_row([bold("Suficiencia:"), f"{posSufic}"])
            table.append(NoEscape('[10pt]'))
            table.add_row([bold("Posibilidad de reconocimiento:"), f"{posRecon}"])
            table.append(NoEscape('[10pt]'))
            table.add_row([bold("Aprobación y actualización del programa:"), f"{aprCurso}"])
            table.append(NoEscape('[10pt]'))
    doc.append(NewPage())
    with doc.create(Tabularx(table_spec=r"p{3cm}p{13cm}")) as table:
            table.add_row([textcolor
            (   
            size="12",
            vspace="14",
            color="parte",
            bold=True,
            text="2. Descripción general"
            )
            ,desGener])  
    doc.append(VerticalSpace("4mm", star=True))  
    doc.append(NewLine())
    with doc.create(Tabularx(table_spec=r"p{3cm}p{13cm}")) as table:
            table.add_row([textcolor
            (   
            size="12",
            vspace="14",
            color="parte",
            bold=True,
            text="3. Objetivos"
            )
            ,objCurso])
    doc.append(VerticalSpace("4mm", star=True)) 
    if id in ["CYD0609"]:
        doc.append(NewPage())
    else:
        doc.append(NewLine())
    with doc.create(Tabularx(table_spec=r"p{3cm}p{13cm}")) as table:
        table.add_row([textcolor
        (   
        size="12",
        vspace="14",
        color="parte",
        bold=True,
        text="4. Contenidos"
        )
        ,conDescr])
    doc.append(NewLine())
    doc.append(conCurso)
    doc.append(textcolor
        (   
        size="14",
        vspace="0",
        color="parte",
        bold=True,
        text="II parte: Aspectos operativos"
        ))
    doc.append(VerticalSpace("4mm", star=True))  
    doc.append(NewLine())
    doc.append(fontselect
        (
        size="10",
        vspace="12"      
        ))
    with doc.create(Tabularx(table_spec=r"p{3cm}p{13cm}")) as table:
        table.add_row([textcolor
        (   
        size="12",
        vspace="14",
        color="parte",
        bold=True,
        text="5. Metodología"
        )
        ,metCurso])
    doc.append(VerticalSpace("2mm", star=True))  
    doc.append(NewLine())
    with doc.create(Tabularx(table_spec=r"p{3cm}p{13cm}")) as table:
        table.add_row([textcolor
        (   
        size="12",
        vspace="14",
        color="parte",
        bold=True,
        text="6. Evaluación"
        )
        ,evaCurso])
    doc.append(VerticalSpace("2mm", star=True))  
    doc.append(NewLine())
    doc.append(evaTabla)
    doc.append(VerticalSpace("2mm", star=True))  
    doc.append(NewLine())
    with doc.create(Tabularx(table_spec=r"p{3cm}p{13cm}")) as table:
        table.add_row([""
        ,evaRepo])
    doc.append(VerticalSpace("4mm", star=True))  
    doc.append(NewLine()) #antes era newline
    with doc.create(Tabularx(table_spec=r"p{3cm}p{13cm}")) as table:
        table.add_row([textcolor
        (   
        size="12",
        vspace="14",
        color="parte",
        bold=True,
        text="7. Bibliografía"
        )
        ,bibCurso]) 
    doc.append(bibPrint)
    # doc.append(VerticalSpace("2mm", star=True))  
    # doc.append(NewLine())
    with doc.create(Tabularx(table_spec=r"p{3cm}p{13cm}")) as table:
        table.add_row([textcolor
        (   
        size="12",
        vspace="14",
        color="parte",
        bold=True,
        text="8. Persona docente"
        )
        ,proImpar])
    doc.append(proCurso)
    output_base = PROGRAM_OUTPUTS / codCurso
    doc.generate_pdf(str(output_base), clean=False, clean_tex=False, compiler='lualatex')
    try:
        subprocess.run(["biber", codCurso], cwd=PROGRAM_OUTPUTS, check=True)
    except subprocess.CalledProcessError as error:
        biber_log = PROGRAM_OUTPUTS / f"{codCurso}.blg"
        diagnostic = ""
        if biber_log.exists():
            log_lines = biber_log.read_text(encoding="utf-8", errors="replace").splitlines()
            relevant_lines = [
                line for line in log_lines if "ERROR" in line or "WARN" in line
            ]
            diagnostic = "\n".join(relevant_lines[-10:])
        message = f"Biber falló al procesar {codCurso}."
        if diagnostic:
            message += f"\n{diagnostic}"
        raise RuntimeError(message) from error
    doc.generate_pdf(str(output_base), clean=False, clean_tex=False, compiler='lualatex')
    doc.generate_pdf(str(output_base), clean=False, clean_tex=False, compiler='lualatex')
    if areCurso in TRClist:
        prefix = "TRC"
    else:
        prefix = areCurso
    generated_pdf = PROGRAM_OUTPUTS / f"{codCurso}.pdf"
    final_pdf = PROGRAM_OUTPUTS / f"{prefix}-{id[3:7]}-{codCurso}-{nomCurso}.pdf"
    generated_pdf.replace(final_pdf)

def clean_auxiliary_files():
    for pattern in (
        "*.tex", "*.aux", "*.bbl", "*.bcf", "*.blg", "*.log", "*.run.xml",
        "*.fdb_latexmk", "*.fls", "*.synctex.gz",
    ):
        for path in PROGRAM_OUTPUTS.glob(pattern):
            path.unlink()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Genera programas de curso en outputs/programas.")
    parser.add_argument("course_ids", nargs="*", help="IDs internos, por ejemplo SCF1002.")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Genera todos los cursos que tienen un programa curricular definido.",
    )
    parser.add_argument("--keep-aux", action="store_true", help="Conserva archivos auxiliares de LaTeX.")
    args = parser.parse_args()

    selected_ids = cursos.loc[cursos["propio"] == 1, "id"].dropna().to_list() if args.all else args.course_ids
    if not selected_ids:
        parser.error("indique al menos un ID de curso o use --all")

    validation_issues = validate_program_data(selected_ids)
    if validation_issues:
        preview = "\n".join(validation_issues[:20])
        remaining = len(validation_issues) - 20
        if remaining > 0:
            preview += f"\n... y {remaining} inconsistencias adicionales"
        parser.error(f"no se puede iniciar la generación:\n{preview}")

    print(f"Se generarán {len(selected_ids)} programa(s).")
    try:
        for course_id in selected_ids:
            generar_programa(course_id)
    finally:
        if not args.keep_aux:
            clean_auxiliary_files()
