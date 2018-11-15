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
start_time = time()


## Paramètres
#code_bss = ['BSS000XUUM','03376X0014/SAEP1']
#code_param = [1340,1339]

class QuantilesPiceau() :
    def __init__(self,code_bss,code_param) :
        self.code_bss = code_bss
        self.code_param = code_param

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
        #création fichier log
        f_log=open('logfile.txt',"w")
        f_log.write("Execution test PICEAU - " + strftime("%Y-%m-%d %H:%M:%S", gmtime()) + "\n")
        f_log.write("Paramètres :\n ")
        f_log.write(" code_bss = " + ','.join(self.code_bss)+"\n")
        f_log.write(" code_param = " + ','.join(str(x) for x in self.code_param)+"\n")
        f_log.write("------------------------------------\n")

        #definition url
        api_hubeau = 'http://hubeau.eaufrance.fr/api/v1/qualite_nappes/'
        objet = 'analyses'
        fields = ['code_bss','date_debut_prelevement','code_param','code_remarque_analyse','resultat','code_qualification']
        str_fields = ','.join(fields)
        str_bss = ','.join(self.code_bss)
        str_par = ','.join(str(x) for x in self.code_param)
        print("str_par"+str_par)
        format = "json"

        url_hubeau = api_hubeau + objet + '?' + 'bss_id=' + str_bss +\
                     '&code_param=' + str_par + '&fields=' + str_fields + '&format=' + format

        req = self.requete(url_hubeau)

        if req[0]!='ok':
            f_log.write("Exécution annulée : " + req[1])
            f_log.close()
            sys.exit(u'Terminé')

        req[1].add_header('User-agent', 'Mozilla/5.0')

        response = self.getdata(req[1])

        if response[0]!='ok':
            f_log.write("Exécution annulée : " + response[1])
            f_log.close()
            sys.exit(u'Terminé')


        data_json = json.load(response[1])
        count_res = data_json['count']
        f_log.write("Appel API OK\n")
        f_log.write("Nombre de résultat = " + str(count_res) +"\n")
        
        data_list = data_json['data']
        pd_table = pd.DataFrame(data_list)
        #print(data_list)
        #print(pd_table)
        #print(pd_table.groupby(['code_bss','code_param']))
        res_quantile = pd_table.groupby(['code_bss','code_param'])[['resultat']].apply(lambda x: [np.percentile(x, 25),np.percentile(x, 50),np.percentile(x, 75)]).reset_index(name='quantiles')
        res_to_file = pd.concat([res_quantile.drop(['quantiles'], axis=1), res_quantile['quantiles'].apply(pd.Series)], axis=1)
        res_to_file.columns = ['code_bss', 'code_param',"q1","q2","q3"]
        res_to_file.to_csv('quantiles.csv',sep=',')

        tot_time = time() - start_time
        f_log.write("Exécution terminée\n")
        f_log.write("Temps d'exécution : %s secondes" % (time() - start_time))
        f_log.close()

if __name__ == '__main__':
    code_bss = sys.argv[1].strip('[]').split(',')
    code_param = list(int(x) for x in sys.argv[2].strip('[]').split(',')) # l'utilisation de map est déconseillé sous python 3
    monQuantilesPiceau = QuantilesPiceau(code_bss,code_param)
    monQuantilesPiceau.run()