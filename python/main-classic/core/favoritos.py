# -*- coding: iso-8859-1 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Lista de vídeos favoritos
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urllib
import os
import sys
import downloadtools
import config
import logger
import samba
from item import Item

CHANNELNAME = "favoritos"
DEBUG = True
BOOKMARK_PATH = config.get_setting( "bookmarkpath" )

if not BOOKMARK_PATH.upper().startswith("SMB://"):
    if BOOKMARK_PATH=="":
        BOOKMARK_PATH = os.path.join( config.get_data_path() , "bookmarks" )
    if not os.path.exists(BOOKMARK_PATH):
        logger.debug("[favoritos.py] Path de bookmarks no existe, se crea: "+BOOKMARK_PATH)
        os.mkdir(BOOKMARK_PATH)

logger.info("[favoritos.py] path="+BOOKMARK_PATH)

def isGeneric():
    return True

def mainlist(item):
    logger.info("[favoritos.py] mainlist")
    itemlist=[]

    # Crea un listado con las entradas de favoritos
    if usingsamba(BOOKMARK_PATH):
        ficheros = samba.get_files(BOOKMARK_PATH)
    else:
        ficheros = os.listdir(BOOKMARK_PATH)
    
    # Ordena el listado por nombre de fichero (orden de incorporación)
    ficheros.sort()
    
    # Rellena el listado
    for fichero in ficheros:

        try:
            # Lee el bookmark
            item = readbookmark(fichero)
            item.channel="favoritos"
            item.action = "play"
            item.extra = os.path.join( BOOKMARK_PATH, fichero )
            itemlist.append(item)
        except:
            for line in sys.exc_info():
                logger.error( "%s" % line )
    
    return itemlist

def readbookmark(filename,readpath=BOOKMARK_PATH):
    logger.info("[favoritos.py] readbookmark")

    if usingsamba(readpath):
        bookmarkfile = samba.get_file_handle_for_reading(filename, readpath)
    else:
        filepath = os.path.join( readpath , filename )

        # Lee el fichero de configuracion
        logger.info("[favoritos.py] filepath="+filepath)
        bookmarkfile = open(filepath)
    
    #Formato JSON
    if filename.endswith(".json"):
      logger.info("[favoritos.py] Formato: JSON")
      import json
      file = bookmarkfile.read()
      bookmarkfile.close()
      JSONFile = json.loads(file)
      item = Item().fromjson(file)
      
    else:
      #No es json
      lines = bookmarkfile.readlines()
      bookmarkfile.close()
      logger.info("[favoritos.py] Formato: TXT, Lineas: " + str(len(lines)))

      item = Item()
      try:
          item.title = urllib.unquote_plus(lines[0].strip())
      except:
          item.title = lines[0].strip()
      
      try:
          item.url = urllib.unquote_plus(lines[1].strip())
      except:
          item.url = lines[1].strip()
      
      try:
          item.thumbnail = urllib.unquote_plus(lines[2].strip())
      except:
          item.thumbnail = lines[2].strip()
      
      try:
          item.server = urllib.unquote_plus(lines[3].strip())
      except:
          item.server = lines[3].strip()
          
      try:
          item.plot = urllib.unquote_plus(lines[4].strip())
      except:
          item.plot = lines[4].strip()

      ## Campos fulltitle y canal añadidos
      if len(lines)>=6:
          try:
              item.fulltitle = urllib.unquote_plus(lines[5].strip())
          except:
              item.fulltitle = lines[5].strip()
      else:
          item.fulltitle=item.title

      if len(lines)>=7:
          try:
              item.channel = urllib.unquote_plus(lines[6].strip())
          except:
              item.channel = lines[6].strip()
      else:
          item.channel=""

      #Si no es JSON lo elimina
      deletebookmark(filename)
      #Y lo vuelve a crear, esta vez en json
      savebookmark(item)

    return item

def savebookmark(item,savepath=BOOKMARK_PATH):
    logger.info("[favoritos.py] savebookmark(path="+savepath+")")

    # Crea el directorio de favoritos si no existe
    if not usingsamba(savepath):
        try:
            os.mkdir(savepath)
        except:
            pass

    # Lee todos los ficheros
    if usingsamba(savepath):
        ficheros = samba.get_files(savepath)
    else:
        ficheros = os.listdir(savepath)
    ficheros.sort()
    
    # Averigua el último número
    if len(ficheros)>0:
        # XRJ: Linea problemática, sustituida por el bucle siguiente
        #filenumber = int( ficheros[len(ficheros)-1][0:-4] )+1
        filenumber = 1
        for fichero in ficheros:
            logger.info("[favoritos.py] fichero="+fichero)
            try:
                tmpfilenumber = int( fichero[0:8] )+1
                if tmpfilenumber > filenumber:
                    filenumber = tmpfilenumber
            except:
                pass
    else:
        filenumber=1


    # Genera el nombre de fichero
    from core import scrapertools
    filename = '%08d-%s.json' % (filenumber,scrapertools.slugify(item.fulltitle))
    logger.info("[favoritos.py] savebookmark filename="+filename)

    # Graba el fichero
    if not usingsamba(savepath):
        fullfilename = os.path.join(savepath,filename)
        bookmarkfile = open(fullfilename,"w")
        bookmarkfile.write(item.tojson())
        bookmarkfile.flush();
        bookmarkfile.close()
    else:
        samba.write_file(filename, item.tojson(), savepath)

def deletebookmark(fullfilename,deletepath=BOOKMARK_PATH):
    logger.info("[favoritos.py] deletebookmark(fullfilename="+fullfilename+",deletepath="+deletepath+")")

    if not usingsamba(deletepath):
        os.remove( os.path.join( urllib.unquote_plus( deletepath ) , urllib.unquote_plus( fullfilename )))
    else:
        fullfilename = fullfilename.replace("\\","/")
        partes = fullfilename.split("/")
        filename = partes[len(partes)-1]
        logger.info("[favoritos.py] filename="+filename)
        logger.info("[favoritos.py] deletepath="+deletepath)
        samba.remove_file(filename,deletepath)

def usingsamba(path):
    return path.upper().startswith("SMB://")
