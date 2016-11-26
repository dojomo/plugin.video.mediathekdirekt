import xbmcaddon
import sys
import os
import xbmcplugin
import xbmcgui
import urllib
import json
import re

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
	length = len(channels) + 1;
	addDir("", "", 'updateData', "", length)
	channels.sort()
	for entry in channels:
		addDir(entry, entry, 'showChannel', getFanart(entry), length)
	xbmcplugin.endOfDirectory(pluginhandle)

def showChannel(channel = ""):
    if channel != "":
    	fanart = getFanart(channel)
    	addDir("Suche", channel, 'showChannel', fanart, 3)
    	addDir("Nach Datum", channel, 'sortByYears', fanart, 3)
    	addDir("Nach Thema", channel, 'sortTopicsInitials', fanart, 3)
    xbmcplugin.endOfDirectory(pluginhandle)

def sortByYears(channel = ""):
    data = getData()
    result = []
    for entry in data:
        date = entry[3].split('.')
        if len(date) > 2:
            if date[2] not in result:
                if channel != "":
                    if entry[0] == channel:
               		    result.append(date[2])
                else:
                    result.append(date[2])
    result.sort(reverse=True)
    for entry in result:
    	addDir(entry, channel+'|'+entry, 'sortByMonths', getFanart(channel), len(result))
    xbmcplugin.endOfDirectory(pluginhandle)

def sortByMonths(channelYear = ""):
    data = getData()
    params = channelYear.split("|")
    channel = ""
    year = ""
    result = []
    if len(params) > 1:
        channel = params[0]
        year = params[1]
    for entry in data:
        if entry[0] == channel:
            date = entry[3].split('.')
            if len(date) > 2:
                if date[2] == year:
                    if date[1]+'.'+date[2] not in result:
                        result.append(date[1]+'.'+date[2])
    result.sort()
    for entry in result:
    	addDir(entry, channel+'|'+entry, 'sortByDays', getFanart(channel), len(result))
    xbmcplugin.endOfDirectory(pluginhandle)

def sortByDays(channelMMYY = ""):
    data = getData()
    params = channelMMYY.split("|")
    channel = ""
    mmYY = ""
    result = []
    if len(params) > 1:
    	channel = params[0]
    	mmYY = params[1]
    for entry in data:
    	if entry[0] == channel:
    		date = entry[3].split('.',1)
    		if len(date) > 1:
    			if date[1] == mmYY:
    				if date[0]+'.'+date[1] not in result:
    					result.append(date[0]+'.'+date[1])
    result.sort()
    for entry in result:
    	params = str(channel+'|'+entry)
    	addDir(entry, params, 'showDay', getFanart(channel), len(result))
    xbmcplugin.endOfDirectory(pluginhandle)

def showDay(channelDate):
    data = getData()
    params = channelDate.split("|")
    channel = ""
    date = ""
    result = []
    if len(params) > 1:
        channel = params[0]
        date = params[1]
    for entry in data:
        if entry[0] == channel:
            if entry[3] == date:
                result.append(entry)
    result.sort(key=lambda entry: entry[1])
    for entry in result:
        addVideo(entry)
    xbmcplugin.endOfDirectory(pluginhandle)

def sortTopicsInitials(channel = ""):
    data = getData()
    result = []
    fanart = getFanart(channel)
    if channel != "":
    	for entry in data:
    		if entry[0] == channel:
    			if len(entry[2]) > 0:
    				l = entry[2][0].upper()
    				if not re.match('^([a-z|A-Z])',l):
    					l = '#'
    				if l not in result:
    					result.append(l)
    result.sort()
    for entry in result:
    	addDir(entry, channel+'|'+entry, 'sortTopics', fanart, len(result))
    xbmcplugin.endOfDirectory(pluginhandle)

def sortTopics(channelInitial="|"):
    data = getData()
    result = []
    params = channelInitial.split("|")
    channel = ""
    initial = ""
    if len(params) > 1:
        channel = params[0]
        initial = params[1]	
    fanart = getFanart(channel)
    if channel != "":
    	for entry in data:
    		if entry[0] == channel:
    			i = entry[2][0].upper()
    			if initial == '#':
    			    if not re.match('^([a-z|A-Z])', i):
    			        if entry[2] not in result:
    			        	result.append(entry[2])
    			else:
    				if initial == i:
    					if entry[2] not in result:
    						result.append(entry[2])
    result.sort()
    xbmcgui.Dialog().ok(addonID, str(result))
    for entry in result:
    	addDir(entry.encode('utf8'), channel.encode('utf8')+'|'+entry.encode('utf8'), 'sortTopic', fanart, len(result))
    xbmcplugin.endOfDirectory(pluginhandle)


def updateData():
    target = urllib.URLopener()
    target.retrieve("http://www.mediathekdirekt.de/good.json", jsonFile)

def getData():
	with open(jsonFile, 'r') as f:
		data = json.load(f, encoding='utf-8')
		return data

def getFanart(channel):
    channel = channel.replace(' ', "").lower()
    channel = channel.split('.')
    channel = channel[0]
    channel = channel.split('-')
    channel = channel[0];
    fanart = os.path.join(addonDir,'resources/images/fanart_'+channel+'.jpg');
    if not os.path.isfile(fanart):
        fanart = os.path.join(addonDir,'resources/images/fanart__zdf.jpg');
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

def addVideo(entry):
    ok = True
    if len(entry) > 6:
        channel = entry[0]
        title = entry[1]
        topic = entry[2]
        date = entry[3]
        year = date.split('.')
        premiered = str(date[-1]+'-'+date[-2]+'-'+date[-3])
        year = date[-1]
        #duration in HH:MM:SS
        duration = entry[4]
        description = entry[5]
        url = entry[6]
        li = xbmcgui.ListItem(title)
        li.setInfo(type="Video", infoLabels={"Title": title, "Duration": duration, "Genre": topic, "Year": year, "Plotoutline": description, "Studio": channel, "premiered": premiered, "aired": premiered, "dateadded": premiered+' '+duration})
        li.setArt({'thumb': getFanart(channel)})
        li.setProperty('IsPlayable', 'true')
        ok = xbmcplugin.addDirectoryItem(handle=pluginhandle, url=url, listitem=li)
    return ok

def serialize(input):
	result = urllib.quote_plus(input)
	return result

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
elif mode == 'sortByYears':
	sortByYears(url)
elif mode == 'sortByMonths':
	sortByMonths(url)
elif mode == 'sortByDays':
	sortByDays(url)
elif mode == 'showDay':
	showDay(url)
elif mode == 'showChannel':
	showChannel(url)
elif mode == 'sortTopicsInitials':
	sortTopicsInitials(url)
elif mode == 'sortTopics':
	sortTopics(url)
else:
    index()