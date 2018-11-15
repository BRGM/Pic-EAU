# -*- coding= utf8 -*-

"""
USAGE: python script to fetch all measurement points from Hub'eau and create write a txt file from it
"""

import requests
import json
import sys

#WL:waterlevel
#WQ:waterquality

#print("System encoding"+sys.getfilesystemencoding())

def getWLMeasurementPoints(output_geojson='wl_hubeau_output.json'):
    url_hubeau=u'http://hubeau.eaufrance.fr/api/v1/'
    req_object=u'niveaux_nappes/'
    bbox=u'bbox={bbox_c1}%2C{bbox_c2}%2C{bbox_c3}%2C{bbox_c4}'.format(
        bbox_c1=-1.28,#1.6194,
        bbox_c2 = 44.0,#47.7965,
        bbox_c3 = 0.3,#2.1910,
        bbox_c4 = 45.0#47.9988
    )
    url='{}{}{stations}{bbox}&size={size}&format={answer_format}'.format(
        url_hubeau,
        req_object,
        stations='stations?',
        bbox=u'bbox?',
        size=20000,
        answer_format=u'geojson')
    #http://hubeau.eaufrance.fr/api/v1/qualite_nappes/stations?size=1000&format=json
    #http://hubeau.eaufrance.fr/api/v1/niveaux_nappes/stations?bbox?&size=10000&format=geojson

    #print(url)
    points_coordinates = requests.get(url)
    #print(points_coordinates)

    # on suppose qu'il renvoie 200
    assert(points_coordinates.status_code in [200,206])

    #req_answer=points_coordinates.text
    #print(req_answer)
    with open(output_geojson,'w') as o:
        return o.write(points_coordinates.text)
    #return open(output_geojson, 'w').write(points_coordinates.text)


def getWLDataFromPoint(code_bss='08025X0009/P',output_ts='./cache/current_wl_ts.json'):
    url_hubeau=u'http://hubeau.eaufrance.fr/api/v1/'
    req_object=u'niveaux_nappes/'
    #http://hubeau.eaufrance.fr/api/v1/niveaux_nappes/chroniques?code_bss=05857X0144%2FF&size=20
    url_ts='{}{}{chroniques}code_bss={code_bss}&size={size}'.format(
        url_hubeau,
        req_object,
        chroniques='chroniques?',
        code_bss=code_bss,
        size=20000)
    hubeau_current_ts=requests.get(url_ts)
    assert(hubeau_current_ts.status_code in [200,206])
    with open(output_ts,'w') as o:
        return o.write(hubeau_current_ts.text)
    # return open(output_ts, 'w').write(hubeau_current_ts.text)


def getWQMeasurementPoints(output_geojson='./cache/wq_hubeau_output.json'):
    url_hubeau=u'http://hubeau.eaufrance.fr/api/v1/'
    req_object = u'qualite_nappes/'
    # http: // hubeau.eaufrance.fr / api / v1 / qualite_nappes / stations?size = 10000 & format = json
    url='{}{}{stations}&size={size}&format={answer_format}'.format(
        url_hubeau,
        req_object,
        stations='stations?',
        size=20000,
        answer_format=u'geojson')
    points_coordinates = requests.get(url)
    # on suppose qu'il renvoie 200|206
    assert(points_coordinates.status_code in [200,206])
    #return open(output_geojson, 'w').write((points_coordinates.text.encode('utf8')).decode('utf8', "replace"))
    with open(output_geojson,'w') as o:
        return o.write(points_coordinates.text.replace('\x90', '?'))
    #return open(output_geojson, 'w').write(points_coordinates.text.replace('\x90', '?'))
    #points_coordinates

def getWQDataFromPoint(bss_id='BSS000XUUM',output_ts='current_wq_ts.json'):
    #http: // hubeau.eaufrance.fr / api / v1 / qualite_nappes / analyses?bss_id = BSS000XUUM & size = 20
    url_hubeau=u'http://hubeau.eaufrance.fr/api/v1/'
    req_object=u'qualite_nappes/'
    url_ts='{}{}{analyses}bss_id={bss_id}&size={size}'.format(
        url_hubeau,
        req_object,
        analyses='analyses?',
        bss_id=bss_id,
        size=5000)
    hubeau_current_ts=requests.get(url_ts)
    assert(hubeau_current_ts.status_code in [200,206])
    with open(output_ts,'w') as o:
        o.write(hubeau_current_ts.text)
    #return  open(output_ts, 'w').write(hubeau_current_ts.text)


if __name__=="__main__":
    getWLMeasurementPoints()
    getWQMeasurementPoints()
    getWLDataFromPoint()
    getWQDataFromPoint()