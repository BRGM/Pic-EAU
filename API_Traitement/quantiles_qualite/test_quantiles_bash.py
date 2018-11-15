# -*- coding: utf-8 -*-
"""
Test PIC'EAU
Calcul d'une médiane et des quantiles pour un ou plusieurs paramètres
et un ou plusieurs points d'eau'''
"""
import sys
import json,urllib2
import pandas as pd
import numpy as np
from time import time, gmtime, strftime
import traceback
start_time = time()

## Paramètres
#code_bss = ['BSS000XUUM','03376X0014/SAEP1']
#code_param = [1340,1339]

code_bss = sys.argv[1].strip('[]').split(',')
code_param =map(int, sys.argv[2].strip('[]').split(',')) 
print code_bss

def requete(url):
	try:
		req = urllib2.Request(url_hubeau)
		print url_hubeau
	except urllib2.HTTPError, e:
		return(['error','HTTPError = ' + str(e.code)])
	except urllib2.URLError, e:
		return(['error','URLError = ' + str(e.reason)])
	except httplib.HTTPException, e:
		return(['error','HTTPException'])
	except Exception:
		return(['error','generic exception: ' + traceback.format_exc()])
	return('ok',req)

def getdata(req):
	try:
		response = urllib2.urlopen(req)
	except Exception:
		return(['error','generic exception: ' + traceback.format_exc()])
	return("ok",response)



#création fichier log
f_log=open('logfile.txt',"w")
f_log.write("Execution test PICEAU - " + strftime("%Y-%m-%d %H:%M:%S", gmtime()) + "\n")
f_log.write("Paramètres :\n ")
f_log.write(" code_bss = " + ','.join(code_bss)+"\n")
f_log.write(" code_param = " + ','.join(str(x) for x in code_param)+"\n")
f_log.write("------------------------------------\n")

#definition url
api_hubeau = 'http://hubeau.eaufrance.fr/api/v1/qualite_nappes/'

objet = 'analyses'
fields = ['code_bss','date_debut_prelevement','code_param','code_remarque_analyse','resultat','code_qualification']
str_fields = ','.join(fields)
str_bss = ','.join(code_bss)
str_par = ','.join(str(x) for x in code_param)
format = "json"

url_hubeau = api_hubeau + objet + '?' + 'bss_id=' + str_bss +\
             '&code_param=' + str_par + '&fields=' + str_fields + '&format=' + format


req = requete(url_hubeau)

if req[0]!='ok':
	f_log.write("Exécution annulée : " + req[1])
	f_log.close()
	sys.exit(u'Terminé')

req[1].add_header('User-agent', 'Mozilla/5.0')

response = getdata(req[1])

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
res_quantile = pd_table.groupby(['code_bss','code_param'])[['resultat']].apply(lambda x: [np.percentile(x, 25),np.percentile(x, 50),np.percentile(x, 75)]).reset_index(name='quantiles')
res_to_file = pd.concat([res_quantile.drop(['quantiles'], axis=1), res_quantile['quantiles'].apply(pd.Series)], axis=1)
res_to_file.columns = ['code_bss', 'code_param',"q1","q2","q3"]
res_to_file.to_csv('quantiles.csv',sep=',')


tot_time = time() - start_time
f_log.write("Exécution terminée\n")
f_log.write("Temps d'exécution : %s secondes" % (time() - start_time))
f_log.close()

