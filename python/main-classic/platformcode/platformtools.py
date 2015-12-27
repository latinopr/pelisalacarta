# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# platformtools
# Herramienta para trabajar con la plataforma, Version KODI
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# ------------------------------------------------------------
'''
Dialogos:
  ProgressDialog:
    Descripcion:
      Muestra un cuadro de dialgo de progreso, con un boton para cancelar.
    Uso:
      dialogo = ProgressDialog(title, text, percent)      <- Muestra el dialogo
      dialogo.update(percent, text)                       <- Actualiza el progreso
      dialogo.iscanceled()                                <- Devuelve True si el usuario ha cancelado
      dialogo.close()                                     <- Cierra el dialogo

  ProgressDialogBG
    Descripcion:
      Muestra un cuadro de dialgo de progreso en segundo plano.
    Uso:
      dialogo = ProgressDialogBG(title, text, percent)    <- Muestra el dialogo
      dialogo.update(percent, text)                       <- Actualiza el progreso
      dialogo.iscanceled()                                <- Devuelve siempre False, creado para mantener la estructura del ProgressDialog
      dialogo.close()                                     <- Cierra el dialogo

  AlertDialog
    Descripcion:
      Muestra un cuadro de dialgo con un boton para Aceptar.
    Uso:
      AlertDialog(title, text)                            <- Muestra el dialogo

  YesNoDialog
    Descripcion:
      Muestra un cuadro de dialgo con dos botones, Si / No.
    Uso:
      resultado = YesNoDialog(title, text)                <- Muestra el dialogo y devuelve True si presiona en SI y False si presiona en No

  SelectDialog
    Descripcion:
      Muestra un cuadro de dialgo con una lista de opciones para seleccionar.
    Uso:
      resultado = YesNoDialog(title, text)                <- Muestra el dialogo y devuelve la opcion seleccionada, -1 si no se selecciona nada

  InputDialog
    Descripcion:
      Muestra un cuadro de dialgo para introducir texto. Si password = True, oculta los caracteres
    Uso:
      resultado = InputDialog(title, default, password)   <- Muestra el dialogo y devuelve el texto introducido, None si se presiona en cancelar

Itemlist:
  ItemlistRefresh
    Descripcion:
      Vuelve a cargar la ultima petición
    Uso:
      ItemlistRefresh()                                   <- Recargarga el listado

  ItemlistUpdate
    Descripcion:
      Ejecuta el item pasado y carga el resultado
    Uso:
      ItemlistUpdate(item)                                <- Carga el item

  renderItems
    Descripcion:
      Función encargada de cargar el itemlist, hay que pasarle el itemlist y el item "padre"
    Uso:
      renderItems(itemlist, parentitem)                                <- Carga el listado

Video:
  IsPlaying
    Descripcion:
      Devuelve True si se esta reproduciendo un video
    Uso:
      IsPlaying()                                   <- Devuelve True si se esta reproduciendo un video


  PlayVideo
    Descripcion:
     función encargada de reproducir un vídeo, despues de pasar por el conector, cuando ya tengamos la url reproducible del video.
     la url del video deve ponerse en item.video_url
    Uso:
      PlayVideo(item)                                   <- Reproduce el vídeo

'''

import os
import sys

import xbmc
import xbmcgui
import xbmcplugin
from core import config
from core import logger

'''
Funciones relacionadas con los dialogos
'''


# Progress dialog
def ProgressDialog(title, text, percent=0):
    class Dialog(object):
        def __init__(self, title, text, percent, PObject):
            self.PObject = PObject
            self.closed = False
            self.PObject.create(title, text)

        def iscanceled(self):
            return self.PObject.iscanceled() or self.closed

        def update(self, percent, text):
            self.PObject.update(percent, *[line for line in text.split("\n")[0:3]])

        def close(self):
            self.PObject.close()
            self.closed = True

    return Dialog(title, text, percent, xbmcgui.DialogProgress())


# Background Progress dialog
def ProgressDialogBG(title, text, percent=0):
    class Dialog(object):
        def __init__(self, title, text, percent, PObject):
            self.PObject = PObject
            self.title = title
            self.PObject.create(title, text)

        def iscanceled(self):
            return False

        def update(self, percent, text):
            self.PObject.update(percent, self.title, text)

        def close(self):
            self.PObject.close()

    return Dialog(title, text, percent, xbmcgui.DialogProgressBG())


# Dialog Alert
def AlertDialog(title, text):
    xbmcgui.Dialog().ok(title, text)


# Dialog Yes/No
def YesNoDialog(title, text):
    return xbmcgui.Dialog().yesno(title, text)


# Dialog select
def SelectDialog(title, options):
    return xbmcgui.Dialog().select(title, options)


# Dialog input
def InputDialog(title="", default="", password=False):
    keyboard = xbmc.Keyboard(default, title, password)
    keyboard.doModal()
    if (keyboard.isConfirmed()):
        return keyboard.getText()
    else:
        return None


'''
Funciones relacionadas con la generacion de los itemlist
'''


# Refresh
def ItemlistRefresh():
    xbmc.executebuiltin("Container.Refresh")


# Update
def ItemlistUpdate(item):
    xbmc.executebuiltin("Container.Update(" + sys.argv[0] + "?" + item.tourl() + ")")


# RenderItems
def renderItems(itemlist, parentitem):
    if parentitem.action == "findvideos":
        from platformcode import subtitletools
        subtitletools.saveSubtitleName(parentitem)
        
    import channelselector
    for item in itemlist:
        if item.thumbnail == "" and item.action == "search": item.thumbnail = channelselector.get_thumbnail_path() + "thumb_buscar.png"
        if item.thumbnail == "" and item.folder == True: item.thumbnail = channelselector.get_thumbnail_path() + "thumb_folder.png"
        if item.thumbnail == "" and item.folder == False: item.thumbnail = channelselector.get_thumbnail_path() + "thumb_nofolder.png"

        if item.fanart == "":
            channel_fanart = os.path.join(config.get_runtime_path(), 'resources', 'images', 'fanart',
                                          item.channel + '.jpg')
            if os.path.exists(channel_fanart):
                item.fanart = channel_fanart
            else:
                item.fanart = os.path.join(config.get_runtime_path(), "fanart.jpg")

        if item.category == "":
            item.category = parentitem.category

        if item.fulltitle == "":
            item.fulltitle = item.title

        if item.fanart == "":

            channel_fanart = os.path.join(config.get_runtime_path(), 'resources', 'images', 'fanart',
                                          item.channel + '.jpg')

            if os.path.exists(channel_fanart):
                item.fanart = channel_fanart
            else:
                item.fanart = os.path.join(config.get_runtime_path(), "fanart.jpg")

        if item.folder:
            AddNewItem(item, totalItems=len(itemlist))
        else:
            if config.get_setting("player_mode") == "1":  # SetResolvedUrl debe ser siempre "isPlayable = true"
                AddNewItem(item, IsPlayable="true", totalItems=len(itemlist))
            else:
                AddNewItem(item, IsPlayable="false", totalItems=len(itemlist))

    viewmode = parentitem.viewmode

    # Cierra el directorio
    xbmcplugin.setContent(int(sys.argv[1]), "Movies")
    xbmcplugin.setPluginCategory(handle=int(sys.argv[1]), category=parentitem.category)
    xbmcplugin.addSortMethod(handle=int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_NONE)

    if config.get_setting("forceview") == "true":
        if viewmode == "list":
            xbmc.executebuiltin("Container.SetViewMode(50)")
        elif viewmode == "movie_with_plot":
            xbmc.executebuiltin("Container.SetViewMode(503)")
        elif viewmode == "movie":
            xbmc.executebuiltin("Container.SetViewMode(500)")

    xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)


# AddnewItem
def AddNewItem(item, totalItems=0, IsPlayable="false"):
    item.title = unicode(item.title, "utf8", "ignore").encode("utf8")
    item.fulltitle = unicode(item.fulltitle, "utf8", "ignore").encode("utf8")
    item.plot = unicode(item.plot, "utf8", "ignore").encode("utf8")

    contextCommands = []
    if type(item.context) == list:
      for context in item.context:
        contextitem = item.clone(action=context["action"],channel=context["channel"])
        contextCommands.append(context["title"],"XBMC.RunPlugin(" + sys.argv[0] + "?" + contextitem.tourl() + ")")

    listitem = xbmcgui.ListItem(item.title, iconImage="DefaultVideo.png", thumbnailImage=item.thumbnail)
    listitem.setInfo("video",
                     {"Title": item.title, "FileName": item.title, "Plot": item.plot, "Duration": item.duration,
                      "Studio": item.channel.capitalize(), "Genre": item.category})
    listitem.addContextMenuItems ( contextCommands, replaceItems=False)
    set_infoLabels(listitem, item.plot)  # Modificacion introducida por super_berny para añadir infoLabels al ListItem

    if item.fanart != "":
        listitem.setProperty('fanart_image', item.fanart)
        xbmcplugin.setPluginFanart(int(sys.argv[1]), item.fanart)

    if IsPlayable == 'true':  # Esta opcion es para poder utilizar el xbmcplugin.setResolvedUrl()
        listitem.setProperty('IsPlayable', 'true')

    itemurl = '%s?%s' % (sys.argv[0], item.tourl())


    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=itemurl, listitem=listitem, isFolder=item.folder)


def set_infoLabels(listitem, plot):
    # Modificacion introducida por super_berny para añadir infoLabels al ListItem
    if plot.startswith("{'infoLabels'"):
        # Necesitaba un parametro que pase los datos desde Item hasta esta funcion 
        # y el que parecia mas idoneo era plot.
        # plot tiene que ser un str con el siguiente formato:
        #   plot="{'infoLabels':{dicionario con los pares de clave/valor descritos en 
        #               http://mirrors.xbmc.org/docs/python-docs/14.x-helix/xbmcgui.html#ListItem-setInfo}}"
        try:
            import ast
            infodict = ast.literal_eval(plot)['infoLabels']
            listitem.setInfo("video", infodict)
        except:
            pass


'''
Funciones relacionadas con la reproduccion del vídeo
'''


# IsPlaying
def IsPlaying():
    return xbmc.Player().isPlaying()


# PlayVideo:
def PlayVideo(item):
    if item.server == "torrent":
        xbmc.executebuiltin("XBMC.RunPlugin(" + item.video_url + ")")
        return

    xlistitem = xbmcgui.ListItem(item.title, iconImage="DefaultVideo.png", thumbnailImage=item.thumbnail, path=item.video_url)
    xlistitem.setInfo("video", {"Title": item.title, "Plot": item.plot, "Studio": item.channel, "Genre": item.category})

    # Descarga el subtitulo
    if item.subtitle:
        # noinspection PyBroadException,PyBroadException,PyBroadException
        try:
            import os
            ficherosubtitulo = os.path.join(config.get_data_path(), 'subtitulo.srt')
            from core import scrapertools
            data = scrapertools.cache_page(item.subtitle)
            fichero = open(ficherosubtitulo, "wb").write(data)
        except:
            logger.info("Error al descargar el subtítulo")

    logger.info("player_mode=" + config.get_setting("player_mode"))
    logger.info("mediaurl=" + item.video_url)
    
    if config.get_setting("player_mode") == "3":
        import download_and_play
        download_and_play.download_and_play(item.video_url, "download_and_play.tmp", config.get_setting("downloadpath"))
        return

    elif config.get_setting("player_mode") == "0" or ( config.get_setting("player_mode") == "3" and item.video_url.startswith("rtmp")):
        # Añadimos el listitem a una lista de reproducción (playlist)
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()
        playlist.add(item.video_url, xlistitem)

        # Reproduce
        playersettings = config.get_setting('player_type')
        logger.info("[xbmctools.py] playersettings=" + playersettings)

        player_type = xbmc.PLAYER_CORE_AUTO
        if playersettings == "0":
            player_type = xbmc.PLAYER_CORE_AUTO
            logger.info("[xbmctools.py] PLAYER_CORE_AUTO")
        elif playersettings == "1":
            player_type = xbmc.PLAYER_CORE_MPLAYER
            logger.info("[xbmctools.py] PLAYER_CORE_MPLAYER")
        elif playersettings == "2":
            player_type = xbmc.PLAYER_CORE_DVDPLAYER
            logger.info("[xbmctools.py] PLAYER_CORE_DVDPLAYER")

        xbmcPlayer = xbmc.Player(player_type)
        xbmcPlayer.play(playlist)

    elif config.get_setting("player_mode") == "1":
        # xlistitem.setProperty('IsPlayable', 'true')
        # xlistitem.setProperty('path', item.video_url)
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, xbmcgui.ListItem(path=mediaurl))

    elif config.get_setting("player_mode") == "2":

        xbmc.executebuiltin("PlayMedia(" + item.video_url + ")")

    xbmc.Player().setSubtitles(item.subtitle)