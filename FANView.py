import simplekml
import pandas as pd
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import Calendar
import babel.numbers
import os
from datetime import datetime
import numpy as np
import re
import time


def coordenadas_GE(coordenadas):
    patron = re.compile(r'(\d+)°(\d+)\'(\d+)\'([NSWE])\s+(\d+)°(\d+)\'(\d+)\'([NSWE])')
    coincidencias = patron.match(coordenadas)

    if coincidencias:
        valor_1 = [coincidencias.group(1), coincidencias.group(2), coincidencias.group(3), coincidencias.group(4)]
        valor_2 = [coincidencias.group(5), coincidencias.group(6), coincidencias.group(7), coincidencias.group(8)]
    else:
        return None
    
    neg = ['S', 'W']

    valor_coord_1 = int(valor_2[0]) + int(valor_2[1]) / 60 + int(valor_2[2]) / 3600
    valor_coord_2 = int(valor_1[0]) + int(valor_1[1]) / 60 + int(valor_1[2]) / 3600

    if valor_2[3] in neg:
        valor_coord_1 = valor_coord_1*-1
    if valor_1[3] in neg:
        valor_coord_2 = valor_coord_2*-1

    return [(valor_coord_1, valor_coord_2)]

def coord(coordenada):
    # Extraer grados, minutos y segundos usando expresiones regulares
    match = re.match(r'(\d+)[ºª]\s*(\d+)\'\s*(\d+\.?\d*)"', coordenada)
    if match:
        grados, minutos, segundos = map(float, match.groups())
        # Convertir a formato gg°mm'ss"
        resultado = grados + minutos / 60 + segundos / 3600
        return resultado
    else:
        return None

def convertir_a_decimal(coordenada):
    # Usar expresiones regulares para extraer grados, minutos y segundos
    match = re.match(r"(\d+)°(\d+)'(\d+)\"", coordenada)
    
    if match:
        grados, minutos, segundos = map(float, match.groups())
        decimal = -1*(grados + minutos / 60 + segundos / 3600)
        return round(decimal, 7)
    else:
        # Manejar casos donde el formato no es el esperado
        print(f"Error en el formato de la coordenada: {coordenada}")
        return None  # O manejar de otra manera según tus necesidades
    
empresas=["MultiX", "Blumar"]
profundidad=[0, 5, 15]

### SELECCIÓN DE EMPRESA ###
selected_option = None

def show_selection():
    global selected_option
    selected_option = combo.get()
    main_window.destroy()

main_window = tk.Tk()
main_window.config(width=300, height=200)
main_window.title("Empresa:")

combo = ttk.Combobox(
    state="readonly",
    values=empresas
)
combo.place(x=50, y=50)
button = ttk.Button(text="Finalizar", command=show_selection)
button.place(x=50, y=100)
main_window.mainloop()
empresa=selected_option
centros_path=r"C:\Users\ernes\Documents\Trabajo\Proyecto_Beta\datos_xlsx\Centros.xlsx"
df_centros=pd.read_excel(centros_path,sheet_name=empresa)
# Aplicar la función a las columnas LATITUDE y LONGITUDE
df_centros['LATITUDE'] = df_centros['LATITUDE'].apply(convertir_a_decimal)
df_centros['LONGITUDE'] = df_centros['LONGITUDE'].apply(convertir_a_decimal)

### SELECCIÓN DE MONITOREO ###
selected_option = None
monitoreo=["CENTRO", "BARCO"]

main_window = tk.Tk()
main_window.config(width=300, height=200)
main_window.title("Elija monitoreo")

combo = ttk.Combobox(
    state="readonly",
    values=monitoreo
)
combo.place(x=50, y=50)
button = ttk.Button(text="Finalizar", command=show_selection)
button.place(x=50, y=100)
main_window.mainloop()
monitoreo_selected=selected_option
## Cuadro Resumen Algas Nocivas
conc_path=r"C:\Users\ernes\Documents\Trabajo\Proyecto_Beta\datos_xlsx\Algas_Nocivas.xlsx"
sheet_name = monitoreo_selected
df_algas_nocivas = pd.read_excel(conc_path, sheet_name=sheet_name)
especie = df_algas_nocivas['ESPECIE'].tolist()


### SELECCIÓN DE ESPECIE ###
selected_option = None

main_window = tk.Tk()
main_window.config(width=300, height=200)
main_window.title("Elija la especie")

combo = ttk.Combobox(
    state="readonly",
    values=especie
)
combo.place(x=50, y=50)
button = ttk.Button(text="Finalizar", command=show_selection)
button.place(x=50, y=100)
main_window.mainloop()
especie=selected_option


### SELECCIÓN DE PROFUNDIDAD ###
selected_option = None

main_window = tk.Tk()
main_window.config(width=300, height=200)
main_window.title("Escoja la Profundidad, en metros")

combo = ttk.Combobox(
    state="readonly",
    values=profundidad
)
combo.place(x=50, y=50)
button = ttk.Button(text="Finalizar", command=show_selection)
button.place(x=50, y=100)
main_window.mainloop()
profundidad=np.int64(selected_option)


### SELECCIÓN DE FECHA ###
fecha_seleccionada = None
def show_calendar():
    def on_date_select():
        global fecha_seleccionada
        fecha_seleccionada = cal.get_date()
        top.destroy()
        main_window.destroy()

    top = tk.Toplevel(main_window)
    cal = Calendar(top, font="Arial 14", selectmode='day', locale='es_ES')
    cal.pack(fill="both", expand=True)
    ttk.Button(top, text="Seleccionar", command=on_date_select).pack()

main_window = tk.Tk()
main_window.config(width=300, height=200)
main_window.title("Seleccionar Fecha")

button = ttk.Button(text="Seleccionar Fecha", command=show_calendar)
button.place(x=50, y=50)
main_window.mainloop()
fecha_obj = datetime.strptime(fecha_seleccionada, "%d/%m/%y")
fecha=fecha_obj.strftime("%Y-%m-%d %H:%M:%S")


### ARMAR CONJUNTO DE PLOTEO ###
DB_path=r"C:\Users\ernes\Documents\Trabajo\Proyecto_Beta\datos_xlsx\DB.xlsx"
df_DB=pd.read_excel(DB_path,sheet_name=empresa)
filtered_data=df_DB[
    (df_DB['MONITOREO'] == monitoreo_selected) &
    (df_DB['NOCIVO'] == 'SI') &
    (df_DB['FECHA'] == fecha) &
    (df_DB['ESPECIE'] == especie) &
    (df_DB['PROFUNDIDAD'] == profundidad)
]

Points_names = filtered_data['CENTRO'].tolist()

df_points_names = pd.DataFrame({'NOMBRE': Points_names})
merged_df = pd.merge(df_points_names, df_centros, on='NOMBRE', how='left')

Points_lat = merged_df['LATITUDE'].tolist()
Points_lon = merged_df['LONGITUDE'].tolist()


### PLOTEO EN KML ###
kml=simplekml.Kml()
for i in range(len(Points_names)):
    point_style = simplekml.Style()
    point_style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/shaded_dot.png'
   
    especie_filtrada_db = df_DB.loc[(df_DB['ESPECIE'] == especie)&(df_DB['PROFUNDIDAD'] == 5), 'CANTIDAD']
    especie_filtrada_nocivas = df_algas_nocivas.loc[df_algas_nocivas['ESPECIE'] == especie, 'NORMAL']

    if especie_filtrada_db.iloc[i] <= especie_filtrada_nocivas.iloc[0]:
        point_style.iconstyle.color = simplekml.Color.rgb(0,255,0)

    elif especie_filtrada_db.iloc[i] > especie_filtrada_nocivas.iloc[0] and especie_filtrada_db.iloc[i] <= df_algas_nocivas.loc[df_algas_nocivas['ESPECIE'] == especie, 'ALERTA'].iloc[0]:
        point_style.iconstyle.color = simplekml.Color.yellow

    else:
        point_style.iconstyle.color = simplekml.Color.red

    point_style.iconstyle.scale = 1.5
    point = kml.newpoint(name='', coords=[(Points_lon[i], Points_lat[i])])
    #point = kml.newpoint(name=Points_names[i], coords=[(Points_lon[i], Points_lat[i])])
    point.style = point_style
    
#Centrar cámara
coord_golfo = "47°11'23'S 75°08'24'W"
[(lon, lat)] = coordenadas_GE(coord_golfo)
kml.document.camera = simplekml.Camera(latitude=lat, longitude=lon,altitude=2000000, tilt=0)

# Guardar mapa en KML
nombre_especie = especie.replace(" ", "_").replace(".", "")
fecha_objeto = datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S")
fecha_formateada = fecha_objeto.strftime("%Y-%m-%d")
nombre_archivo=f"{nombre_especie}_{empresa}_{fecha_formateada}_{profundidad}m.kml"

kml_path = os.path.join(r"C:\Users\ernes\Documents\Trabajo\Proyecto_Beta\KML", nombre_archivo)
kml.save(kml_path)

#Abrir el archivo en Google Earth
subprocess.Popen(r"C:\Program Files\Google\Google Earth Pro\client\googleearth.exe", shell=True)
time.sleep(5)
subprocess.Popen(f"{kml_path}", shell=True)