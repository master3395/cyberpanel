# -*- coding: utf-8 -*-
from django.shortcuts import render
from plogical.mailUtilities import mailUtilities
import os
from xml.etree import ElementTree
from plogical.httpProc import httpProc

def installed(request):
    mailUtilities.checkHome()
    pluginPath = '/home/cyberpanel/plugins'
    pluginList = []

    if os.path.exists(pluginPath):
        for plugin in sorted(os.listdir(pluginPath)):
            pluginDir = os.path.join(pluginPath, plugin)
            if not os.path.isdir(pluginDir) or plugin.startswith('_'):
                continue
            completePath = os.path.join('/usr/local/CyberCP', plugin, 'meta.xml')
            if not os.path.isfile(completePath):
                continue
            try:
                pluginMetaData = ElementTree.parse(completePath)
            except ElementTree.ParseError:
                continue

            data = {}
            data['name'] = pluginMetaData.find('name').text
            data['type'] = pluginMetaData.find('type').text
            data['desc'] = pluginMetaData.find('description').text
            data['version'] = pluginMetaData.find('version').text

            pluginList.append(data)

    proc = httpProc(request, 'pluginHolder/plugins.html',
                    {'plugins': pluginList}, 'admin')
    return proc.render()
