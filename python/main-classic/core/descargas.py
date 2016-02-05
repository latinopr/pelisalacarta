# -*- coding: iso-8859-1 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Lista de vídeos descargados
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os
import sys

from core import config
from core import logger
from core import samba
from core import favoritos
from core.item import Item
from core import downloadtools
from servers import servertools

CHANNELNAME = "descargas"
DEBUG = True

DOWNLOAD_LIST_PATH = config.get_setting("downloadlistpath")
IMAGES_PATH = os.path.join( config.get_runtime_path(), 'resources' , 'images' )
ERROR_PATH = os.path.join( DOWNLOAD_LIST_PATH, 'error' )
usingsamba = DOWNLOAD_LIST_PATH.upper().startswith("SMB://")

def isGeneric():
    return True

def mainlist(item):
    logger.info("[descargas.py] mainlist")
    itemlist=[]

    # Lee la ruta de descargas
    downloadpath = config.get_setting("downloadpath")

    logger.info("[descargas.py] downloadpath=" + downloadpath)

    itemlist.append( Item( channel="descargas", action="pendientes", title="Descargas pendientes"))
    itemlist.append( Item( channel="descargas", action="errores", title="Descargas con error"))

    # Añade al listado de XBMC
    try:
        ficheros = os.listdir(downloadpath)
        for fichero in ficheros:
            logger.info("[descargas.py] fichero=" + fichero)
            if fichero!="lista" and fichero!="error" and fichero!=".DS_Store" and not fichero.endswith(".nfo") and not fichero.endswith(".tbn") and os.path.join(downloadpath,fichero)!=config.get_setting("downloadlistpath"):
                url = os.path.join( downloadpath , fichero )
                if not os.path.isdir(url):
                    itemlist.append( Item( channel="descargas", action="play", title=fichero, fulltitle=fichero, url=url, server="local", folder=False))

    except:
        logger.info("[descargas.py] exception on mainlist")
        pass

    return itemlist

def pendientes(item):
    logger.info("[descargas.py] pendientes")
    itemlist=[]

    # Crea un listado con las entradas de favoritos
    if usingsamba:
        ficheros = samba.get_files(DOWNLOAD_LIST_PATH)
    else:
        ficheros = os.listdir(DOWNLOAD_LIST_PATH)

    # Ordena el listado por orden de incorporación
    ficheros.sort()
    
    # Crea un listado con las entradas de la lista de descargas
    for fichero in ficheros:
        logger.info("fichero="+fichero)
        try:
            # Lee el bookmark
            item = favoritos.readbookmark(fichero,DOWNLOAD_LIST_PATH)               

            
            item.channel="descargas"
            item.action="play"
            item.extra = os.path.join( DOWNLOAD_LIST_PATH, fichero )
            item.folder = False
            # Crea la entrada
            # En la categoría va el nombre del fichero para poder borrarlo
            itemlist.append(item)

        except:
            pass
            logger.info("[descargas.py] error al leer bookmark")
            for line in sys.exc_info():
                logger.error( "%s" % line )

    itemlist.append( Item( channel=CHANNELNAME , action="downloadall" , title="(Empezar la descarga de la lista)", thumbnail=os.path.join(IMAGES_PATH, "Crystal_Clear_action_db_update.png") , folder=False ))

    return itemlist

def errores(item):
    logger.info("[descargas.py] errores")
    itemlist=[]

    # Crea un listado con las entradas de favoritos
    if usingsamba:
        ficheros = samba.get_files(ERROR_PATH)
    else:
        ficheros = os.listdir(ERROR_PATH)

    # Ordena el listado por orden de incorporación
    ficheros.sort()
    
    # Crea un listado con las entradas de la lista de descargas
    for fichero in ficheros:
        logger.info("[descargas.py] fichero="+fichero)
        try:
            # Lee el bookmark
            item = favoritos.readbookmark(fichero,ERROR_PATH)
            
            item.channel="descargas"
            item.action="play"
            item.extra = os.path.join( ERROR_PATH, fichero )
            item.folder = False
            logger.info(item.tostring())
            # Crea la entrada
            # En la categoría va el nombre del fichero para poder borrarlo
            itemlist.append(item)
        except:
            pass
            logger.info("[descargas.py] error al leer bookmark")
            for line in sys.exc_info():
                logger.error( "%s" % line )

    return itemlist

def downloadall(item):
    logger.info("[descargas.py] downloadall")

    # Lee la lista de ficheros
    if usingsamba:
        ficheros = samba.get_files(DOWNLOAD_LIST_PATH)
    else:
        ficheros = os.listdir(DOWNLOAD_LIST_PATH)

    logger.info("[descargas.py] numero de ficheros=%d" % len(ficheros))

    # La ordena
    ficheros.sort()
    
    # Crea un listado con las entradas de favoritos
    for fichero in ficheros:
        # El primer video de la lista
        logger.info("[descargas.py] fichero="+fichero)

        if fichero!="error" and fichero!=".DS_Store":
            # Descarga el vídeo
            try:
                # Lee el bookmark
                item = favoritos.readbookmark(fichero,DOWNLOAD_LIST_PATH)
                logger.info("[descargas.py] url="+item.url)

                # Averigua la URL del vídeo
                video_urls,puedes,motivo = servertools.resolve_video_urls_for_playing(item.server,item.url,"",False)

                # La última es la de mayor calidad, lo mejor para la descarga
                mediaurl = video_urls[ len(video_urls)-1 ][1]
                logger.info("[descargas.py] mediaurl="+mediaurl)

                # Genera el NFO
                nfofilepath = downloadtools.getfilefromtitle("sample.nfo",item.fulltitle)
                outfile = open(nfofilepath,"w")
                outfile.write("<movie>\n")
                outfile.write("<title>("+item.fulltitle+")</title>\n")
                outfile.write("<originaltitle></originaltitle>\n")
                outfile.write("<rating>0.000000</rating>\n")
                outfile.write("<year>2009</year>\n")
                outfile.write("<top250>0</top250>\n")
                outfile.write("<votes>0</votes>\n")
                outfile.write("<outline></outline>\n")
                outfile.write("<plot>"+item.plot+"</plot>\n")
                outfile.write("<tagline></tagline>\n")
                outfile.write("<runtime></runtime>\n")
                outfile.write("<thumb></thumb>\n")
                outfile.write("<mpaa>Not available</mpaa>\n")
                outfile.write("<playcount>0</playcount>\n")
                outfile.write("<watched>false</watched>\n")
                outfile.write("<id>tt0432337</id>\n")
                outfile.write("<filenameandpath></filenameandpath>\n")
                outfile.write("<trailer></trailer>\n")
                outfile.write("<genre></genre>\n")
                outfile.write("<credits></credits>\n")
                outfile.write("<director></director>\n")
                outfile.write("<actor>\n")
                outfile.write("<name></name>\n")
                outfile.write("<role></role>\n")
                outfile.write("</actor>\n")
                outfile.write("</movie>")
                outfile.flush()
                outfile.close()
                logger.info("[descargas.py] Creado fichero NFO")
                
                # Descarga el thumbnail
                if item.thumbnail != "":
                   logger.info("[descargas.py] thumbnail="+item.thumbnail)
                   thumbnailfile = downloadtools.getfilefromtitle(item.thumbnail,item.fulltitle)
                   thumbnailfile = thumbnailfile[:-4] + ".tbn"
                   logger.info("[descargas.py] thumbnailfile="+thumbnailfile)
                   try:
                       downloadtools.downloadfile(item.thumbnail,thumbnailfile)
                       logger.info("[descargas.py] Thumbnail descargado")
                   except:
                       logger.info("[descargas.py] error al descargar thumbnail")
                       for line in sys.exc_info():
                           logger.error( "%s" % line )
                
                # Descarga el video
                #dev = downloadtools.downloadtitle(mediaurl,fulltitle)
                dev = downloadtools.downloadbest(video_urls,item.fulltitle)
                if dev == -1:
                    # El usuario ha cancelado la descarga
                    logger.info("[descargas.py] Descarga cancelada")
                    return
                elif dev == -2:
                    # Error en la descarga, lo mueve a ERROR y continua con el siguiente
                    logger.info("[descargas.py] ERROR EN DESCARGA DE "+fichero)
                    if not usingsamba:
                        origen = os.path.join( DOWNLOAD_LIST_PATH , fichero )
                        destino = os.path.join( ERROR_PATH , fichero )
                        import shutil
                        shutil.move( origen , destino )
                    else:
                        favoritos.savebookmark(item, ERROR_PATH)
                        favoritos.deletebookmark(fichero, DOWNLOAD_LIST_PATH)
                else:
                    logger.info("[descargas.py] Video descargado")
                    # Borra el bookmark e itera para obtener el siguiente video
                    filepath = os.path.join( DOWNLOAD_LIST_PATH , fichero )
                    if usingsamba:
                        os.remove(filepath)
                    else:
                        favoritos.deletebookmark(fichero, DOWNLOAD_LIST_PATH)
                    logger.info("[descargas.py] "+fichero+" borrado")
            except:
                logger.info("[descargas.py] ERROR EN DESCARGA DE "+fichero)
                import sys
                for line in sys.exc_info():
                    logger.error( "%s" % line )
                if not usingsamba:
                    origen = os.path.join( DOWNLOAD_LIST_PATH , fichero )
                    destino = os.path.join( ERROR_PATH , fichero )
                    import shutil
                    shutil.move( origen , destino )
                else:
                    favoritos.savebookmark(item,ERROR_PATH)
                    favoritos.deletebookmark(fichero, DOWNLOAD_LIST_PATH)

def savebookmark(item,savepath=DOWNLOAD_LIST_PATH):
    favoritos.savebookmark(item,savepath)

def deletebookmark(fullfilename,deletepath=DOWNLOAD_LIST_PATH):
    favoritos.deletebookmark(fullfilename,deletepath)

def delete_error_bookmark(fullfilename,deletepath=ERROR_PATH):
    favoritos.deletebookmark(fullfilename,deletepath)

def mover_descarga_error_a_pendiente(fullfilename):
    # La categoría es el nombre del fichero en favoritos, así que lee el fichero
    item = favoritos.readbookmark(fullfilename,"")
    # Lo añade a la lista de descargas
    savebookmark(item)
    # Y lo borra de la lista de errores
    os.remove(fullfilename)
