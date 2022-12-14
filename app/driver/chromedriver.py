import zipfile
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get(session):
    print(session.path())

    options = Options()

    #Capabilities, sirve para poder ver el consumo
    options.set_capability('loggingPrefs', {'performance' : 'INFO'})
    options.set_capability('goog:loggingPrefs', { 'performance':'ALL' })

    options.add_argument(f"--user-data-dir={session.path()}") #Session
    options.add_argument("--ignore-certificate-errors") #Ignores any certificate errors if there is any
    options.add_argument("--no-sandbox") # Necesario para correrlo como root dentro del container

    if session.proxy != "":
        #host : port : username : password
        proxy_vars = session.proxy.split(':')
        background = background_js % tuple(proxy_vars)

        pluginfile = session.path()+'/proxy_auth_plugin.zip'

        with zipfile.ZipFile(pluginfile, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background)
        options.add_extension(pluginfile)
    else:
        print("no proxy config")

    driver = webdriver.Chrome(options=options)
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
