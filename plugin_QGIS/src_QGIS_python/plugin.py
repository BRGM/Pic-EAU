# coding=utf-8

import os.path
import os
from qgis.gui import QgsMessageBar
from qgis.core import QgsRasterLayer
from PyQt5.QtCore import QObject, Qt, QUrl
from PyQt5.QtWidgets import QAction, QWidget, QLineEdit, QPushButton, QVBoxLayout, QListWidgetItem
from PyQt5.QtGui import QIcon
from PyQt5.uic import  loadUi
from PyQt5 import  uic

from .hubeau import getWLMeasurementPoints
from .hubeau import getWQMeasurementPoints
from .hubeau import getWLDataFromPoint
from .gitlab import getIssues
from .plotwl import plotWaterLevel
from .piceau import getQuantile
from .plot_boxplot_pz import BoxPlotStat_Descr
#from .piceau_main_window import PicoDialog

def img_path(img):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)),'img',img)

def cache_path(myfile):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)),'cache',myfile)

def ui_path(ui):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)),'ui',ui)

class Plugin(QObject):
    def initGui(self):
        pass

    def __init__(self, iface):
        QObject.__init__(self)
        self.__iface=iface

        self.__iface.messageBar().pushInfo("Grettings",u"A new way to see water level in France, and issues associated too !")
        self.__action = QAction(QIcon(img_path('logo_gir.svg')), "Use Pic'eau", self.__iface.mainWindow())
        self.__action.triggered.connect(self.__addlayers)
        self.__iface.addToolBarIcon(self.__action)
        self.__graph=QAction(QIcon(img_path('plotts.svg')),'GraphTS!', self.__iface.mainWindow())
        self.__graph.triggered.connect(self.__plotwl)
        self.__iface.addToolBarIcon(self.__graph)

        if self.__iface.activeLayer() is not None:
            self.__curlayer=self.__iface.activeLayer().selectedFeatures()
        else:
            self.__curlayer = False

        # marche: deux lignes dessous
        self.__dock = uic.loadUi(ui_path('pic_eau.ui'))
        self.__iface.addDockWidget(Qt.RightDockWidgetArea, self.__dock)
        # set connection/action
        self.__dock.pushButton_trace.clicked.connect(self.__plotwl_webview)
        #li_bss=self.__dock.listView
        #id_bss=QListWidgetItem('ici',li_bss)
        #self.__dock.listView.addItem(id_bss)
        #self.__dock.listWidgetBSS.insertItem(0, '05857X0144/F')
        self.__dock.listWidgetBSS.insertItem(0, '08025X0009/P')
        self.__dock.listWidgetBSS.insertItem(1, '08037X0398/F1')
        self.__dock.listWidgetBSS.insertItem(2, '08037X0169/F')
        self.__dock.listWidgetBSS.insertItem(3, '08033X0237/F3')

        self.__curBSS_ID=self.__dock.listWidgetBSS.selectedItems()
        #self.__iface.messageBar().pushInfo("Grettings",str(self.__curBSS_ID))
        self.__dock.pushButton_stat_descr.clicked.connect(self.__boxplot_webview)


    def __selected_list_item(self):
        self.__dock.listWidgetBSS.clear()


    def __addlayers(self):
        wlmp=cache_path(u'wlmeasurementpoints.json')
        getWLMeasurementPoints(wlmp)
        self.__iface.addVectorLayer(wlmp, u"Points d'eau quantité", "ogr")
        wqmp=cache_path(u'wqmeasurementpoints.json')
        getWQMeasurementPoints(wqmp)
        self.__iface.addVectorLayer(wqmp, u"Points d'eau qualité", "ogr")
        il=cache_path(u'issues_list.json')
        getIssues(il)
        self.__iface.addVectorLayer(il, u"Tickets", "ogr")
        #BDLISA
        #urlWithParams = 'contextualWMSLegend=0&crs=EPSG:4326&dpiMode=7&format=image/png&layers=topp:states&styles=&url=https://ahocevar.com/geoserver/wms'
        urlWithParams='contextualWMSLegend=0&crs=EPSG:4326&dpiMode=7&featureCount=10&format=image/png&layers=ENTITES_O1_NV1&styles=&url=http://www.reseau.eaufrance.fr/geotraitements/bdlisa/services/carto/?'
        #layername = 'topp:states'
        layername = 'ENTITES_O1_NV1'
        self.__iface.addRasterLayer(urlWithParams,layername, 'wms')

        ##StringToRaster(raster)

        #urlWithParams = 'url=http://www.reseau.eaufrance.fr/geotraitements/bdlisa/services/carto/?layers=ENTITES_O1_NV1&styles=&format=image/png&crs=EPSG:4326&contextualWMSLegend=0&dpiMode=7&featureCount=10'
        #rlayer = self.QgsRasterLayer(urlWithParams, 'BDLISA', 'wms')
        #QgsMapLayerRegistry.instance().addMapLayer(rlayer)
        #self.__iface.addRasterLayer(rlayer)

    def __plotwl(self):
        wlts = cache_path(u'current_wl_ts.json')
        getWLDataFromPoint(code_bss='08025X0009/P',output_ts=wlts)
        plotWaterLevel(wlts)

    def __plotwl_webview(self):
        wlts = cache_path(u'current_wl_ts.json')
        getWLDataFromPoint(code_bss='08025X0009/P', output_ts=wlts)
        out_html=cache_path('cur_wl_ts.html')
        plotWaterLevel(wlts,trace='N', out_html=out_html)
        #url=back.plot
        #urlAddress = QtCore.QUrl(url)

        #file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "cur_wl_ts.html"))
        file_path = os.path.abspath(cache_path('cur_wl_ts.html'))
        local_url = QUrl.fromLocalFile(file_path)
        self.__dock.plot_WV.load(local_url)
        #self.__dock.plot_WV.show()
        #self.__dock.webView.QWebView(url)

    def __boxplot_webview(self):
        wlts = cache_path(u'current_wl_ts.json')
        bx_html_out=cache_path(u'cur_ts_box_plot.html')
        BoxPlotStat_Descr(wlts, trace='N', bx_out_html=bx_html_out)

        #file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "cur_ts_box_plot.html"))
        file_path=os.path.abspath(cache_path('cur_ts_box_plot.html'))
        local_url = QUrl.fromLocalFile(file_path)
        self.__dock.plot_WV.load(local_url)
        #self.__dock.plot_WV.show()

    def __cust_plotwl_webview(self):
        wlts = cache_path(u'cust_current_wl_ts.json')
        bss=[i for i in self.__curBSS_ID]
        my_bss=bss[0]
        getWLDataFromPoint(code_bss=bss, output_ts=wlts)
        back = plotWaterLevel(wlts, trace='N')
        # url=back.plot
        # urlAddress = QtCore.QUrl(url)

        file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "./cache/cur_wl_ts.html"))
        local_url = QUrl.fromLocalFile(file_path)
        self.__dock.plot_WV.load(local_url)
        # self.__dock.webView.QWebView(url)


    def __showquantile(self):
        #self.__iface.addVectorLayer()
        pass



    def __del__(self):
        self.__iface.removeToolBarIcon(self.__action)
        self.__iface.removeToolBarIcon(self.__graph)
        del self.toolbar

    def unload(self):
        pass