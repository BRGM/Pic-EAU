import requests
import json
import re

URL_GITLAB_PROJECT = "https://gitlab.com/api/v4/projects/7473129/issues?state=opened"
GEOJSON_RE = re.compile(r"'''(.*)'''",re.S)

def getIssues(outputfile='issues.geojson') :
    resultat = []
    requete = requests.get(URL_GITLAB_PROJECT)
    data = json.loads(requete.text)
    for issues in data :
        description = issues['description']
        if description.find("# geometry")==-1 :
            print("# geometry not found in ",description)
            continue   
        regexp = GEOJSON_RE.findall(description)
        if regexp :
            geometry = json.loads(regexp[0])
            geometry['features'][0]['properties']['title']=issues['title']
            geometry['features'][0]['properties']['url']=issues['web_url']
            if len(resultat)==0 :
                resultat=geometry
            else :
                resultat['features'].append(geometry['features'][0])
        else :
            print("geojson into triple-quote not found")

    with open(outputfile, 'w') as o:
                return o.write(json.dumps(resultat))
    #open(outputfile,'w').write(json.dumps(resultat))
        
        
if __name__=="__main__":
    getIssues()