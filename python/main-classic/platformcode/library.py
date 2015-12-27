# -*- coding: iso-8859-1 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Herramientas de integración en Librería
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# Autor: jurrabi
#------------------------------------------------------------
import urllib
import os
import re
import sys
import xbmc
import xbmcgui
import string
import xml.parsers.expat

from core import config
from core import logger
from core import downloadtools
from core import scrapertools

CHANNELNAME = "library"
allchars = string.maketrans('', '')
deletechars = '\\/:*"<>|?' #Caracteres no válidos en nombres de archivo
# Esto permite su ejecución en modo emulado (preguntar a jesus por esto)
# seguro que viene bien para debuguear
try:
    pluginhandle = int( sys.argv[ 1 ] )
except:
    pluginhandle = ""

DEBUG = True

LIBRARY_PATH = config.get_library_path()
if not os.path.exists(LIBRARY_PATH):
    logger.info("[library.py] Library path doesn't exist:"+LIBRARY_PATH)
    os.mkdir(LIBRARY_PATH)

#MOVIES_PATH
MOVIES_PATH = xbmc.translatePath( os.path.join( LIBRARY_PATH, 'CINE' ) )
if not os.path.exists(MOVIES_PATH):
    logger.info("[library.py] Movies path doesn't exist:"+MOVIES_PATH)
    os.mkdir(MOVIES_PATH)

#SERIES_PATH
SERIES_PATH = xbmc.translatePath( os.path.join( LIBRARY_PATH, 'SERIES' ) )
if not os.path.exists(SERIES_PATH):
    logger.info("[library.py] Series path doesn't exist:"+SERIES_PATH)
    os.mkdir(SERIES_PATH)

def elimina_tildes(s):
    s = s.replace("Á","a")
    s = s.replace("É","e")
    s = s.replace("Í","i")
    s = s.replace("Ó","o")
    s = s.replace("Ú","u")
    s = s.replace("á","a")
    s = s.replace("é","e")
    s = s.replace("í","i")
    s = s.replace("ó","o")
    s = s.replace("ú","u")
    s = s.replace("À","a")
    s = s.replace("È","e")
    s = s.replace("Ì","i")
    s = s.replace("Ò","o")
    s = s.replace("Ù","u")
    s = s.replace("à","a")
    s = s.replace("è","e")
    s = s.replace("ì","i")
    s = s.replace("ò","o")
    s = s.replace("ù","u")
    s = s.replace("ç","c")
    s = s.replace("Ç","C")
    s = s.replace("Ñ","n")
    s = s.replace("ñ","n")
    return s

def title_to_folder_name(title):
    logger.info("Serie="+title)
    Serie = elimina_tildes(title)
    logger.info("Serie="+Serie)
    Serie = string.translate(Serie,allchars,deletechars)
    logger.info("Serie="+Serie)
    return Serie
 
def savelibrary(item,verbose=True,accion="play_from_library",pedirnombre=True):
    logger.info("[library.py] savelibrary:" + item.tostring())
    
    if not "Serie" in item: item.Serie=""
    
    if item.category != "Series":  #JUR - DEBUGIN INTERNO PARA 2.14
        item.category = "Cine"
        
    if item.category == "Cine":
        filename=string.translate(item.title,allchars,deletechars)+".strm"
        fullfilename = os.path.join(MOVIES_PATH,filename)
    elif item.category == "Series":
        if item.Serie == "": #Añadir comprobación de len>0 bien hecha
            logger.info('[library.py] savelibrary ERROR: intentando añadir una serie y serie=""')
            pathserie = SERIES_PATH
        else:
            #Eliminamos caracteres indeseados para archivos en el nombre de la serie
            Serie = title_to_folder_name(item.Serie)
            pathserie = xbmc.translatePath( os.path.join( SERIES_PATH, item.Serie ) )
        if not os.path.exists(pathserie):
            logger.info("[library.py] savelibrary Creando directorio serie:"+pathserie)
            try:
                os.mkdir(pathserie)
            except:
                os.mkdir(pathserie)

        #Limpiamos el titulo para usarlo como fichero
        from  core import scrapertools
        filename = scrapertools.get_season_and_episode(item.title)+".strm"
        #filename=string.translate(titulo,allchars,deletechars)+".strm"

        fullfilename = os.path.join(pathserie,filename)
    else:    #Resto de categorias de momento en la raiz de library
        fullfilename = os.path.join(LIBRARY_PATH,filename)
    
        
    if os.path.exists(fullfilename):
        logger.info("[library.py] savelibrary el fichero existe. Se sobreescribe")
        nuevo = 0
    else:
        nuevo = 1
    try:
        LIBRARYfile = open(fullfilename,"w")
    except IOError:
        logger.info("[library.py] savelibrary Error al grabar el archivo "+fullfilename)
        nuevo = 0
        raise
    item.channel = "library"
    item.strmfile = True
    itemurl = '%s?%s' % ( sys.argv[ 0 ] , item.tourl())
    logger.info("[library.py] savelibrary fullfilename=%s , itemurl=%s" % (fullfilename,itemurl))
    
    JSONfile  = item.tojson()
    JSONfile = "#" + '#'.join(JSONfile.splitlines(True))
    

    LIBRARYfile.write(itemurl + "\n" + JSONfile)
#    LIBRARYfile.write(urllib.quote_plus(url)+'\n')
#    LIBRARYfile.write(urllib.quote_plus(thumbnail)+'\n')
#    LIBRARYfile.write(urllib.quote_plus(server)+'\n')
#    LIBRARYfile.write(urllib.quote_plus(downloadtools.limpia_nombre_excepto_1(plot))+'\n')
    LIBRARYfile.flush();
    LIBRARYfile.close()

    logger.info("[library.py] savelibrary acaba")

    return nuevo
    

##############################################################################################
#C�digo para actualizar los strm al nuevo formato de url

def update2json(item, path="", progreso = None):
    from core.item import Item
    if path== "": path=LIBRARY_PATH
    import xbmcgui
    Main = False
    if progreso is None: 
      Main = True
      progreso = xbmcgui.DialogProgress()
      progreso.create("Actualizando Bibliotreca.." , "Entrando en directorio: " + path)
      
    logger.info("Entrando en directorio: " + path)
    for file in os.listdir(path):
      if os.path.isdir(os.path.join(path,file)):
        logger.info("Directorio: " + os.path.join(path,file))
        progreso.create("Actualizando Bibliotreca.." , "Entrando en directorio: " + os.path.join(path,file))
        update2json(item,os.path.join(path,file), progreso)
      else:
        logger.info("Archivo: " + os.path.join(path,file))
        
        if file.endswith(".strm"):
          progreso.create("Actualizando Bibliotreca.." , "Actualizando: " + os.path.join(path,file))
          strm= open(os.path.join(path,file), "rb").read()
          
          item = extract_parameters(strm)
          logger.info(item.tostring())
          logger.info(Item().tostring())
          #Si el item es igual a un item en blanco, significa que no se ha podido extraer los parametros,
          #lo cual quiere decir que probablemente ya esta actualizado, por tanto se omite
          if not item.tourl() == Item().tourl():
            open(os.path.join(path,file), "wb").write(sys.argv[0] + "?" + item.tourl())
    if Main == True:        
      progreso.close()
      xbmcgui.Dialog().ok("Actualizando Bibliotreca..","Actualizaci�n terminada...")
        

def get_params(strm):
    logger.info("get_params")
    
    param_string = strm.split("?")[1]
    
    logger.info("get_params "+str(param_string))
    
    commands = {}

    if param_string:
        split_commands = param_string[param_string.find('?') + 1:].split('&')
    
        for command in split_commands:
            logger.info("get_params command="+str(command))
            if len(command) > 0:
                if "=" in command:
                    split_command = command.split('=')
                    key = split_command[0]
                    value = split_command[1] #urllib.unquote_plus()
                    commands[key] = value
                else:
                    commands[command] = ""
    
    logger.info("get_params "+repr(commands))
    return commands

# Extract parameters from sys.argv
def extract_parameters(strm):
    from core.item import Item
    item = Item()
    params = get_params(strm)


    if (params.has_key("channel")):
        item.channel = urllib.unquote_plus( params.get("channel") )

    
    # Extrae la url de la p?na
    if (params.has_key("url")):
        item.url = urllib.unquote_plus( params.get("url") )


    # Extrae la accion
    if (params.has_key("action")):
        item.action = params.get("action")


    # Extrae el server
    if (params.has_key("server")):
        item.server = params.get("server")
 

    # Extrae la categoria
    if (params.has_key("category")):
        item.category = urllib.unquote_plus( params.get("category") )

            
    # Extrae el t?lo de la serie
    if (params.has_key("show")):
        item.show = params.get("show")


    # Extrae el t?lo del video
    if params.has_key("title"):
        item.title = urllib.unquote_plus( params.get("title") )


    # Extrae el t?lo del video
    if params.has_key("fulltitle"):
        item.fulltitle = urllib.unquote_plus( params.get("fulltitle") )


    if params.has_key("thumbnail"):
        item.thumbnail = urllib.unquote_plus( params.get("thumbnail") )


    if params.has_key("fanart"):                                                                                                                                                
        item.fanart = urllib.unquote_plus( params.get("fanart") )                                                                                                                  


    if params.has_key("plot"):
        item.plot = urllib.unquote_plus( params.get("plot") )


    if params.has_key("extradata"):
        item.extra = urllib.unquote_plus( params.get("extradata") )


    if params.has_key("subtitle"):
        item.subtitle = urllib.unquote_plus( params.get("subtitle") )


    if params.has_key("viewmode"):
        item.viewmode = urllib.unquote_plus( params.get("viewmode") )


    if params.has_key("password"):
        item.password = urllib.unquote_plus( params.get("password") )


    if params.has_key("show"):
        item.show = urllib.unquote_plus( params.get("show") )
    else:
        if params.has_key("Serie"):
            item.show = urllib.unquote_plus( params.get("Serie") )

    return item

############################################################################################  
#fin de codigo para actualizar strm al nuevo formato de url


    
def update(total,errores=0, nuevos=0, serie="No indicada"):
    logger.info("[library.py] update")
    """Pide Resumen de actualización. Además pregunta y actualiza la Biblioteca
    
    nuevos: Número de episodios actualizados. Se muestra como resumen en la ventana 
            de confirmación.
    total:  Número de episodios Totales en la Biblioteca. Se muestra como resumen 
            en la ventana de confirmación.
    Erores: Número de episodios que no se pudo añadir (generalmente por caracteres 
            no válidos en el nombre del archivo o por problemas de permisos.
    """
    
    if nuevos == 1:
        texto = 'Se ha añadido 1 episodio a la Biblioteca (%d en total)' % (total,)
    else:
        texto = 'Se han añadido %d episodios a la Biblioteca (%d en total)' % (nuevos,total)

    logger.info("[library.py] update - %s" % texto)
    advertencia = xbmcgui.Dialog()

    # Pedir confirmación para actualizar la biblioteca
    if nuevos > 0:
        logger.info("[library.py] update - nuevos")
        if errores == 0:
            actualizar = advertencia.yesno('pelisalacarta' , texto ,'¿Deseas que actualice ahora la Biblioteca?')
        else:  # Si hubo errores muestra una línea adicional en la pregunta de actualizar biblioteca
            if errores == 1:
                texto2 = '(No se pudo añadir 1 episodio)'
            else:
                texto2 = '(No se pudieron añadir '+str(errores)+' episodios)'
            actualizar = advertencia.yesno('pelisalacarta' , texto , texto2 , '¿Deseas que actualice ahora la Biblioteca?')
    else: #No hay episodios nuevos -> no actualizar
        logger.info("[library.py] update - no nuevos")
        if errores == 0:
            texto2 = ""
        elif errores == 1:
            texto2 = '(No se pudo añadir 1 episodio)'
        else:
            texto2 = '(No se pudieron añadir '+str(errores)+' episodios)'
        #advertencia.ok('pelisalacarta',texto,texto2)
        actualizar = False
    
    if actualizar:
        logger.info("Actualizando biblioteca...")
        xbmc.executebuiltin('UpdateLibrary(video)')
    else:
        logger.info("No actualiza biblioteca...")

    logger.info ('[Library update] Serie: "%s". Total: %d, Erroneos: %d, Nuevos: %d' %(serie, total, errores, nuevos))

def MonitorSerie ( canal, accion, server, url, serie): 
    ''' Añade una serie a la lista de series a monitorizar.
    
    Si se configura para que lo haga pelisalacarta arrancará un proceso al inicio de XBMC
    para monitorizar las series que se desee mediante una llamada a esta función.
    Los episodios nuevos que vayan apareciendo en la web del canal para la serie indicada
    se irán añdiendo a la biblioteca.
    Para dejar de monitorizar una serie llamar a StopMonitorSerie
    '''
    parser = xml.parsers.expat.ParserCreate()
    
    
def fixStrmLibrary(path = LIBRARY_PATH):
    '''Revisa todos los ficheros strm de la librería y repara la url del plugin
    
    Este cambio es necesario con el paso a XBMC Dharma (10.5) donde las url de
    plugin cambiaron de:
      plugin://video/pelisalacarta/
    a: 
      plugin://plugin.video.pelisalacarta/
    dado que esto podría volver a pasar (en ciertos momentos se ha estado
    experimentando con urls del tipo addon://... hemos decidido crear esta función
    para arreglar los strm en cualquier momento.
    '''
    logger.info("[library.py] fixStrm")
    logger.info("[library.py] fixStrm path="+path)
    # Comprobamos la validez del parámetro
    if not os.path.exists(path):
        logger.info("[library.py] fixStrm ERROR: PATH NO EXISTE")
        return 0
    if not os.path.isdir(path):
        logger.info("[library.py] fixStrm ERROR: PATH NO ES DIRECTORIO")
        return 0
    else:
        logger.info("[library.py] fixStrm El path es un directorio")
    total,errores = 0,0 
    for dirpath, dirnames, filenames in os.walk(path):
        for file in filenames:
            if file[-5:] == '.strm':
                if fixStrm (os.path.join(dirpath,file)):
                    total = total + 1
                else:
                    logger.info("[library.py] fixStrm ERROR al fixear "+file)
                    errores = errores + 1
        #Excluye las carpetas de Subversión de la búsqueda
        if ".svn" in dirnames:
            dirnames.remove (".svn")
    return total,errores
   
def fixStrm (file):
    logger.info("[library.py] fixStrm file: "+file)
    url = LeeStrm (file)
    if len(url)==0:
        return False
    args = url.split('?',1)
    url2 = '%s?%s' % (sys.argv[ 0 ],args [1])
    logger.info ("[library.py] fixStrm new url: "+url2)
    return SaveStrm (file,url2)
    
def LeeStrm(file):
    try:
        fp = open(file,'r')
        data = fp.read()
        fp.close()
    except:
        data = ""
    return data

def SaveStrm (file, data):
    try:
        LIBRARYfile = open(file,"w")
        LIBRARYfile.write(data)
        LIBRARYfile.flush()
        LIBRARYfile.close()
    except IOError:
        logger.info("Error al grabar el archivo "+file)
        return False
    return True


def dlog (text):
    if DEBUG:

        logger.info(text)
