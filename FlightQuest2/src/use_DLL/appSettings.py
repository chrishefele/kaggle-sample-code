import xml.etree.ElementTree as ET

CONFIG_FILE = 'RunSimulation.exe.config'

def makeAppSettingFunction(config_file):
    # Returns a function that returns specific application setting
    # First, create a dict of settings by parsing the .config XML file
    app_settings = {}
    xml_tree = ET.parse(config_file).getroot().findall('appSettings')[0]
    for node in xml_tree:  
        # print node.tag, node.attrib 
        k, v = node.attrib['key'], node.attrib['value']
        app_settings[k] = v
    # create and return a closure
    def appSettingFunction(s):
        return app_settings[s]
    return appSettingFunction  

if __name__ == '__main__':
    print "testing appSettings()"
    print "\t","parsing:", CONFIG_FILE
    appSetting = makeAppSettingFunction(CONFIG_FILE)
    settings = [ "dates", "basePath", "configFile", "projectionFile", 
        "airportsFile", "landingFile", "taxiFile",  "weatherFiles", 
        "flightFiles",  "groundConditionFiles", 
        "actualTakeoffFiles", "actualLandingFiles" ]
    for setting in settings:
        print '\t', setting, '-->', appSetting(setting)
    
