
    __author__ = 'Mayukh Sarkar'
__email__ = 'mayukh.sarkar@morpho.com'
import os
import subprocess
from abc import ABCMeta, abstractmethod


################# Unit testing ######################
#### This should be uncommented for unit testing ####
products = [
    {"Product": "S65-85OS04_M2M_GP211_JC222_R6",
     "PlatformName": "winPc",
     "PlatformVariant": "eeprom",
     "DocGeneration": False,
     "BuildStatus": "Pass",
     },
]
#####################################################

class JCSIM(object):
    __metaclass__ = ABCMeta

    counter = 0

    def __init__(self, ws):
        os.system("taskkill /f /im JCSim3x.exe")
        self.jcsim = os.path.join(ws, r'tools', r'Jacade', r'SimulationEnvironment', r'JCSim3x.exe')

    @abstractmethod
    def _initiate_jcsim(self, proto=None):
        pass

    @abstractmethod
    def build(self):
        pass


class UTE(JCSIM):
    def __init__(self, workspace=None, products=None):
        JCSIM.__init__(self, workspace)
        if workspace is not None:
            self.workspace = workspace
        if products is not None:
            self.protos = [each['Product'] for each in products]
        self._LIBJARS = ""

    def _make_scenario(self, proto):
        header = os.path.join(self.workspace, 'source', 'SIMbiOS_2_9', proto, 'tst', 'config') + ';'
        header += os.path.join(r"..", 'test') + ';'
        header += os.path.join(r"..", 'config_fs') + ';'
        header += os.path.join(r"..", 'applet') + ';'
        header += os.path.join(r"..", 'src') + ';'
        return header

    def _verbose(self, proto):
        PRJ_DIR = self.workspace
        CRD_DIR = os.path.join(PRJ_DIR, 'source', 'SIMbiOS_2_9', proto)
        CRD_TST = os.path.join(CRD_DIR, 'tst')
        SCDL_DIR = os.path.join(CRD_DIR, 'dev', 'sw')
        TST_DIR = os.path.join(PRJ_DIR, 'tst')
        UTEBAT_DIR = os.path.join(TST_DIR, 'batch')
        MY_SCDL = os.path.join(SCDL_DIR, proto + r'.scdl')
        MY_UTEBAT = os.path.join(UTEBAT_DIR, r'toolkit', r'Toolkit_CompleteBatch.utebat')
        MY_LOGS = os.path.join(CRD_TST, 'proto_winpc')

        print r'*******************************************************************************'
        print '* script: %s ... starting up ...' % os.path.basename(__file__)
        print r'*******************************************************************************'

        print 'PRJ_DIR    =', PRJ_DIR
        print 'CRD_DIR    =', CRD_DIR
        print 'CRD_TST    =', CRD_TST
        print 'SCDL_DIR   =', SCDL_DIR
        print '.'
        print 'TST_DIR    =', TST_DIR
        print 'UTEBAT_DIR =', UTEBAT_DIR
        print '.'
        print 'UTEBAT     =', MY_UTEBAT
        print 'MY_SCDL    =', MY_SCDL
        print 'MY_LOGS    =', MY_LOGS
        print '.'
        print 'JAVA_HOME  ='
        print 'CD         =', PRJ_DIR
        # global _LIBJARS
        self._LIBJARS = self._make_scenario(proto)
        self._LIBJARS += ';'
        return MY_SCDL, MY_LOGS, MY_UTEBAT

    def _initiate_jcsim(self, proto=None):
        if proto is None:
            raise ValueError('Proto can not be None')
        DLL_DIR = os.path.join(self.workspace, 'target', proto + r'_' + r'winPc', r'release', r'bin')
        VJC = os.path.join(DLL_DIR, proto + r".vjc")
        if UTE.counter > 0:
            os.system("taskkill /f /im JCSim3x.exe")
            UTE.counter -= 1
        JCSim3x = subprocess.Popen("start " + self.jcsim + ' -minimized ' + " -vjc " + VJC, shell=True)
        UTE.counter += 1

    def build(self):
        for proto in self.protos:
            scdl, log, utebat = self._verbose(proto)
            self.populate_libs(os.path.join(self.workspace, "tools"))
            self.start_build(proto, scdl, utebat, log)

    def start_build(self, proto, scdl, utebat, log):
        self._initiate_jcsim(proto)
        print '.'
        print '+=====================================================================+'
        print '|  CHECK PRECONDITIONS:                                               |'
        print '|    (1)  Have you started JCSim3x.exe?                               |'
        print '|    (2)  Is the IO-Mode adjusted in JCSim3x and UTE?                 |'
        print '|          - e.g.: DirectIO with TLP-port:9027                        |'
        print '|    (3)  Have you inserted a Simulation.DLL (=loaded a *.vjc file)?  |'
        print '+=====================================================================+'
        print '.'
        print 'java.exe path =', os.path.join(self.workspace, 'tools', 'jdk', 'bin')
        print 'logging.properties path =', os.path.join(self.workspace, 'source', 'SIMbiOS_2_9', proto, 'tst', 'config')
        print '.'

        print '*******************************************************************************'
        print '* NEXT STEP: ... UTE-CONSOLE ... will be called next'
        print '*            (com.orga.ute.gui.console.Console)'
        print '*'
        print '* log-files path: %s' % os.path.join(self.workspace, 'source', 'SIMbiOS_2_9', proto, 'tst',
                                                    'proto_winpc')
        print '*******************************************************************************'
        print '.'
        ############ hard coding UTEBAT file ################
        java = os.path.join(self.workspace, 'tools', 'jdk', 'bin', 'java.exe')
        javaOp1 = r" -d32 -Xmx384M -Xms128M -Djava.library.path="
        cardinterfacePath = os.path.join(self.workspace, 'tools', 'cardinterface')
        javaOp2 = r" -Djava.util.logging.config.file="
        loggingPath = os.path.join(self.workspace, 'source', 'SIMbiOS_2_9', proto, 'tst', 'config',
                                   'logging.properties')
        uteConsole = r" com.orga.ute.gui.console.Console -b " + utebat + r" -PIODLL=com.orga.ute.artifact.card.reader.tlp.TlpDirectControlIO -PLOG_DIR=" + log
        peeS = r" -Pee_software=" + scdl
        global _LIBJARS
        dc = dict(os.environ)
        dc['classPath'] = self._LIBJARS
        # print _LIBJARS
        subprocess.Popen(java + javaOp1 + cardinterfacePath + javaOp2 + loggingPath + uteConsole + peeS, shell=True,
                         env=dc, cwd=os.path.join(self.workspace, 'tst', 'lib'))

    def populate_libs(self, tools):
        ############## for header paths ##############
        t = os.path.join(r"..", r"lib", r"ute", r"*") + ';'
        self._LIBJARS += t
        t = os.path.join(r"..", r"lib", r"*") + ';'
        self._LIBJARS += t
        t = os.path.join(r"..", r"..", r"source", r"uiccFramework", r"tst", r"lib") + r"\\"
        t = os.path.join(t, r"*") + ';'
        self._LIBJARS += t
        ############## for core jars #################
        libJars = []
        for each in os.listdir(tools):
            for e in os.listdir(os.path.join(tools, each)):
                if e.endswith('jar'):
                    libJars.append(os.path.join(r"..", r"..", "tools", each, e))

        core = ';'.join(libJars)
        core += ';'
        ############## for api jars #################
        libJars = []
        for each in os.listdir(os.path.join(tools, 'api')):
            for e in os.listdir(os.path.join(tools, 'api', each)):
                if e.endswith('jar'):
                    libJars.append(os.path.join(r"..", r"..", "tools", "api", each, e))
        api = ';'.join(libJars)
        api += ';'
        ############# for xml-jdom jars ############
        libJars = []
        for each in os.listdir(os.path.join(tools, r'xml', r'jdom', r'1.1.1')):
            if os.path.isdir(os.path.join(tools, r'xml', r'jdom', r'1.1.1', each)):
                for e in os.listdir(os.path.join(tools, r"xml", r"jdom", r"1.1.1", each)):
                    if e.endswith('jar'):
                        libJars.append(os.path.join(r"..", r"..", "tools", "xml", "jdom", r"1.1.1", each, e))

        for each in os.listdir(os.path.join(tools, r'xml', r'jdom', r'2.0.2')):
            if os.path.isdir(os.path.join(tools, r'xml', r'jdom', r'2.0.2', each)):
                for e in os.listdir(os.path.join(tools, r"xml", r"jdom", r"2.0.2", each)):
                    if e.endswith('jar'):
                        libJars.append(os.path.join(r"..", r"..", "tools", "xml", "jdom", r"2.0.2", each, e))

        jdom = ";".join(libJars)
        jdom += ";"
        ########### for ImageConverter ############

        img = os.path.join(r"..", r"..", r'tools', r'ImageConvert', r'*')

        self._LIBJARS += core + api + jdom + img + ';'


if __name__ == '__main__':
    ute = UTE(r"D:\p4v\ssimbiOS_2_9", products)
    ute.build()
