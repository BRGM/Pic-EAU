# coding=utf8

"""
USAGE: python script to fetch all measurement points from Hub'eau and create write a txt file from it
"""

import requests
import json
import sys
import pandas as pd
#print("System encoding"+sys.getfilesystemencoding())

def getQuantile(li_bss=u'[BSS000XUUM,03376X0014.SAEP1]', li_param=u'[1340,1339]', service=u'quantiles_piceau/'):
    # on attend en paramètre : li_bss: liste de string et li_param: liste de code sandre, format string
    # li_bss = u'[BSS000XUUM,03376X0014.SAEP1]'
    # li_param = u'[1340,1339]'
    url_piceau = u'http://piceau.brgm-rec.fr:8080/'
    service = service
    url_quantile = u'{}{}{li_bss}/{li_param}'.format(
        url_piceau,
        service,
        li_bss=li_bss,
        li_param=li_param
    )
    print(url_quantile)
    req_piceau = requests.get(url_quantile)
    assert (req_piceau.status_code == 200)

    quantile_df=pd.read_json(req_piceau.text)

    return req_piceau.text, quantile_df

    # assert(req_piceau.status_code)
    # http://piceau.brgm-rec.fr:8080/quantiles_piceau/[BSS000XUUM,03376X0014.SAEP1]/[1340,1339]

if __name__=='__main__':
    getQuantile()