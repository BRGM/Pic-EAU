# -*- coding: utf-8 -*-
"""
Test PIC'EAU
Calcul d'une médiane et des quantiles pour un ou plusieurs paramètres
et un ou plusieurs points d'eau'''
"""
import sys
import json
import urllib.request,urllib.error
import pandas as pd
import numpy as np
from time import time, gmtime, strftime
import traceback
import cherrypy




## Paramètres
#code_bss = ['BSS000XUUM','03376X0014/SAEP1']
#code_param = [1340,1339]

class QuantilesPiceau() :
    def __init__(self,code_bss,code_param) :
        self.code_bss = code_bss
        self.code_param = code_param
        self.resultat = None
        self.error = None

    def requete(self,url):
        try:
            req = urllib.request.Request(url)
            print(url)
        except urllib.request.HTTPError as e:
            return(['error','HTTPError = ' + str(e.code)])
        except urllib.request.URLError as e:
            return(['error','URLError = ' + str(e.reason)])
        except urllib.error.HTTPError as e:
            return(['error','HTTPException'])
        except Exception:
            return(['error','generic exception: ' + traceback.format_exc()])
        return('ok',req)

    def getdata(self,req):
        try:
            response = urllib.request.urlopen(req)
        except Exception:
            return(['error','generic exception: ' + traceback.format_exc()])
        return("ok",response)

    def run(self):
        start_time = time()
        
        #création fichier log
        cherrypy.log("Execution test PICEAU - " + strftime("%Y-%m-%d %H:%M:%S", gmtime()) + "\n")
        cherrypy.log("Paramètres :\n ")
        cherrypy.log(" code_bss = " + ','.join(self.code_bss)+"\n")
        cherrypy.log(" code_param = " + ','.join(str(x) for x in self.code_param)+"\n")
        cherrypy.log("------------------------------------\n")

        #definition url
        api_hubeau = 'http://hubeau.eaufrance.fr/api/v1/qualite_nappes/'
        objet = 'analyses'
        fields = ['code_bss','date_debut_prelevement','code_param','code_remarque_analyse','resultat','code_qualification']
        str_fields = ','.join(fields)
        str_bss = ','.join(self.code_bss)
        str_par = ','.join(str(x) for x in self.code_param)
        format = "json"

        url_hubeau = api_hubeau + objet + '?' + 'bss_id=' + str_bss +\
                     '&code_param=' + str_par + '&fields=' + str_fields + '&format=' + format

        req = self.requete(url_hubeau)

        if req[0]!='ok':
            self.error = response[1]
            return

        req[1].add_header('User-agent', 'Mozilla/5.0')

        response = self.getdata(req[1])

        if response[0]!='ok':
            self.error = response[1]
            return


        data_json = json.load(response[1])
        count_res = data_json['count']
        cherrypy.log("Appel API OK\n")
        cherrypy.log("Nombre de résultat = " + str(count_res) +"\n")

        data_list = data_json['data']
        pd_table = pd.DataFrame(data_list)
        res_quantile = pd_table.groupby(['code_bss','code_param'])[['resultat']].apply(lambda x: [np.percentile(x, 25),np.percentile(x, 50),np.percentile(x, 75)]).reset_index(name='quantiles')
        res_to_file = pd.concat([res_quantile.drop(['quantiles'], axis=1), res_quantile['quantiles'].apply(pd.Series)], axis=1)
        res_to_file.columns = ['code_bss', 'code_param',"q1","q2","q3"]
        #res_to_file.to_csv('quantiles.csv',sep=',')
        cherrypy.log(res_to_file.to_json())
        self.resultat=res_to_file.to_json()

        tot_time = time() - start_time
        cherrypy.log("Exécution terminée\n")
        cherrypy.log("Temps d'exécution : %s secondes" % (time() - start_time))

@cherrypy.expose      
class Webservice(object):
    @cherrypy.expose
    def GET(self,code_bss=None,code_param=None):
        if code_bss is None or code_param is None:
            return json.dumps({"statut":"code bss ou code param manquant"})
        else :    
            cherrypy.log(code_bss)
            cherrypy.log(code_param)
            code_bss = code_bss.strip('[]').split(',')
            code_param = list(int(x) for x in code_param.strip('[]').split(','))
            cherrypy.log(str(code_bss))
            cherrypy.log(str(code_param))
            monQuantilesPiceau = QuantilesPiceau(code_bss,code_param)
            monQuantilesPiceau.run()
            if monQuantilesPiceau.error is not None :
                return json.dumps({"error":monQuantilesPiceau.error})
            else :
                return monQuantilesPiceau.resultat
    
    
    def POST(self, another_string):
        return "non implemented"
    
    def PUT(self, another_string):
        return "non implemented"

    def DELETE(self):
        return "non implemented"
        
if __name__ == '__main__':
    #monQuantilesPiceau = QuantilesPiceau(code_bss,code_param)
    #monQuantilesPiceau.run()
    
    cherrypy.log("debut du programme")
    cherrypy.config.update("piceau.config")
    cherrypy.quickstart(Webservice(),"/quantiles_piceau","piceau.config")