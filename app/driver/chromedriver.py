import os
import zipfile
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

def get(session):
    #Get the current path to save files here
    dir = str(Path( __file__ ).parent.absolute())

    chrome_options = Options()

    #Capabilities, sirve para poder ver el consumo
    chrome_options.set_capability('loggingPrefs', {'performance' : 'INFO'})
    chrome_options.set_capability('goog:loggingPrefs', { 'performance':'ALL' })

    #Session
    chrome_options.add_argument(f'--user-data-dir={dir}/sessions/{session.phone}')
    print(f'--user-data-dir={dir}/sessions/{session.phone}')

    # Ignores any certificate errors if there is any
    chrome_options.add_argument("--ignore-certificate-errors")
    # Necesario para correrlo como root dentro del container
    chrome_options.add_argument("--no-sandbox")

    if session.proxy != "":
        #host : port : username : password
        proxy_vars = session.proxy.split(':')
        background = background_js % tuple(proxy_vars)

        pluginfile = dir+'/proxy_auth_plugin.zip'

        with zipfile.ZipFile(pluginfile, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background)
        chrome_options.add_extension(pluginfile)
    else:
        print("no proxy config")

    driver = webdriver.Chrome(options=chrome_options)
    return driver

manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"22.0.0"
}
"""

background_js = """
var config = {
        mode: "fixed_servers",
        rules: {
        singleProxy: {
            scheme: "http",
            host: "%s",
            port: parseInt(%s)
        },
        bypassList: ["localhost"]
        }
    };

chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

function callbackFn(details) {
    return {
        authCredentials: {
            username: "%s",
            password: "%s"
        }
    };
}

chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
);
"""
