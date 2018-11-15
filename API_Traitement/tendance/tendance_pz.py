# -*- coding: utf-8 -*-
"""
Test PIC'EAU
Calcul de la tendance sur les données piézo
et un ou plusieurs points d'eau. La tendance peut être calculé si :
il existe au moins une donnée par mois calendaire,
il existe au mois 10 données mensuelles dans une année
il existe au moins 10 années qui respectent ces critères'''
"""
import sys
import json
import urllib.request,urllib.error
import pandas as pd
import numpy as np
from time import time, gmtime, strftime
import traceback
from mk_test import MannKendallTest

#import scipy
#from .mk_test_poo import MannKendall

start_time = time()


def requete(url):
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
        return (['error', 'generic exception: ' + traceback.format_exc()])
    return ("ok", response)

def agg_on_month(df):
    pass

def run(code_bss):
    # création fichier log
    f_log = open('logfile.txt', "w")
    f_log.write("Execution test piezo PICEAU - " + strftime("%Y-%m-%d %H:%M:%S", gmtime()) + "\n")
    f_log.write("Paramètres :\n ")
    f_log.write(" code_bss = " + ','.join(code_bss) + "\n")
    #f_log.write(" code_param = " + ','.join(str(x) for x in self.code_param) + "\n")
    f_log.write("------------------------------------\n")

    # definition url
    # https: // hubeau.eaufrance.fr / api / v1 / niveaux_nappes / chroniques?code_bss = 05857X0144 % 2FF & size = 20 & sort = asc

    # code_bss=['05857XX0144/F','05857XX0144/F']

    # code_bss = ['05857X0144/F']
    api_hubeau = 'http://hubeau.eaufrance.fr/api/v1/niveaux_nappes/'
    objet = 'chroniques'
    fields = ['size=20000', 'sort=asc']
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
    print(pd_table)
    return(pd_table)

run(['07117X0011/F'])

url_hubeau='http://hubeau.eaufrance.fr/api/v1/niveaux_nappes/chroniques?code_bss=07117X0011/F&size=20000&sort=asc'
req = requete(url_hubeau)
req[1].add_header('User-agent', 'Mozilla/5.0')
res=getdata(req[1])
dt_json=json.load(res[1])
dt_list=dt_json['data']
df=pd.DataFrame(dt_list)

# converts in datetime
df['date_mesure']=pd.to_datetime(df['date_mesure'])
# add month and year columns to perform grouping later on
df['year'], df['month'] = df['date_mesure'].dt.year, df['date_mesure'].dt.month

# count of data per month, per year
# use of reset_index() to preserve year and month columns, otherwise, passed to index
df_per_m_per_y=df.groupby(['year','month']).count().reset_index()

# index of month where there is at least 1 measurement
idx_m =df_per_m_per_y.loc[:,'niveau_nappe_eau'].values >= 1
# count of month per year, where ndata>1
df_per_y=df_per_m_per_y[idx_m].groupby(['year']).count()
# performing monthly average on water level where month is elligible
# all monthly average
df_month_mean=df.groupby(['year','month']).mean().reset_index()
df_month_mean['day'] = np.repeat(15,len(df_month_mean['year']))
df_month_mean['date'] = pd.to_datetime(df_month_mean.loc[:,['year', 'month', 'day']], format='%d%m%Y')

# elligible data
df_month_mean=df_month_mean[idx_m]

#index of year where 10/12 month with at least 1 data/month are available
idx_y=df_per_y.loc[:,'niveau_nappe_eau'].values >= 10
# number of year that satisfies the criteria
nb_y_pass=df_per_y[idx_y].shape[0]

if nb_y_pass>10:
    print(u'Plus de 10 valeurs de moyennes mensuelles, test peut être fait')
    # t is the index
    # x is the data
    MannKendallTest(t=np.array(df_month_mean['timestamp_mesure'].values),x=np.array(df_month_mean['niveau_nappe_eau'].values),eps=0.01,alpha=0.05, Ha='upordown')


t=np.array(df_month_mean['date'].values)
x=np.array(df_month_mean['niveau_nappe_eau'].values)
np.corrcoef(t,x)

df_month_mean['date'].values
np.ndarray(shape=(1, len(df_month_mean['date'])),data=df_month_mean['date'].values,dtype=float, order='F', buffer=None)
np.array(df_month_mean['date'].values)

GB=df.groupby('year').count()
print(GB)
idx=GB.loc[:,'timestamp_mesure'].values> (365/2)

# nb d'années qui ont plus de 182.5 données/an :
GB[idx].shape[0]

# moy annuelles
moy_an=df.groupby('year').mean()
# passage en pd.Series
wl_data=moy_an.loc[:,'niveau_nappe_eau']
# ACF des données au lag 3 ans sur données moyennes annuelles
wl_data.autocorr(lag=2)


