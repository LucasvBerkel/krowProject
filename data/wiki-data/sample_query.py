import requests
import json

url = 'https://query.wikidata.org/sparql'
query = """
PREFIX wd: <http://www.wikidata.org/entity/> 
PREFIX wdt: <http://www.wikidata.org/prop/direct/>

SELECT ?q WHERE {
  ?q wdt:P31/wdt:P279* wd:Q11424
}
"""

if __name__ == "__main__":
    r = requests.get(url, params = {'format': 'json', 'query': query})
    data = r.json()

    with open('sample_query.json', 'w') as outfile:
        json.dump(data, outfile)
