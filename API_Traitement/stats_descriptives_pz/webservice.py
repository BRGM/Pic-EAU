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

class StatDescriptives_pz():
    def __init__(self, code_bss, date_debut, date_fin):
        self.code_bss=code_bss
        self.date_debut=date_debut
        self.date_fin=date_fin

    def requete(self, url):
        try:
            req = urllib.request.Request(url)
            print(url)
        except urllib.request.HTTPError as e:
            return (['error', 'HTTPError = ' + str(e.code)])
        except urllib.request.URLError as e:
            return (['error', 'URLError = ' + str(e.reason)])
        except urllib.error.HTTPError as e:
            return (['error', 'HTTPException'])
        except Exception:
            return (['error', 'generic exception: ' + traceback.format_exc()])
        return ('ok', req)

    def getdata(self,req):
        try:
            response = urllib.request.urlopen(req)
        except Exception:
            return(['error','generic exception: ' + traceback.format_exc()])
        return("ok",response)


    def run(self):
        #création fichier log
        f_log=open('logfile.txt',"w")
        f_log.write("Execution test PICEAU - stat descriptives " + strftime("%Y-%m-%d %H:%M:%S", gmtime()) + "\n")
        f_log.write("Paramètres :\n ")
        f_log.write(" code_bss = " + ','.join(self.code_bss)+"\n")
        f_log.write(" date début = " + self.date_debut+"\n")
        f_log.write(" date fin = " + self.date_fin+"\n")
        f_log.write("------------------------------------\n")

        #definition url
        # cible &size=20&date_debut_mesure=1990-01-01&date_fin_mesure=2010-01-01&sort=asc
        #def run(code_bss=['07783X0002/F1'],date_debut='1990-01-01', date_fin='2010-01-01'):
        api_hubeau = 'http://hubeau.eaufrance.fr/api/v1/niveaux_nappes/'
        objet = 'chroniques'
        start='date_debut_mesure='+self.date_debut
        stop='date_fin_mesure='+self.date_fin
        fields = ['size=20000',start,stop, 'sort=asc']
        str_fields = '&'.join(fields)
        # str_bss = ','.join(self.code_bss)
        str_bss = ','.join(self.code_bss)

        url_hubeau = api_hubeau + objet + '?' + 'code_bss=' + str_bss + \
                     '&' + str_fields

        req = self.requete(url_hubeau)

        if req[0] != 'ok':
            f_log.write("Exécution annulée : " + req[1])
            f_log.close()
            sys.exit(u'Terminé')

        req[1].add_header('User-agent', 'Mozilla/5.0')

        response = self.getdata(req[1])

        if response[0] != 'ok':
            f_log.write("Exécution annulée : " + response[1])
            f_log.close()
            sys.exit(u'Terminé')

        data_json = json.load(response[1])
        count_res = data_json['count']
        f_log.write("Appel API OK\n")
        f_log.write("Nombre de résultat = " + str(count_res) + "\n")

        data_list = data_json['data']
        pd_table = pd.DataFrame(data_list)
        # calcul des métriques
        stat_desc=pd_table.loc[:, ['code_bss', 'date_mesure', 'niveau_nappe_eau']].groupby(['code_bss']).describe()
        res_to_return=stat_desc.to_json(orient='index')
        #res_to_return = stat_desc.to_dict(orient='index')
        dim=pd_table.shape
        print(pd_table.head(10))
        print(dim)
        print(stat_desc)
        print(res_to_return)
        f_log.write("Stats renvoyées ="+ str(res_to_return)+ "\n")

        tot_time = time() - start_time
        f_log.write("Exécution terminée\n")
        f_log.write("Temps d'exécution : %s secondes" % (time() - start_time))
        f_log.close()

        # ecrire sur le disque un json avec le res.

        return pd_table, stat_desc, res_to_return, open('stat_descr.json', 'w').write(res_to_return)

@cherrypy.expose      
class Webservice(object):
    @cherrypy.expose
    def GET(self,code_bss=None,date_debut=None, date_fin=None):
        if code_bss is None or date_debut is None or date_fin is None:
            return json.dumps({"statut":"code bss ou date_fin ou date_début manquant"})
        else :    
            cherrypy.log(code_bss)
            cherrypy.log(code_param)
            code_bss = code_bss.strip('[]').split(',')
            code_param = list(int(x) for x in code_param.strip('[]').split(','))
            cherrypy.log(str(code_bss))
            cherrypy.log(str(code_param))
            monQuantilesPiceau = StatDescriptives_pz(code_bss,date_debut, date_fin)
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