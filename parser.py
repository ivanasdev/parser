import pandas as pd
from bs4 import BeautifulSoup
import csv
from csv import writer
import os
import re
import requests
from ftplib import FTP
import json
import spacy 
from spacy_download import load_spacy
import nltk
from nltk.corpus import wordnet as wn

        


def Envia_errores(folio, error):
    url = 'https://lizzi.appsholos.com/dev/api/index_get'
    params = {
        'action': 'envioIncidencias',
        'folio': folio,
        '_pass': 'holoscommsistemasdisruptivos',
        'licitador': 1,
        'error': error,
        'proceso': 'Genera_CSV'
    }

    try:
        response = requests.get(url, params=params)
        text_respuesta = response.text
        # Aquí puedes hacer algo con la respuesta recibida

        # Finaliza la ejecución del programa
        return
        ## sys.exit()

    except requests.exceptions.RequestException as e:
        print('Error al enviar errores al servicio web:', e)
        # Finaliza la ejecución del programa
        return
        ## sys.exit()

def enviar_archivos_ftp(servidor, usuario, contraseña, archivos):
    try:
        # Conexión al servidor FTP
        ftp = FTP(servidor)
        ftp.login(usuario, contraseña)
        ftp.set_pasv(False)  # bingo :) PARA QUITAR ERROR 1101
        ftp.cwd(dir_folios) #cambia a la carpeta de carga

        # Iterar sobre la lista de archivos
        for archivo in archivos:
            # Abrir el archivo en modo lectura binaria
            with open(archivo, 'rb') as file:
                # Subir el archivo al servidor
                ftp.storbinary(f'STOR {archivo}', file)
            print(f'{archivo} enviado correctamente.')
        # Cerrar la conexión FTP
        ftp.quit()

    except Exception as e:
        text_error=('Error durante la transferencia FTP:', e)
        # *** llamar funcion de envio de errores ***
        Envia_errores(num_folio, text_error)


nombre_carpetas = os.listdir()
url = "https://lizzi.appsholos.com/dev/api/folio_nuevo"
parametros = {
    "id_licitador": 1,
    "_pass": 'holoscommsistemasdisruptivos'
}
# Realizar la petición GET al webservice
response = requests.get(url, params=parametros)
# Verificar el código de respuesta HTTP
if response.status_code == 200:
    # Obtener la respuesta del webservice como JSON
    respuesta = response.json()
    # Obtener los datos de la respuesta
    estatus = respuesta.get("estatus")#1
    texto = respuesta.get("texto")#Registro ingresado correctamente
    num_folio = respuesta.get("parametros")#1
else:
    text_error= "Error en la solicitud al webservice: folio_nuevo."
    Envia_errores(0, text_error)

folio = str(num_folio).zfill(6)
#GENERA NOMBRE DE ARCHIVOS
detalle = folio+'_detalles'+ '.csv'
anexos = folio+'_anexos'+'.csv'
eventos = folio+'_eventos'+'.json'

register_list = []
anexos_list = []

def clean_string(cad):
    characteres = "'\n"
    for x in range(len(characteres)):
        cadena = cad.replace(characteres[x],"")
    return cadena

for nombre in nombre_carpetas:

    if 'File No.' in str(nombre):
        nombre_arch = str(nombre)
        # print(nombre_arch) <-- Aqui despliega los nombres de los archivos a generar
        file = open(nombre_arch, encoding='utf-8')
        soup = BeautifulSoup(file, 'html.parser', from_encoding='utf-8')
        caja = soup.find('div', class_='page-header')#Trae la informacion de todo lo que tiene el div
        id_licitacion = caja.find('small').get_text()#Numero de licitacion
        id_licitacion = id_licitacion[5:]
        register_list.append(id_licitacion)  
        arch = 1
        tablas = pd.read_html(nombre_arch, encoding='utf8', index_col=False)
        links_sobrantes = 0

        tabla_detalle = tablas[0]
        list_tabla_detalle = tabla_detalle[1].to_list()
        detalleskeywords=list_tabla_detalle[4]
        
        separador = ' " '
        separado = detalleskeywords.split(separador)
        frase = " ".join(separado)
       
        nlp=load_spacy("es_core_news_sm")
        sentence=frase
        doc=nlp(sentence)
        keywords1=[]
        for token in doc:
            if token.pos_ in ["PRON","PROPN","NOUN","VERB","AUX","ADV"]:
                keywords1.append(token.text)
          
                
             

                
                    
        for atributo in list_tabla_detalle:
            register_list.append(atributo)
            
            
           
    
           
        with open(detalle, 'a', newline='', encoding='utf8') as f_object:
            register_list.append(keywords1) 
          
            writer_object = writer(f_object)
            writer_object.writerow(register_list)
            f_object.close()
        register_list.clear()




        #Acceder a la tabla anexos
        tabla_anexos = tablas[1]
#print(tabla_anexos)
  
        #print(indice_c)

        #Obtain the links
        list_urls = []
        sub_list_urls = []
        patt = re.compile('href="(.*)"/>')
        div_info = soup.find('div', class_='panel panel-info')
        list_orangeLink = soup.find_all('td', class_ = 'orangeLink')
        len_list_orangeLink = len(list_orangeLink)
    #para quitar los caracteres sobrantes del link
        for link in list_orangeLink:
            url = re.findall(patt, str(link))[0]
            url = url[:-65]
            list_urls.append(url)
        rows_number = tabla_anexos.shape[0]
        rows_sobrantes = 0

        sub_list_urls = []
        for i in range(rows_number):
            http = 'https://msc.cfe.mx'+str(list_urls[i])
            sub_list_urls.append(http)
        tabla_anexos['Descargar'] = sub_list_urls
        sub_list_urls.clear()


    #obtener la columna de los archivos de los detalles manualmente
        list_class_tds = soup.find('table',attrs={'class':'table table-striped fixed'}).find('tbody').find_all('td')
    #print(list_class_tds)


        for i in range(rows_number):
            anexos_list.append(id_licitacion)
            #rows = soup.find_all('table',attrs={'class':'table table-striped fixed'})
            #noms_arch = rows[1].find_all('td')[i]   #Aqui estan los nombres de los archivos eureka
            nom_arch = tabla_anexos.columns.values
            #print(nom_arch)                #------------------->Aqui voy 
            list_reg_anexos = tabla_anexos.iloc[i].to_list()
            for elem in list_reg_anexos:
                anexos_list.append(elem)
            #print('lo que va a agregarse: ')
            #print(anexos_list)
            with open(anexos, 'a', newline='', encoding='utf8') as f_object:
                writer_object = writer(f_object)
                writer_object.writerow(anexos_list)
                f_object.close()
            register_list.clear()
            anexos_list.clear()
            


servidor = 'appsholos.com' 
usuario = 'u925124967.ftplizzi'
contraseña = 'M}[}pmcBRNg^#7-)'
dir_folios = '/dev/upload/folios/' + folio + '/' # Arma ubicacion carpeta para cargar archivos
# print(dir_folios)

archivos = [detalle, anexos, eventos] 

enviar_archivos_ftp(servidor, usuario, contraseña, archivos)

# URL del webservice
url = "https://lizzi.appsholos.com/dev/api/index_get"

# Parámetros a enviar al webservice
parametros = {
    "action": "uploadtender",
    "_pass": 'holoscommsistemasdisruptivos',
    "folio": num_folio
}

# Realizar la petición GET al webservice
response = requests.get(url, params=parametros)

# Verificar el código de respuesta HTTP
if response.status_code == 200:
    respuesta = response.json()
    estatus_2 = respuesta.get("estatus")
    texto_2 = respuesta.get("texto")
    parametros_2 = respuesta.get("parametros")
    
    
else:
    text_error="Error en la solicitud al webservice: uploadtender"
    # LLAMAR FUNCION DE MENSAJES DE ERROR
    Envia_errores(num_folio, text_error)


#fin del proceso
