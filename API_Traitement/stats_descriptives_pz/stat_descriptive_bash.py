# -*- coding: utf-8 -*-
"""
Test PIC'EAU
Calcul d'une médiane et des quantiles pour une chronique pz
pour un ou plusieurs points d'eau'''
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
#date_debut= ['01/01/1990']
#date_fin=['01/01/2010']

code_bss = sys.argv[1].strip('[]').split(',')
# date_debut =pd.to_datetime(sys.argv[2].strip('[]'))
# date_fin =pd.to_datetime(sys.argv[3].strip('[]'))
date_debut =sys.argv[2].strip('[]')
date_fin =sys.argv[3].strip('[]')
print (code_bss)


def requete( url):
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

def getdata(req):
	try:
		response = urllib.request.urlopen(req)
	except Exception:
		return(['error','generic exception: ' + traceback.format_exc()])
	return("ok",response)



#création fichier log
f_log=open('logfile.txt',"w")
f_log.write("Execution test PICEAU - stat descriptives " + strftime("%Y-%m-%d %H:%M:%S", gmtime()) + "\n")
f_log.write("Paramètres :\n ")
f_log.write(" code_bss = " + ','.join(code_bss)+"\n")
f_log.write(" date début = " + date_debut+"\n")
f_log.write(" date fin = " + date_fin+"\n")
f_log.write("------------------------------------\n")

#definition url
# cible &size=20&date_debut_mesure=1990-01-01&date_fin_mesure=2010-01-01&sort=asc
def run(code_bss=['07783X0002/F1'],date_debut='1990-01-01', date_fin='2010-01-01'):
    api_hubeau = 'http://hubeau.eaufrance.fr/api/v1/niveaux_nappes/'
    objet = 'chroniques'
    start='date_debut_mesure='+date_debut
    stop='date_fin_mesure='+date_fin
    fields = ['size=20000',start,stop, 'sort=asc']
    str_fields = '&'.join(fields)
    # str_bss = ','.join(self.code_bss)
    str_bss = ','.join(code_bss)
    str_bss

    # str_par = ','.join(str(x) for x in self.code_param)
    # print("str_par" + str_par)
    # format = "json"

    url_hubeau = api_hubeau + objet + '?' + 'code_bss=' + str_bss + \
                 '&' + str_fields

    req = requete(url_hubeau)

    if req[0] != 'ok':
        f_log.write("Exécution annulée : " + req[1])
        f_log.close()
        sys.exit(u'Terminé')

    req[1].add_header('User-agent', 'Mozilla/5.0')

    response = getdata(req[1])

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
    return pd_table, stat_desc, res_to_return

run(code_bss, date_debut, date_fin)
# code pour qlté
# data_list = data_json['data']
# pd_table = pd.DataFrame(data_list)
# res_quantile = pd_table.groupby(['code_bss','code_param'])[['resultat']].apply(lambda x: [np.percentile(x, 25),np.percentile(x, 50),np.percentile(x, 75)]).reset_index(name='quantiles')
# res_to_file = pd.concat([res_quantile.drop(['quantiles'], axis=1), res_quantile['quantiles'].apply(pd.Series)], axis=1)
# res_to_file.columns = ['code_bss', 'code_param',"q1","q2","q3"]
# res_to_file.to_csv('quantiles.csv',sep=',')
# fin code pour qlté

tot_time = time() - start_time
f_log.write("Exécution terminée\n")
f_log.write("Temps d'exécution : %s secondes" % (time() - start_time))
f_log.close()

