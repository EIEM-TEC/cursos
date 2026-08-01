"""Reúne funciones gráficas y auxiliares compartidas por los generadores de programas y mallas."""

import textwrap
import roman
import numpy as np
from matplotlib import pyplot as plt
from pylatex import Document, Package, Command, PageStyle, Head, Foot, NewPage,\
    TextColor, MiniPage, StandAloneGraphic, simple_page_number,\
    TikZ, TikZScope, TikZNode, TikZOptions, TikZCoordinate, TikZNodeAnchor, TikZPath,\
    UnsafeCommand,\
    VerticalSpace, HorizontalSpace, NewLine,\
    LongTable
from pylatex.base_classes import Arguments
from pylatex.utils import NoEscape, bold, italic

def number_to_ordinals(number_str):
    match number_str:
        case "1" | "3":
            number_str += r"\textsuperscript{er}"
        case "2":
            number_str += r"\textsuperscript{do}"
        case "4" | "5" | "6":
            number_str += r"\textsuperscript{to}"
        case "7" | "10":
            number_str += r"\textsuperscript{mo}"
        case "8":
            number_str += r"\textsuperscript{vo}"
        case "9":
            number_str += r"\textsuperscript{no}"
    return number_str 

def gen_list_porc(N):
    # Verificar que N esté entre 0 y 100
    if N < 0 or N > 100:
        raise ValueError("El número debe estar entre 0 y 100 inclusive.")
    
    # Generar la lista de números múltiplos de 10 hasta N
    lista_numeros = list(range(10, N + 1, 10))
    
    # Generar la lista de cadenas con el signo '%'
    lista_porcentajes = [f"{numero}%" for numero in lista_numeros]
    
    return lista_numeros, lista_porcentajes

def radar_clie(ax,cat,val,title,fontsize,tfontsize,rpmax,mult,textw):
    
    N = len(cat)

    # Cerramos el círculo
    val += val[:1]
    ang = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    ang += ang[:1]

    # Dibujamos el gráfico
    ax.plot(ang, val, linewidth=2, linestyle='solid', color='teal')
    ax.fill(ang, val, color='teal', alpha=0.4)

    # Ajustamos los límites radiales
    ax.set_ylim(0, rpmax)

    # Ajustamos las etiquetas del eje radial
    ax.set_rlabel_position(0)
    # list_porc, list_l_porc = gen_list_porc(rpmax)
    list_porc = list(range(mult, rpmax + 1, mult))
    list_l_porc = [f"{numero}%" for numero in list_porc]

    ax.set_yticks(list_porc, list_l_porc, color="grey", size=fontsize)

    ax.set_xticks(ang[:-1])
    ax.set_xticklabels([])  # Ocultamos las etiquetas por defecto

    # Añadimos las etiquetas manualmente
    for angle, label in zip(ang[:-1], cat):
        angle_degree = np.degrees(angle)
        if angle_degree >= 90 and angle_degree <= 270:
            alignment = "right"
            angle_text = angle_degree + 180  # Rotamos el texto para que no esté al revés
        else:
            alignment = "left"
            angle_text = angle_degree
        # Posicionamos el texto dentro del gráfico
        ax.text(
            angle,
            ax.get_ylim()[1] * 0.4,  # Ajusta este factor para mover el texto radialmente
            textwrap.fill(label, width=int(textw)),
            size=fontsize,
            horizontalalignment=alignment,
            verticalalignment="top",
            rotation=angle_text,
            rotation_mode='anchor'
        )

    # Añadimos título
    ax.set_title(textwrap.fill(title, width=tfontsize*4), size=tfontsize, color='blue', y=1.1)

    # Añadimos gridlines personalizados
    ax.grid(color='grey', linestyle='dashed', linewidth=0.5)

    # Mejoramos la estética general
    ax.spines['polar'].set_visible(False)
    ax.set_facecolor('#f7f7f7')

def multiradar(lista,saberes,areas,columnaPorc,fontsize,tfontsize,rpmax,mult,textw):
    fig, axs = plt.subplots(4, 2, subplot_kw=dict(projection='polar'), figsize=(10, 18))

    row = 0
    column = 0
    for area in lista:
        nom = areas[areas['codArea']==area].nombre.item()
        sab = saberes[saberes['codArea']==area]
        porc = areas[areas['codArea']==area]
        porc = porc[columnaPorc].item()
        cat = sab['nombre'].to_list()
        val = sab[columnaPorc].to_list()
        #val = [(x / porc)*100 for x in val]
        radar_clie(axs[row,column],cat,val,nom,fontsize,tfontsize,rpmax,mult,textw)
        if column < 1:
            column += 1
        else:
            row += 1
            column = 0
    if len(lista) < 8:
        fig.delaxes(axs[row,column])
    plt.tight_layout(pad=1, w_pad=0, h_pad=0)
    plt.savefig(f'./graficos/{columnaPorc}.pdf', dpi=600)

def radar(nombre,areas,cat,val,title,fontsize,tfontsize,rpmax,mult,textw):
    nom = areas[areas['codArea'].isin(cat)]['nombre']
    fig, axs = plt.subplots(subplot_kw=dict(projection='polar'), figsize=(10, 10))
    radar_clie(axs,nom,val,title,fontsize,tfontsize,rpmax,mult,textw)
    plt.savefig(f'./graficos/{nombre}.pdf', dpi=600)

def radar_saberes(nombre,saberes,areas,columnaPorc,fontsize,tfontsize,rpmax,mult,textw):
    nom = areas[areas['codArea']==nombre].nombre.item()
    sab = saberes[saberes['codArea']==nombre]
    porc = areas[areas['codArea']==nombre]
    porc = porc[columnaPorc].item()
    cat = sab['nombre'].to_list()
    val = sab[columnaPorc].to_list()
    fig, axs = plt.subplots(subplot_kw=dict(projection='polar'), figsize=(10, 10))
    radar_clie(axs,cat,val,"",fontsize,tfontsize,rpmax,mult,textw)
    plt.savefig(f'./graficos/{nombre}.pdf', dpi=600)

def textcolor(size,vspace,color,bold,text,hspace="0"):
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

def colocar_titulo(titulo,color):
    dump = NoEscape(r"\draw ")
    dump += NoEscape(f"({round(57/2)},{round(4)})")
    dump += NoEscape(f"pic{{titulo={{{titulo},{color}}}}};")
    return dump

def colocar_curso(codigo,nombre,fila,semestre,sesgo,horasteoria,horaspractica,creditos,color):
    dump = NoEscape(r"\draw ")
    dump += NoEscape(f"({round(6.87*(semestre-sesgo)+0.5,2)},{round(-4.2*fila-0.5,2)})")
    dump += NoEscape(f"pic{{curso={{{codigo},{nombre},{round(horasteoria)},{round(horaspractica)},{round(creditos)},{color}}}}};")
    return dump

def colocar_semestre(semestre,sesgo,color,horasteoriasemestre,horaspracticasemestre,creditossemestre):
    dump = NoEscape(r"\draw ")
    dump += NoEscape(f"({round(6.87*(semestre-sesgo)+0.5,2)},{round(0)})")
    if semestre == 0:
        dump += NoEscape(f"pic{{semestre={{{semestre},{color},{horasteoriasemestre},{horaspracticasemestre},{creditossemestre}}}}};")
    else:
        dump += NoEscape(f"pic{{semestre={{{roman.toRoman(semestre)},{color},{horasteoriasemestre},{horaspracticasemestre},{creditossemestre}}}}};")
    return dump

def colocar_arrowreq(semestre,sesgo,fila,sesgovert,color):
    dump = NoEscape(r"\draw ")
    dump += NoEscape(f"[-{{Stealth[length=3mm,width=2mm]}},{color},line width=0.5mm]")
    dump += NoEscape(f"({round(6.87*(semestre-sesgo)-3.85,2)},{round(-4.2*fila-sesgovert,2)}) -- ")
    dump += NoEscape(f"({round(6.87*(semestre-sesgo)-2.03,2)},{round(-4.2*fila-sesgovert,2)});")
    return dump

def colocar_arrowreqs(semestre,sesgo,fila,dir,color):
    dump = NoEscape(r"\draw ")
    dump += NoEscape(f"[{color},line width=0.5mm]") 
    if dir == 1:
        dump += NoEscape(f"({round(6.87*(semestre-sesgo)-3.85,2)},{round(-4.2*fila-3.5,2)}) --++ (0.3,0) --++ (0,1.8)coordinate(inicio)")
    else:
        dump += NoEscape(f"({round(6.87*(semestre-sesgo)-3.85,2)},{round(-4.2*fila+2.5,2)}) --++ (0.3,0) --++ (0,-1.8)coordinate(inicio)")
    dump += NoEscape(r";")
    dump += NoEscape("\n")
    dump += NoEscape(r"\draw ")
    dump += NoEscape(f"[-{{Stealth[length=3mm,width=2mm]}},{color},line width=0.5mm]")
    dump += NoEscape(f"(inicio) --++ (1.55,0)")
    dump += NoEscape(r";")
    dump += NoEscape("\n")
    dump += NoEscape(r"\draw ")
    dump += NoEscape(f"[fill,{color}] ")
    dump += NoEscape(f"(inicio) circle (0.45mm)")
    dump += NoEscape(r";")
    return dump


def colocar_arrowcoreq(semestre,sesgo,fila,dir,color):
    dump = NoEscape(r"\draw ")
    dump += NoEscape(f"[-{{Stealth[length=3mm,width=2mm]}},{color},line width=0.5mm]")
    if dir == 1:
        dump += NoEscape(f"({round(6.87*(semestre-sesgo)+0.5,2)},{round(-4.2*fila-3.08,2)}) --++ ")
        dump += NoEscape(f"(0,0.97);")
    if dir == -1:
        dump += NoEscape(f"({round(6.87*(semestre-sesgo)+0.5,2)},{round(-4.2*fila+2.08,2)}) --++ ")
        dump += NoEscape(f"(0,-0.97);")        
    return dump

def colocar_diaesreq(semestre,sesgo,fila,sesgovert,num,color):#1.35 de largo
    dump = NoEscape(r"\draw ")
    dump += NoEscape(f"[-{{Turned Square[open,length=4mm,line width=0.25mm,width=4mm]}},{color},line width=0.5mm,]")
    dump += NoEscape(f"({round(6.87*(semestre-sesgo)+3.02,2)},{round(-4.2*fila-sesgovert,2)}) --++ (1.35,0) ")
    dump += NoEscape(r"node[align=center,text width=4mm,xshift=-4.5mm]{\color{black}\fontsize{10pt}{10pt}\selectfont \textbf{")
    dump += NoEscape(f"{num}")
    dump += NoEscape(r"}};")                 
    return dump

def colocar_diareq(semestre,sesgo,fila,sesgovert,num,color):#1.35 de largo
    dump = NoEscape(r"\draw ")
    dump += NoEscape(f"[{{Turned Square[open,length=4mm,line width=0.25mm,width=4mm]}}-,{color},line width=0.5mm,]")
    dump += NoEscape(f"({round(6.87*(semestre-sesgo)-3.38,2)},{round(-4.2*fila-sesgovert,2)}) ")
    dump += NoEscape(r"node[align=center,text width=4mm,xshift=4.5mm]{\color{black}\fontsize{10pt}{10pt}\selectfont \textbf{")
    dump += NoEscape(f"{num}")
    dump += NoEscape(r"}}")  
    dump += NoEscape(f"--++ (1.35,0);")
    return dump

def colocar_triacoreq(semestre,sesgo,fila,num,color):
    dump = NoEscape(r"\draw ")
    dump += NoEscape(f"[-{{Triangle[reversed,open,length=3mm,line width=0.25mm,width=4mm]}},{color},line width=0.5mm,]")
    dump += NoEscape(f"({round(6.87*(semestre-sesgo)+0.5,2)},{round(-4.2*fila+1.11,2)}) --++ ")
    dump += NoEscape(f"(0,0.94)")
    dump += NoEscape(r"node[align=center,text width=4mm,yshift=-2.5mm]{\color{black}\fontsize{10pt}{10pt}\selectfont \textbf{")
    dump += NoEscape(f"{num}")
    dump += NoEscape(r"}};")      
    return dump

def colocar_triaescoreq(semestre,sesgo,fila,num,color):
    dump = NoEscape(r"\draw ")
    dump += NoEscape(f"[-{{Triangle[open,length=3mm,line width=0.25mm,width=4mm]}},{color},line width=0.5mm,]")
    dump += NoEscape(f"({round(6.87*(semestre-sesgo)+0.5,2)},{round(-4.2*fila-2.11,2)}) --++ ")
    dump += NoEscape(f"(0,-0.94)")    
    dump += NoEscape(r"node[align=center,text width=4mm,yshift=4.5mm]{\color{black}\fontsize{10pt}{10pt}\selectfont \textbf{")
    dump += NoEscape(f"{num}")
    dump += NoEscape(r"}};")      
    return dump

def colocar_recreq(titulo1,titulo2,color):
    dump = NoEscape(r"\filldraw ")
    dump += NoEscape(f"[fill=white, draw=black]")
    dump += NoEscape(r"(30,1) ")
    dump += NoEscape(r" rectangle ") 
    dump += NoEscape(r" ++ (25,-40);")
    dump += NoEscape("\n")
    dump += NoEscape(r"\filldraw ")
    dump += NoEscape(f"[fill={color}, draw=black]")
    dump += NoEscape(r"(30,1) ")
    dump += NoEscape(r" rectangle ") 
    dump += NoEscape(r" ++ (25,-2) node[midway,align=center,text width=60mm]{\color{black}\fontsize{20pt}{10pt}\selectfont \textbf{")
    dump += NoEscape(f"{titulo1}")
    dump += NoEscape(r"}};") 
    dump += NoEscape("\n")
    dump += NoEscape(r"\filldraw ")
    dump += NoEscape(f"[fill={color}, draw=black]")
    dump += NoEscape(r"(30,-18) ")
    dump += NoEscape(r" rectangle ") 
    dump += NoEscape(r" ++ (25,-2) node[midway,align=center,text width=60mm]{\color{black}\fontsize{20pt}{10pt}\selectfont \textbf{")
    dump += NoEscape(f"{titulo2}")
    dump += NoEscape(r"}};") 
    return dump

def colocar_notasTC(textonota,sesgo):
    dump = NoEscape(r"\filldraw ")
    dump += NoEscape(r"[fill=white, draw=white]")
    dump += NoEscape(f"(25,{round(-39.8-sesgo*.8,2)})")
    dump += NoEscape(r" node[align=left,text width=490mm]{\color{black}\fontsize{16pt}{10pt}\selectfont \textbf{")
    dump += NoEscape(f"{sesgo}. {textonota}")
    dump += NoEscape(r"}};") 
    return dump

def colocar_notas(textonota,sesgo):
    dump = NoEscape(r"\filldraw ")
    dump += NoEscape(r"[fill=white, draw=white]")
    dump += NoEscape(f"(31,{round(-19-sesgo*2)})")
    dump += NoEscape(r" rectangle ") 
    dump += NoEscape(r" ++ (23,-2) node[midway,align=left,text width=220mm]{\color{black}\fontsize{16pt}{10pt}\selectfont \textbf{")
    dump += NoEscape(f"{sesgo}. {textonota}")
    dump += NoEscape(r"}};") 
    return dump

def malla_enf(malla,cursos,sesgo,lista,nombrearea,area_colors,titulo,rango,enf):
        reqcounter = 0
        malla.append(colocar_titulo(titulo,"lightgray"))
        if enf:
            malla.append(colocar_recreq("Electivas","Notas","lightgray"))
            malla.append(colocar_notas("Cursos del tronco común en color blanco",1))
            malla.append(colocar_notas("Debe escogerse 2 de las 9 electivas posibles para cursarlas en el décimo semestre",2))
            malla.append(colocar_notas("Debe realizarse un Trabajo Final de Graduación para poder graduarse de Licenciatura. Este equivale a 7 créditos y 21 horas prácticas semanales",3))
        else:
            malla.append(colocar_notasTC("Debe cursarse tres centros de formación humanistica para poder graduarse",1))
            #malla.append(colocar_notasTC("Debe realizarse una Práctica Profesional para poder escoger la salida lateral de bachillerato. Esta equivale a 7 créditos y 315 horas laboradas en un semestre",2))
        cursos_enf = cursos[cursos["area"].isin(lista)]
        for semestre in rango:
            horasteoriasemestre = cursos_enf[cursos_enf.semestre == semestre].horasTeoria.sum()
            horaspracticasemestre = cursos_enf[cursos_enf.semestre == semestre].horasPractica.sum()
            creditossemestre = cursos_enf[cursos_enf.semestre == semestre].creditos.sum()
            malla.append(colocar_semestre(semestre,sesgo,"lightgray",horasteoriasemestre,horaspracticasemestre,creditossemestre))            
        for id in cursos_enf.id:
            semestre = cursos_enf[cursos_enf.id == id].semestre.item()
            codigo = cursos_enf[cursos_enf.id == id].codigo.item()
            nombre = cursos_enf[cursos_enf.id == id].nombre.item()
            fila = cursos_enf[cursos_enf.id == id].fila.item()
            horasteoria = cursos_enf[cursos_enf.id == id].horasTeoria.item()
            horaspractica = cursos_enf[cursos_enf.id == id].horasPractica.item()
            creditos = cursos_enf[cursos_enf.id == id].creditos.item()
            area = cursos_enf[cursos_enf.id == id].area.item()        
            if enf:
                if area == nombrearea:
                    color = area_colors.get(area)
                else:
                    color = "white"
            else:
                color = area_colors.get(area)
            if semestre >= sesgo:
                requi = cursos_enf[cursos_enf.id == id].requisitos.str.split(';',expand=True)
                corequi = str(cursos_enf[cursos_enf.id == id].correquisitos.item())                           
                malla.append(colocar_curso(codigo,nombre,fila,semestre,sesgo,horasteoria,horaspractica,creditos,color))
                if not(requi[0].isna().item()):
                    for column in requi.columns:
                        idreq = requi[column].item()
                        # print(id)
                        # print(idreq)
                        codreq = cursos_enf[cursos_enf.id == idreq].codigo.item()
                        semreq = cursos_enf[cursos_enf.id == idreq].semestre.item()
                        filareq = cursos_enf[cursos_enf.id == idreq].fila.item()
                        sevesreq = cursos_enf[cursos_enf.id == idreq].sevesreq.item()
                        sevreq = cursos_enf[cursos_enf.id == id].sevreq.item() 
                        if semestre > sesgo:
                            if (filareq == fila) and (semreq == semestre - 1):
                                malla.append(colocar_arrowreq(semestre,sesgo,fila,-0.7,"black"))
                            elif ((filareq == fila - 1) or (filareq == fila + 1)) and (semreq == semestre - 1):
                                if (filareq == fila - 1):
                                    dir = -1
                                if (filareq == fila + 1):
                                    dir = 1
                                malla.append(colocar_arrowreqs(semestre,sesgo,fila,dir,"black"))                   
                            else:
                                reqcounter +=1
                                malla.append(colocar_diareq(semestre,sesgo,fila,sevreq,reqcounter,"black"))
                                malla.append(colocar_diaesreq(semreq,sesgo,filareq,sevesreq + 0.9,reqcounter,"black"))
                                cursos_enf.loc[cursos_enf['id'] == idreq, 'sevesreq'] = sevesreq + 1
                                cursos_enf.loc[cursos_enf['id'] == id, 'sevreq'] = sevreq + 1.8
                if not(corequi == 'nan'):
                    semcoreq = cursos_enf[cursos_enf.id == corequi].semestre.item()
                    filacoreq = cursos_enf[cursos_enf.id == corequi].fila.item()
                    if ((filacoreq == fila - 1) or (filacoreq == fila + 1)) and (semcoreq == semestre):
                        if (filacoreq == fila - 1):
                            dir = -1
                        if (filacoreq == fila + 1):
                            dir = 1
                        malla.append(colocar_arrowcoreq(semestre,sesgo,fila,dir,"black"))
                    else:
                        reqcounter +=1
                        malla.append(colocar_triacoreq(semestre,sesgo,fila,reqcounter,"black"))
                        malla.append(colocar_triaescoreq(semcoreq,sesgo,filacoreq,reqcounter,"black"))
