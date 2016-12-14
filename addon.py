import xbmcaddon
import sys
import os
import xbmcplugin
import xbmcgui
import urllib
import json
import re
import time
from datetime import date, timedelta

addonID = 'plugin.video.mediathekdirekt'
addon = xbmcaddon.Addon(id=addonID)
pluginhandle = int(sys.argv[1])
translation = addon.getLocalizedString
addonDir = xbmc.translatePath(addon.getAddonInfo('path'))
defaultFanart = os.path.join(addonDir,'resources/ard_fanart.jpg')
icon = os.path.join(addonDir,'icon.png')
addon_work_folder = xbmc.translatePath("special://profile/addon_data/" + addonID)
jsonFile = xbmc.translatePath("special://profile/addon_data/" + addonID + "/good.json")
maxFileAge = int(addon.getSetting("maxFileAge"))
maxFileAge = maxFileAge*60
showTopicsDirectly = str(addon.getSetting("showTopicsDirectly")).lower()

if not os.path.isdir(addon_work_folder):
    os.mkdir(addon_work_folder)

def index():
    data = getData()
    channels = []
    for entry in data:
        if entry[0] not in channels:
            channels.append(entry[0])
    length = len(channels) + 3;
    addDir(translation(30001), '', 'search', '', length)
    if showTopicsDirectly == "true":
        addDir(translation(30010), '|', 'sortTopics', '', length)
    else:
        addDir(translation(30010), '', 'sortTopicsInitials', '', length)
    channels.sort()
    for entry in channels:
        addDir(entry, entry, 'showChannel', getFanart(entry), length)
    addDir(translation(30006), "", 'updateData', "", length)
    xbmcplugin.endOfDirectory(pluginhandle)

def showChannel(channel = ""):
    today = date.today()
    yesterday = today - timedelta(days=1)
    today = today.strftime("%d.%m.%Y")
    yesterday = yesterday.strftime("%d.%m.%Y")
    if channel != "":
        fanart = getFanart(channel)
        addDir(translation(30002), channel, 'search', fanart, 6)
        addDir(translation(30008), channel+'|'+today, 'searchDate', fanart, 6)
        addDir(translation(30009), channel+'|'+yesterday, 'searchDate', fanart, 6)
        addDir(translation(30003), channel, 'sortByYears', fanart, 6)
        if showTopicsDirectly == "true":
            addDir(translation(30004), channel+'|', 'sortTopics', fanart, 6)
        else:
            addDir(translation(30004), channel, 'sortTopicsInitials', fanart, 6)
        addDir(translation(30005), channel, 'sortTitleInitials', fanart, 6)
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
    length = len(result) + 1
    addDir(translation(30007), channel, 'searchDate', getFanart(channel), length)
    for entry in result:
        addDir(entry, channel+'|'+entry, 'sortByMonths', getFanart(channel), length)
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
    xbmcplugin.setContent(pluginhandle, 'movies');
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

def sortTitleInitials(channel = ""):
    data = getData()
    result = []
    fanart = getFanart(channel)
    if channel != "":
        for entry in data:
            if entry[0] == channel:
                if len(entry[1]) > 0:
                    l = entry[1][0].upper()
                    if not re.match('^([a-z|A-Z])',l):
                        l = '#'
                    if l not in result:
                        result.append(l)
    result.sort()
    for entry in result:
        addDir(entry, channel+'|'+entry, 'sortTitles', fanart, len(result))
    xbmcplugin.endOfDirectory(pluginhandle)


def sortTopicsInitials(channel = ""):
    data = getData()
    result = []
    fanart = getFanart(channel)
    for entry in data:
        if channel != "":
            if entry[0] == channel:
                if len(entry[2]) > 0:
                    l = entry[2][0].upper()
                    if not re.match('^([a-z|A-Z])',l):
                        l = '#'
                    if l not in result:
                        result.append(l)
        else:
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

def sortTitles(channelInitial="|"):
    xbmcplugin.setContent(pluginhandle, 'movies');
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
                i = entry[1][0].upper()
                if initial == '#':
                    if not re.match('^([a-z|A-Z])', i):
                            result.append(entry)
                else:
                    if initial == i:
                        result.append(entry)
    result.sort(key=lambda entry: entry[1].lower())
    for entry in result:
        addVideo(entry)
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
    for entry in data:
        if channel != "":
            if entry[0] == channel:
                i = entry[2][0].upper()
                if initial == '#':
                    if not re.match('^([a-z|A-Z])', i):
                        if entry[2] not in result:
                            result.append(entry[2])
                elif (initial == "") and (showTopicsDirectly == "true"):
                    if entry[2] not in result:
                        result.append(entry[2])
                else:
                    if initial == i:
                        if entry[2] not in result:
                            result.append(entry[2])
        else:
            i = entry[2][0].upper()
            if initial == '#':
                if not re.match('^([a-z|A-Z])', i):
                    if entry[2] not in result:
                        result.append(entry[2])
            elif (initial == "") and (showTopicsDirectly == "true"):
                if entry[2] not in result:
                    result.append(entry[2])
            else:
                if initial == i:
                    if entry[2] not in result:
                        result.append(entry[2])
    result.sort(key=lambda entry: entry.lower())
    for entry in result:
        addDir(entry.encode('utf8'), channel.encode('utf8')+'|'+entry.encode('utf8'), 'sortTopic', fanart, len(result))
    xbmcplugin.endOfDirectory(pluginhandle)

def sortTopic(channelTopic = "|"):
    xbmcplugin.setContent(pluginhandle, 'movies');
    data = getData()
    result = []
    params = channelTopic.split("|",1)
    channel = ""
    topic = ""
    if len(params) > 1:
        channel = params[0]
        topic = params[1]
    fanart = getFanart(channel)
    for entry in data:
        if channel != "":
            if entry[0] == channel:
                if entry[2].encode('utf8') == topic:
                    result.append(entry)
        else:
            if entry[2].encode('utf8') == topic:
                result.append(entry)
    result.sort(key=lambda entry: entry[1].lower())
    for entry in result:
        addVideo(entry)
    xbmcplugin.endOfDirectory(pluginhandle)

def search(channel=""):
    xbmcplugin.setContent(pluginhandle, 'movies');
    result = []
    keyboard = xbmc.Keyboard('', translation(30002))
    keyboard.doModal()
    if keyboard.isConfirmed() and keyboard.getText():
        search_string = keyboard.getText().encode('utf8').lower()
        if len(search_string) > 0:
            data = getData()
            for entry in data:
                cEntry = entry
                if search_string in cEntry[1].encode('utf8').lower():
                    if channel != "":
                        if cEntry[0] == channel:
                            cEntry[1] = cEntry[2]+': '+cEntry[1]
                            result.append(cEntry)
                    else:
                        cEntry[1] = cEntry[2]+': '+cEntry[1]
                        result.append(cEntry)
                elif search_string in cEntry[2].encode('utf8').lower():
                    if channel != "":
                        if cEntry[0] == channel:
                            cEntry[1] = cEntry[2]+': '+cEntry[1]
                            result.append(cEntry)
                    else:
                        cEntry[1] = cEntry[2]+': '+cEntry[1]
                        result.append(cEntry)
            result.sort(key=lambda entry: entry[1].lower())
            for entry in result:
                addVideo(entry)
        xbmcplugin.endOfDirectory(pluginhandle)

def searchDate(channelDate = ""):
    xbmcplugin.setContent(pluginhandle, 'movies');
    channel = ""
    date = ""
    params = channelDate.split('|')
    channel = params[0]
    if len(params) > 1:
        date = params[1]
    result = []
    if date == "":
        dialog = xbmcgui.Dialog()
        date = dialog.numeric(1, translation(30007))
        date = re.sub('[^0-9|^\/]','0',date)
        date = date.replace('/','.')
    if (channel != "") and (len(date) == 10):
        data = getData()
        for entry in data:
            cEntry = entry
            if (entry[0] == channel) and (entry[3] == date):
                cEntry[1] = cEntry[2]+': '+cEntry[1]
                result.append(cEntry)
            result.sort(key=lambda entry: entry[1].lower())
        for entry in result:
            addVideo(entry)
    xbmcplugin.endOfDirectory(pluginhandle)

def updateData():
    target = urllib.URLopener()
    target.retrieve("http://www.mediathekdirekt.de/good.json", jsonFile)

def getData():
    if not os.path.isfile(jsonFile):
        updateData()
    else:
        fileTime = os.path.getmtime(jsonFile)
        now = time.time()
        if now-fileTime > maxFileAge:
            updateData()

    with open(jsonFile, 'r') as f:
        data = json.load(f)
        return data

def getFanart(channel):
    channel = channel.replace(' ', "").lower()
    channel = channel.split('.')
    channel = channel[0]
    channel = channel.split('-')
    channel = channel[0];
    fanart = os.path.join(addonDir,'resources/images/fanart_'+channel+'.jpg');
    if not os.path.isfile(fanart):
        fanart = icon
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
    if len(entry) > 7:
        channel = entry[0]
        title = entry[1]
        topic = entry[2]
        date = entry[3]
        year = date.split('.')
        premiered = str(date[2]+'-'+date[1]+'-'+date[0])
        year = date[-4:]
        duration = entry[4]
        description = entry[5]+"..."
        url = entry[6]
        link = entry[7]
        fanart = getFanart(channel)
        li = xbmcgui.ListItem(title)
        li.setInfo(type="Video", infoLabels={"Title": title, "Duration": duration, "Genre": topic, "Year": year, "PlotOutline": description, "Plot": description, "Studio": channel, "premiered": premiered, "aired": premiered, "dateadded": premiered+' '+duration})
        li.setArt({'thumb': fanart})
        li.setProperty("fanart_image", fanart)
        li.setProperty('IsPlayable', 'true')
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
elif mode == 'sortTopic':
    sortTopic(url)
elif mode == 'search':
    search(url)
elif mode == 'sortTitleInitials':
    sortTitleInitials(url)
elif mode == 'sortTitles':
    sortTitles(url)
elif mode == 'searchDate':
    searchDate(url)
else:
    index()