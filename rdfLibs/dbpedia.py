import git
import time
import requests
import json

import urllib.parse

from rdflib import URIRef, Graph, Literal, Namespace
from rdflib.namespace import RDF, FOAF

url = 'https://query.wikidata.org/sparql'
query = """
PREFIX wd: <http://www.wikidata.org/entity/> 
PREFIX wdt: <http://www.wikidata.org/prop/direct/>

SELECT ?entity ?dateOfBirth
WHERE{ 
   ?entity rdfs:label "{}"@en . 
   ?entity wdt:P569 ?dateOfBirth
}
"""

first_query_part = """
PREFIX wd: <http://www.wikidata.org/entity/> 
PREFIX wdt: <http://www.wikidata.org/prop/direct/>

SELECT ?entity ?dateOfBirth
WHERE{ 
   ?entity rdfs:label \""""

end_query_part = """"@en . 
    ?entity wdt:P569 ?dateOfBirth
}"""

if __name__ == "__main__":

    git_repo = git.Repo(".", search_parent_directories=True)
    git_root = git_repo.git.rev_parse("--show-toplevel")

    local = Namespace("localhost:imdb/")
    dbpedia = Namespace("http://dbpedia.org/resource/")
    wdt = Namespace("http://www.wikidata.org/prop/direct/")

    g = Graph()

    g.parse("imdbRdf.ttl", format="ttl")

    imdb_persons_uri = set()

    for person, p, name in g.triples((None, FOAF.name, None)):
        imdb_persons_uri.add((str(person), name))

    found_persons = set()

    g = Graph()

    start_time = time.time()
    print("Starting searching person info")
    for idx, row in enumerate(imdb_persons_uri):
        try:

            if idx % 100000 == 0:
                elapsed_time = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))
                print("Idx: {}\tFound Persons: {}\tElapsed time: {}".format(idx, len(found_persons), elapsed_time))
                start_time = time.time()

            query = "{}{}{}".format(first_query_part, row[1], end_query_part)

            r = requests.get(url, params={'format': 'json', 'query': query})
            data = r.json()

            temp = URIRef(row[0])
            g.add((temp, wdt.p569, data))
            break
        except KeyboardInterrupt:
            break

    g.serialize(destination='dbpediaRdf.ttl', format='turtle')
