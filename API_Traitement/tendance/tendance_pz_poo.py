# -*- coding: utf-8 -*-
"""
Test PIC'EAU
Calcul de la tendance sur les données piézo
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

class TendancesPiezoPiceau() :
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

    def getdata(self, req):
        try:
            response = urllib.request.urlopen(req)
        except Exception:
            return (['error', 'generic exception: ' + traceback.format_exc()])
        return ("ok", response)

    def run(self):
        # création fichier log
        f_log = open('logfile.txt', "w")
        f_log.write("Execution test piezo PICEAU - " + strftime("%Y-%m-%d %H:%M:%S", gmtime()) + "\n")
        f_log.write("Paramètres :\n ")
        f_log.write(" code_bss = " + ','.join(self.code_bss) + "\n")
        f_log.write(" code_param = " + ','.join(str(x) for x in self.code_param) + "\n")
        f_log.write("------------------------------------\n")

        # definition url
        #https: // hubeau.eaufrance.fr / api / v1 / niveaux_nappes / chroniques?code_bss = 05857X0144 % 2FF & size = 20 & sort = asc

        #code_bss=['05857XX0144/F','05857XX0144/F']

        #code_bss = ['05857X0144/F']
        api_hubeau = 'http://hubeau.eaufrance.fr/api/v1/niveaux_nappes/'
        objet = 'chroniques'
        fields = ['size=20000', 'sort=asc']
        str_fields = '&'.join(fields)
        #str_bss = ','.join(self.code_bss)
        str_bss = ','.join(code_bss)
        str_bss
        #str_par = ','.join(str(x) for x in self.code_param)
        #print("str_par" + str_par)
        #format = "json"

        url_hubeau = api_hubeau + objet + '?' + 'code_bss=' + str_bss +\
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

if __name__ == '__main__':
    tend_pz = TendancesPiezoPiceau(code_bss,code_param)
    tend_pz.run()