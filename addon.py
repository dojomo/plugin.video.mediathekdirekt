import xbmcaddon
import sys
import os
import xbmcplugin
import xbmcgui
import urllib
import json

addonID = 'plugin.video.mediathekdirekt'
addon = xbmcaddon.Addon(id=addonID)
pluginhandle = int(sys.argv[1])
translation = addon.getLocalizedString
addonDir = xbmc.translatePath(addon.getAddonInfo('path'))
defaultFanart = os.path.join(addonDir,'resources/ard_fanart.jpg')
icon = os.path.join(addonDir,'icon.png')
addon_work_folder = xbmc.translatePath("special://profile/addon_data/" + addonID)
jsonFile = xbmc.translatePath("special://profile/addon_data/" + addonID + "/good.json")

if not os.path.isdir(addon_work_folder):
    os.mkdir(addon_work_folder)

def index():
	data = getData()
	xbmcgui.Dialog().ok(addonID, 'data len', str(len(data)))
	channels = []
	for entry in data:
		if entry[0] not in channels:
			channels.append(entry[0])
	addDir("", "", 'updateData', "", 0)
	for entry in channels:
		fanart_image = getFanart(entry)
		addDir(str(entry), "", 'index', fanart_image, 0)
	xbmcplugin.endOfDirectory(pluginhandle)

def updateData():
    target = urllib.URLopener()
    target.retrieve("http://www.mediathekdirekt.de/good.json", jsonFile)

def getData():
	with open(jsonFile, 'r') as f:
		data = json.load(f)
		return data

def getFanart(channel):
    channel = channel.replace(' ', "").lower()
    fanart = os.path.join(addonDir,'resources/fanart_'+channel+'.jpg');
    if not os.path.isfile(fanart):
        fanart = os.path.join(addonDir,'resources/fanart_zdf.jpg');
    #xbmcgui.Dialog().ok(addonID, 'fanart', str(fanart))
    xbmc.executebuiltin('Notification(Hello World,'+fanart+',10000,/script.hellow.world.png)')
    return fanart

def addDir(name, url, mode, iconimage, total=0):
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    if iconimage:
        liz.setProperty("fanart_image", iconimage)
    else:
        liz.setProperty("fanart_image", defaultFanart)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, totalItems=total, isFolder=True)
    return ok

def addVideo(name, url):
    li = xbmcgui.ListItem(name, iconImage=icon)
    ok = xbmcplugin.addDirectoryItem(handle=pluginhandle, url=url, listitem=li)
    return ok

def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
name = urllib.unquote_plus(params.get('name', ''))

if mode == 'updateData':
    updateData()
else:
    index()