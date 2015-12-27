# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta
# Generic Launcher
# http://blog.tvalacarta.info/plugin-xbmc/
#------------------------------------------------------------

import os
import sys
from core.item import Item
from core import logger
from core import config
from platformcode import platformtools
from core import channeltools

def start():
    ''' Primera funcion que se ejecuta al entrar en el plugin.
    Dentro de esta funcion deberian ir todas las llamadas a las
    funciones que deseamos que se ejecuten nada mas abrir el plugin.
    
    '''
    logger.info("pelisalacarta.platformcode.launcher start")
    
    # Test if all the required directories are created
    config.verify_directories_created()
      

def run(item):
    itemlist = []
    #Muestra el item en el log:
    PrintItems(item)
    
    #Control Parental, comprueba si es adulto o no
    if item.action=="mainlist":
      # Parental control
      if channeltools.is_adult(item.channel) and config.get_setting("adult_pin")!="":
        tecleado = platformtools.InputDialog("PIN para canales de adultos","",True)
        if not tecleado==config.get_setting("adult_pin"):
          return

    #Importa el canal para el item, todo item debe tener un canal, sino sale de la función
    if item.channel: channelmodule = ImportarCanal(item)
    else: return []

    #Action Play, para mostrar el menú con las opciones de reproduccion.
    if item.action=="play":
      logger.info("pelisalacarta.platformcode.launcher play")
      # Si el canal tiene una acción "play" tiene prioridad
      if hasattr(channelmodule, 'play'):
          logger.info("pelisalacarta.platformcode.launcher executing channel 'play' method")
          itemlist = channelmodule.play(item)
          if len(itemlist)>0:
              play_menu(itemlist)
          else:
              platformtools.AlertDialog("plugin", "No hay nada para reproducir")
      else:
          logger.info("pelisalacarta.platformcode.launcher no channel 'play' method, executing core method")
          play_menu(item)
          
      itemlist = None

      
    #Action Search, para mostrar el teclado y lanzar la busqueda con el texto indicado. 
    elif item.action=="search":
      logger.info("pelisalacarta.platformcode.launcher search")
      tecleado = platformtools.InputDialog()
      if not tecleado is None:
          itemlist = channelmodule.search(item,tecleado)
      else:
          itemlist = []
      
    #Todas las demas las intenta ejecturaren el siguiente orden:
    # 1. En el canal
    # 2. En el launcher
    # 3. Si no existe en el canal ni en el launcher guarda un error en el log
    else:
      #Si existe la funcion en el canal la ejecuta
      if hasattr(channelmodule, item.action):
        logger.info("Ejectuando accion: " + item.channel + "." + item.action + "(item)")
        exec "itemlist = channelmodule." + item.action + "(item)"
        
      #Si existe la funcion en el launcher la ejecuta
      elif hasattr(sys.modules[__name__], item.action):
        logger.info("Ejectuando accion: " + item.action + "(item)")
        exec "itemlist =" + item.action + "(item)"
        
      #Si no existe devuelve un error
      else:
          logger.info("No se ha encontrado la accion ["+ item.action + "] en el canal ["+item.channel+"] ni en el launcher")
          
     
          
    #Llegados a este punto ya tenemos que tener el itemlist con los resultados correspondientes
    #Pueden darse 3 escenarios distintos:
    # 1. la función ha generado resultados y estan en el itemlist
    # 2. la función no ha generado resultados y por tanto el itemlist contiene 0 items, itemlist = []
    # 3. la función realiza alguna accion con la cual no se generan nuevos items, en ese caso el resultado deve ser: itemlist = None para que no modifique el listado
    #A partir de aquí ya se ha ejecutado la funcion en el lugar adecuado, si queremos realizar alguna acción sobre los resultados, este es el lugar.
          
    
     
    #Filtrado de Servers      
    if item.action== "findvideos" and config.get_setting('filter_servers') == 'true': 
      server_white_list, server_black_list = set_server_list() 
      itemlist = filtered_servers(itemlist, server_white_list, server_black_list) 
      
    
    #Si la accion no ha devuelto ningún resultado, añade un item con el texto "No hay elementos para mostrar"              
    if type(itemlist)==list:
      if  len(itemlist) ==0:
        itemlist = [Item(title="No hay elementos para mostrar", thumbnail=os.path.join(config.get_runtime_path() , "resources" , "images" , "thumb_error.png" ))]

    #Si la accion ha devuelto resultados:
    if type(itemlist)==list:
    
      #Añade los menus contextuales a los items
      for x in range(len(itemlist)):
        itemlist[x].context = AddContext(itemlist[x])
        
      #Imprime en el log el resultado
      PrintItems(itemlist)
      
      #Muestra los resultados en pantalla
      platformtools.renderItems(itemlist, item)


def ImportarCanal(item):
  channel = item.channel
  channelmodule=""
  if os.path.exists(os.path.join( config.get_runtime_path(), "channels",channel+".py")):
    exec "from channels import "+channel+" as channelmodule"
  elif os.path.exists(os.path.join( config.get_runtime_path(),"core",channel+".py")):
    exec "from core import "+channel+" as channelmodule"
  elif os.path.exists(os.path.join( config.get_runtime_path(),channel+".py")):
    exec "import "+channel+" as channelmodule"
  return channelmodule

def PrintItems(itemlist):
  if type(itemlist)==list:
    if len(itemlist) >0:
      logger.info("Items devueltos")  
      logger.info("-----------------------------------------------------------------------")
      for item in itemlist:
        logger.info(item.tostring())
      logger.info("-----------------------------------------------------------------------")
  else:
    item =  itemlist
    logger.info("-----------------------------------------------------------------------")
    logger.info(item.tostring())    
    logger.info("-----------------------------------------------------------------------")
    

'''
Añade los comandos del menu contectual, esta función esta obsoleta, el nuevo formato para item.context es un list con:
{"title": "Titulo del Menu","action": "Accion del menu","channel" : "Canal donde ejecutar la accion"}
y se deven añadir desde el canal.
'''
def AddContext(item):
  contextCommands = []
  if not type(item.context) == list and item.context:
    if item.show != "": #Añadimos opción contextual para Añadir la serie completa a la biblioteca
        contextCommands.append({"title": "Añadir Serie a Biblioteca","action": "addlist2Library"})
    if "1" in item.context and item.action != "por_teclado":
        contextCommands.append({"title": config.get_localized_string( 30300 ),"action": "borrar_busqueda","channel" : "buscador"})
    if "4" in item.context:
        contextCommands.append({"title": "XBMC Subtitle","action": "searchSubtitle","channel" : "subtitletools"})
    if "5" in item.context:
        contextCommands.append({"title": config.get_localized_string( 30162 ),"action": "buscartrailer","channel" : "trailertools"})
    if "6" in item.context:
        contextCommands.append({"title": config.get_localized_string( 30410 ),"action": "play_video","channel" : "justintv"})
    if "8" in item.context:# Añadir canal a favoritos justintv
        contextCommands.append({"title": config.get_localized_string( 30406 ),"action": "addToFavorites","channel" : "justintv"})
    if "9" in item.context:# Remover canal de favoritos justintv
        contextCommands.append({"title": config.get_localized_string( 30407 ),"action": "removeFromFavorites","channel" : "justintv"})
  return contextCommands
  
def findvideos(item):
    logger.info("pelisalacarta.platformcode.launcher findvideos")
    from servers import servertools
    itemlist = servertools.find_video_items(item)        
    return itemlist

def add_pelicula_to_library(item):
    logger.info("pelisalacarta.platformcode.launcher add_pelicula_to_library")
    from platformcode import library
    # Obtiene el listado desde el que se llamó
    library.savelibrary( titulo=item.fulltitle , url=item.url , thumbnail=item.thumbnail , server=item.server , plot=item.plot , canal=item.channel , category="Cine" , Serie=item.show.strip() , verbose=False, accion="play_from_library", pedirnombre=False, subtitle=item.subtitle )


def add_serie_to_library(item):
    logger.info("pelisalacarta.platformcode.launcher add_serie_to_library, show=#"+item.show+"#")
    from platformcode import library
    import xbmcgui

    # Obtiene el listado desde el que se llamó
    action = item.extra
    
    # Esta marca es porque el item tiene algo más aparte en el atributo "extra"
    if "###" in item.extra:
        action = item.extra.split("###")[0]
        item.extra = item.extra.split("###")[1]

    exec "itemlist = channel."+action+"(item)"

    # Progreso
    pDialog = xbmcgui.DialogProgress()
    ret = pDialog.create('pelisalacarta', 'Añadiendo episodios...')
    pDialog.update(0, 'Añadiendo episodio...')
    totalepisodes = len(itemlist)
    logger.info ("[launcher.py] Total Episodios:"+str(totalepisodes))
    i = 0
    errores = 0
    nuevos = 0
    for item in itemlist:
        i = i + 1
        pDialog.update(i*100/totalepisodes, 'Añadiendo episodio...',item.title)
        logger.info("pelisalacarta.platformcode.launcher add_serie_to_library, title="+item.title)
        if (pDialog.iscanceled()):
            return

        try:
            #(titulo="",url="",thumbnail="",server="",plot="",canal="",category="Cine",Serie="",verbose=True,accion="strm",pedirnombre=True):
            # Añade todos menos el que dice "Añadir esta serie..." o "Descargar esta serie..."
            if item.action!="add_serie_to_library" and item.action!="download_all_episodes":
                nuevos = nuevos + library.savelibrary( titulo=item.title , url=item.url , thumbnail=item.thumbnail , server=item.server , plot=item.plot , canal=item.channel , category="Series" , Serie=item.show.strip() , verbose=False, accion="play_from_library", pedirnombre=False, subtitle=item.subtitle, extra=item.extra )
        except IOError:
            import sys
            for line in sys.exc_info():
                logger.error( "%s" % line )
            logger.info("pelisalacarta.platformcode.launcherError al grabar el archivo "+item.title)
            errores = errores + 1
        
    pDialog.close()
    
    # Actualizacion de la biblioteca
    itemlist=[]
    if errores > 0:
        itemlist.append(Item(title="ERROR, la serie NO se ha añadido a la biblioteca o lo ha hecho incompleta"))
        logger.info ("[launcher.py] No se pudo añadir "+str(errores)+" episodios")
    else:
        itemlist.append(Item(title="La serie se ha añadido a la biblioteca"))
        logger.info ("[launcher.py] Ningún error al añadir "+str(errores)+" episodios")
    
    # FIXME:jesus Comentado porque no funciona bien en todas las versiones de XBMC
    #library.update(totalepisodes,errores,nuevos)
    xbmctools.renderItems(itemlist, params, url, category)
    
    #Lista con series para actualizar
    nombre_fichero_config_canal = os.path.join( config.get_library_path() , "series.xml" )
    if not os.path.exists(nombre_fichero_config_canal):
        nombre_fichero_config_canal = os.path.join( config.get_data_path() , "series.xml" )

    logger.info("nombre_fichero_config_canal="+nombre_fichero_config_canal)
    if not os.path.exists(nombre_fichero_config_canal):
        f = open( nombre_fichero_config_canal , "w" )
    else:
        f = open( nombre_fichero_config_canal , "r" )
        contenido = f.read()
        f.close()
        f = open( nombre_fichero_config_canal , "w" )
        f.write(contenido)
    from platformcode import library
    f.write( library.title_to_folder_name(item.show)+","+item.url+","+item.channel+"\n")
    f.close();


def download_all_episodes(item,first_episode="",preferred_server="vidspot",filter_language=""):
    logger.info("pelisalacarta.platformcode.launcher download_all_episodes, show="+item.show)
    channel = ImportarCanal(item)
    show_title = item.show

    # Obtiene el listado desde el que se llamó
    action = item.extra

    # Esta marca es porque el item tiene algo más aparte en el atributo "extra"
    if "###" in item.extra:
        action = item.extra.split("###")[0]
        item.extra = item.extra.split("###")[1]

    exec "episode_itemlist = channel."+action+"(item)"

    # Ordena los episodios para que funcione el filtro de first_episode
    episode_itemlist = sorted(episode_itemlist, key=lambda Item: Item.title) 

    from servers import servertools
    from core import downloadtools
    from core import scrapertools

    best_server = preferred_server
    worst_server = "moevideos"

    # Para cada episodio
    if first_episode=="":
        empezar = True
    else:
        empezar = False

    for episode_item in episode_itemlist:
        try:
            logger.info("pelisalacarta.platformcode.launcher download_all_episodes, episode="+episode_item.title)
            episode_title = scrapertools.get_match(episode_item.title,"(\d+x\d+)")
            logger.info("pelisalacarta.platformcode.launcher download_all_episodes, episode="+episode_title)
        except:
            import traceback
            logger.info(traceback.format_exc())
            continue

        if first_episode!="" and episode_title==first_episode:
            empezar = True

        if episodio_ya_descargado(show_title,episode_title):
            continue

        if not empezar:
            continue

        # Extrae los mirrors
        try:
            mirrors_itemlist = channel.findvideos(episode_item)
        except:
            mirrors_itemlist = servertools.find_video_items(episode_item)
        print mirrors_itemlist

        descargado = False

        new_mirror_itemlist_1 = []
        new_mirror_itemlist_2 = []
        new_mirror_itemlist_3 = []
        new_mirror_itemlist_4 = []
        new_mirror_itemlist_5 = []
        new_mirror_itemlist_6 = []

        for mirror_item in mirrors_itemlist:
            
            # Si está en español va al principio, si no va al final
            if "(Español)" in mirror_item.title:
                if best_server in mirror_item.title.lower():
                    new_mirror_itemlist_1.append(mirror_item)
                else:
                    new_mirror_itemlist_2.append(mirror_item)
            elif "(Latino)" in mirror_item.title:
                if best_server in mirror_item.title.lower():
                    new_mirror_itemlist_3.append(mirror_item)
                else:
                    new_mirror_itemlist_4.append(mirror_item)
            elif "(VOS)" in mirror_item.title:
                if best_server in mirror_item.title.lower():
                    new_mirror_itemlist_3.append(mirror_item)
                else:
                    new_mirror_itemlist_4.append(mirror_item)
            else:
                if best_server in mirror_item.title.lower():
                    new_mirror_itemlist_5.append(mirror_item)
                else:
                    new_mirror_itemlist_6.append(mirror_item)

        mirrors_itemlist = new_mirror_itemlist_1 + new_mirror_itemlist_2 + new_mirror_itemlist_3 + new_mirror_itemlist_4 + new_mirror_itemlist_5 + new_mirror_itemlist_6

        for mirror_item in mirrors_itemlist:
            logger.info("pelisalacarta.platformcode.launcher download_all_episodes, mirror="+mirror_item.title)

            if "(Español)" in mirror_item.title:
                idioma="(Español)"
                codigo_idioma="es"
            elif "(Latino)" in mirror_item.title:
                idioma="(Latino)"
                codigo_idioma="lat"
            elif "(VOS)" in mirror_item.title:
                idioma="(VOS)"
                codigo_idioma="vos"
            elif "(VO)" in mirror_item.title:
                idioma="(VO)"
                codigo_idioma="vo"
            else:
                idioma="(Desconocido)"
                codigo_idioma="desconocido"

            logger.info("pelisalacarta.platformcode.launcher filter_language=#"+filter_language+"#, codigo_idioma=#"+codigo_idioma+"#")
            if filter_language=="" or (filter_language!="" and filter_language==codigo_idioma):
                logger.info("pelisalacarta.platformcode.launcher download_all_episodes, downloading mirror")
            else:
                logger.info("pelisalacarta.platformcode.launcher language "+codigo_idioma+" filtered, skipping")
                continue

            if hasattr(channel, 'play'):
                video_items = channel.play(mirror_item)
            else:
                video_items = [mirror_item]

            if len(video_items)>0:
                video_item = video_items[0]

                # Comprueba que esté disponible
                video_urls, puedes, motivo = servertools.resolve_video_urls_for_playing( video_item.server , video_item.url , video_password="" , muestra_dialogo=False)

                # Lo añade a la lista de descargas
                if puedes:
                    logger.info("pelisalacarta.platformcode.launcher download_all_episodes, downloading mirror started...")
                    # El vídeo de más calidad es el último
                    mediaurl = video_urls[len(video_urls)-1][1]
                    devuelve = downloadtools.downloadbest(video_urls,show_title+" "+episode_title+" "+idioma+" ["+video_item.server+"]",continuar=False)

                    if devuelve==0:
                        logger.info("pelisalacarta.platformcode.launcher download_all_episodes, download ok")
                        descargado = True
                        break
                    elif devuelve==-1:
                        try:
                            import xbmcgui
                            advertencia = xbmcgui.Dialog()
                            resultado = advertencia.ok("plugin" , "Descarga abortada")
                        except:
                            pass
                        return
                    else:
                        logger.info("pelisalacarta.platformcode.launcher download_all_episodes, download error, try another mirror")
                        continue

                else:
                    logger.info("pelisalacarta.platformcode.launcher download_all_episodes, downloading mirror not available... trying next")

        if not descargado:
            logger.info("pelisalacarta.platformcode.launcher download_all_episodes, EPISODIO NO DESCARGADO "+episode_title)




def set_server_list():
    logger.info("pelisalacarta.platformcode.launcher.set_server_list start")
    server_white_list = []
    server_black_list = []

    if len(config.get_setting('whitelist')) > 0:
        server_white_list_key = config.get_setting('whitelist').replace(', ', ',').replace(' ,', ',')
        server_white_list = re.split(',', server_white_list_key)

    if len(config.get_setting('blacklist')) > 0:
        server_black_list_key = config.get_setting('blacklist').replace(', ', ',').replace(' ,', ',')
        server_black_list = re.split(',', server_black_list_key)

    logger.info("set_server_list whiteList %s" % server_white_list)
    logger.info("set_server_list blackList %s" % server_black_list)
    logger.info("pelisalacarta.platformcode.launcher.set_server_list end")

    return server_white_list, server_black_list

def filtered_servers(itemlist, server_white_list, server_black_list):
    logger.info("pelisalacarta.platformcode.launcher.filtered_servers start")
    new_list = []
    white_counter = 0
    black_counter = 0

    logger.info("filtered_servers whiteList %s" % server_white_list)
    logger.info("filtered_servers blackList %s" % server_black_list)

    if len(server_white_list) > 0:
        logger.info("filtered_servers whiteList")
        for item in itemlist:
            logger.info("item.title " + item.title)
            if any(server in item.title for server in server_white_list):
                # if item.title in server_white_list:
                logger.info("found")
                new_list.append(item)
                white_counter += 1
            else:
                logger.info("not found")

    if len(server_black_list) > 0:
        logger.info("filtered_servers blackList")
        for item in itemlist:
            logger.info("item.title " + item.title)
            if any(server in item.title for server in server_black_list):
                # if item.title in server_white_list:
                logger.info("found")
                black_counter += 1
            else:
                new_list.append(item)
                logger.info("not found")

    logger.info("whiteList server %s has #%d rows" % (server_white_list, white_counter))
    logger.info("blackList server %s has #%d rows" % (server_black_list, black_counter))

    if len(new_list) == 0:
        new_list = itemlist
    logger.info("pelisalacarta.platformcode.launcher.filtered_servers end")

    return new_list


def add_to_favorites(item):
    if "item_action" in item: 
      item.action = item.item_action
      del item.item_action
      
    from core import favoritos
    from core import downloadtools
    if not item.fulltitle: item.fulltitle = item.title
    title = platformtools.InputDialog(default=downloadtools.limpia_nombre_excepto_1(item.fulltitle)+" ["+item.channel+"]")
    if title is not None:
        item.title = title
        favoritos.savebookmark(item)
        platformtools.AlertDialog("Pelisalacarta", config.get_localized_string(30102) +"\n"+ item.title +"\n"+ config.get_localized_string(30108))
    return
    
def remove_from_favorites(item):
    from core import favoritos
    # En "extra" está el nombre del fichero en favoritos
    favoritos.deletebookmark(item.extra)
    platformtools.AlertDialog("Pelisalacarta", config.get_localized_string(30102) +"\n"+ item.title +"\n"+ config.get_localized_string(30105))
    platformtools.ItemlistRefresh()
    return

def download(item):
    from core import downloadtools
    if not item.fulltitle: item.fulltitle = item.title
    title = platformtools.InputDialog(default=item.fulltitle)
    if title is not None:
      devuelve = downloadtools.downloadbest(item.video_urls,title)
    
      if devuelve==0:
          platformtools.AlertDialog("Pelisalacarta", "Descargado con éxito")
      elif devuelve==-1:
          platformtools.AlertDialog("Pelisalacarta", "Descarga abortada")
      else:
          platformtools.AlertDialog("Pelisalacarta", "Error en la descarga")
    return

def add_to_library(item):
    if "item_action" in item: 
      item.action = item.item_action
      del item.item_action

    from platformcode import library
    if not item.fulltitle=="":
        item.title = item.fulltitle
    library.savelibrary(item)
    platformtools.AlertDialog("Pelisalacarta", config.get_localized_string(30101) +"\n"+ item.title +"\n"+ config.get_localized_string(30135))
    return

def add_to_downloads(item):
    if "item_action" in item: 
      item.action = item.item_action
      del item.item_action
      
    from core import descargas
    from core import downloadtools
    if not item.fulltitle: item.fulltitle = item.title
    title = platformtools.InputDialog(default=downloadtools.limpia_nombre_excepto_1(item.fulltitle))
    if title is not None:
      item.title = title
      descargas.savebookmark(item)
        
    platformtools.AlertDialog("Pelisalacarta", config.get_localized_string(30101) +"\n"+ item.title +"\n"+ config.get_localized_string(30109))
    return

def remove_from_downloads(item):
  from core import descargas
  # La categoría es el nombre del fichero en la lista de descargas
  descargas.deletebookmark(item.extra)

  platformtools.AlertDialog("Pelisalacarta", config.get_localized_string(30101) +"\n"+ item.title +"\n"+ config.get_localized_string(30106))
  platformtools.ItemlistRefresh()
  return
  
def delete_file(item):
  os.remove(item.url)
  platformtools.ItemlistRefresh()
  return


def move_to_downloads(item):
  from core import descargas
  descargas.mover_descarga_error_a_pendiente(item.extra)
  platformtools.AlertDialog("Pelisalacarta", config.get_localized_string(30101) +"\n"+ item.title +"\n"+ config.get_localized_string(30101))
  platformtools.ItemlistRefresh()
  return

def remove_from_downloads_error(item):
  from core import descargas
  descargas.mover_descarga_error_a_pendiente(item.extra)

  platformtools.AlertDialog("Pelisalacarta", config.get_localized_string(30101) +"\n"+ item.title +"\n"+ config.get_localized_string(30107))
  platformtools.ItemlistRefresh()
  return

def send_to_jdownloader(item):
  #d = {"web": url}urllib.urlencode(d)
  from core import scrapertools
  if item.subtitle!="":
      data = scrapertools.cachePage(config.get_setting("jdownloader")+"/action/add/links/grabber0/start1/web="+item.url+ " " +item.thumbnail + " " + item.subtitle)
  else:
      data = scrapertools.cachePage(config.get_setting("jdownloader")+"/action/add/links/grabber0/start1/web="+item.url+ " " +item.thumbnail)
  return

def send_to_pyload(item):
  logger.info("Enviando a pyload...")
  
  if item.Serie!="":
      package_name = item.Serie
  else:
      package_name = "pelisalacarta"

  from core import pyload_client
  pyload_client.download(url=item.url,package_name=package_name)
  return

def search_trailer(item):
  config.set_setting("subtitulo", "false")
  import sys
  item.channel = "trailertools"
  item.action ="buscartrailer"
  run(item)
  return

#Crea la lista de opciones para el menu de reproduccion
def check_video_options(item, video_urls):
  itemlist = []
  #Opciones Reproducir
  playable = (len(video_urls) > 0)
  
  for video_url in video_urls:
    itemlist.append(item.clone(option=config.get_localized_string(30151) + " " + video_url[0], video_url= video_url[1], action="play_video"))
  
  if item.server=="local":                            
    itemlist.append(item.clone(option=config.get_localized_string(30164), action="delete_file"))
  if not item.server=="local" and playable:           
    itemlist.append(item.clone(option=config.get_localized_string(30153), action="download", video_urls = video_urls))

  if item.channel=="favoritos":                       
    itemlist.append(item.clone(option=config.get_localized_string(30154), action="remove_from_favorites"))
  if not item.channel=="favoritos" and playable:      
    itemlist.append(item.clone(option=config.get_localized_string(30155), action="add_to_favorites", item_action = item.action))

  if not item.strmfile and playable:                  
    itemlist.append(item.clone(option=config.get_localized_string(30161), action="add_to_library", item_action = item.action))

  if item.channel!="descargas" and playable:          
    itemlist.append(item.clone(option=config.get_localized_string(30157), action="add_to_downloads", item_action = item.action))
  if not item.channel!="descargas" and item.category=="errores":
    itemlist.append(item.clone(option=config.get_localized_string(30159), action="remove_from_downloads_error"))
  if not item.channel!="descargas" and item.category=="errores" and playable:
    itemlist.append(item.clone(option=config.get_localized_string(30160), action="move_to_downloads"))
  if not item.channel!="descargas" and not item.category=="errores":
    itemlist.append(item.clone(option=config.get_localized_string(30156), action="remove_from_downloads"))

  if config.get_setting("jdownloader_enabled")=="true" and playable:
    itemlist.append(item.clone(option=config.get_localized_string(30158), action="send_to_jdownloader"))
  if config.get_setting("pyload_enabled")=="true" and playable:
    itemlist.append(item.clone(option=config.get_localized_string(30158).replace("jdownloader","pyLoad"), action="send_to_pyload")) 
    
  if not item.channel in ["Trailer","ecarteleratrailers"] and playable:
    itemlist.append(item.clone(option=config.get_localized_string(30162), action="search_trailer"))
    
  return itemlist

#play_menu, abre el menu con las opciones para reproducir
def play_menu(item):
    from servers import servertools

    if type(item) ==list and len(item)==1:
      item = item[0]
      
    #Modo Normal
    if type(item) == Item: 
      if item.server=="": item.server="directo"
      video_urls,puedes,motivo = servertools.resolve_video_urls_for_playing(item.server,item.url,item.password,True)
      
    #Modo "Play" en canal, puede devolver varias url
    elif type(item) ==list and len(item)>1:
    
      itemlist = item     #En este caso en el argumento item, en realidad hay un itemlist
      item = itemlist[0]  #Se asigna al item, el item primero del itemlist
      
      video_urls = []
      for videoitem in itemlist:
        if videoitem.server=="": videoitem.server="directo"
        opcion_urls,puedes,motivo = servertools.resolve_video_urls_for_playing(videoitem.server,videoitem.url)
        opcion_urls[0][0] = opcion_urls[0][0] + " [" + videoitem.fulltitle + "]"
        video_urls.extend(opcion_urls)
      item = itemlist[0]
      puedes = True
      motivo = ""
      
      
    if not "strmfile" in item: item.strmfile=False   
    #TODO: unificar show y Serie ya que se usan indistintamente.
    if not "Serie" in item: item.Serie = item.show
    if item.server=="": item.server="directo"
    
    opciones = check_video_options(item, video_urls)
    if not puedes:
      if item.server!="directo":
        motivo = motivo.replace("<br/>", "\n")
        platformtools.AlertDialog("No puedes ver ese vídeo porque...",motivo+"\n"+item.url)
      else:
        platformtools.AlertDialog("No puedes ver ese vídeo porque...","El servidor donde está alojado no está\nsoportado en pelisalacarta todavía\n"+item.url)

    if len(opciones)==0:
        return
        
    default_action = config.get_setting("default_action")
    logger.info("default_action="+default_action)
    # Si la accion por defecto es "Preguntar", pregunta
    if default_action=="0":
        seleccion = platformtools.SelectDialog(config.get_localized_string(30163), [opcion.option for opcion in opciones])
    elif default_action=="1":
        seleccion = 0
    elif default_action=="2":
        seleccion = len(video_urls)-1
    elif default_action=="3":
        seleccion = seleccion
    else:
        seleccion=0

    if seleccion > -1:
      logger.info("seleccion=%d" % seleccion)
      logger.info("seleccion=%s" % opciones[seleccion].option)
      selecteditem = opciones[seleccion]
      del selecteditem.option
      run(opciones[seleccion])

    return

#play_video, Llama a la función especifica de la plataforma para reproducir
def play_video(item):
    from platformcode import platformtools
    platformtools.PlayVideo(item) 