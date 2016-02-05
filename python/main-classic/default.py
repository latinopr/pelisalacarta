# -*- coding: iso-8859-1 -*-
#------------------------------------------------------------
# pelisalacarta
# XBMC entry point
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

# Constants
__plugin__  = "pelisalacarta"
__author__  = "pelisalacarta"
__url__     = "http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/"
__date__ = "26/03/2015"
__version__ = "4.0"

import os
import sys
from core import config
from core import logger
from core.item import Item

logger.info("pelisalacarta.default init...")

librerias = xbmc.translatePath( os.path.join( config.get_runtime_path(), 'lib' ) )
sys.path.append (librerias)

# Extract parameters from sys.argv
def extract_parameters():
  logger.info("pelisalacarta.platformcode.launcher extract_parameters")
  if sys.argv[2].replace("?",""):
    item = Item().fromurl(sys.argv[2].replace("?",""))
  else:
    item=Item(channel="channelselector", action="mainlist")
  return item
  
from platformcode import launcher

if sys.argv[2] == "":
  import xbmcplugin
  import xbmc
  launcher.start()
  xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=False)
  xbmc.executebuiltin("Container.Update("+sys.argv[ 0 ] + "?)")
else:
  item = extract_parameters()
  if "strmfile" in item and item.strmfile == True:
    item.strmfile= False      
    import xbmc, xbmcgui, xbmcplugin
    listitem = xbmcgui.ListItem( None, path=os.path.join(config.get_runtime_path(),"icon.png"))
    xbmcplugin.setResolvedUrl(int(sys.argv[1]),True,listitem)
    xbmc.Player().stop()
    xbmc.executebuiltin("Container.Update("+sys.argv[ 0 ]+ "?" + item.tourl()+")")
  else:
    launcher.run(item)
