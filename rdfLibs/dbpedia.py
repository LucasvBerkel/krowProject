import git
import time
import requests
from dateutil.parser import parse

from rdflib import URIRef, Graph, Literal, Namespace
from rdflib.namespace import RDF, FOAF, OWL

url = 'https://query.wikidata.org/sparql'
query = """
PREFIX wd: <http://www.wikidata.org/entity/> 
PREFIX wdt: <http://www.wikidata.org/prop/direct/>

SELECT ?entity ?dateOfBirth
WHERE{ 
   ?entity rdfs:label "{}"@en . 
   ?entity wdt:P569 ?dateOfBirth.
    ?entity wdt:P21 ?gender.
    ?entity wdt:P27 ?countyOfOrigin.
    ?entity wdt:P26 ?spouse
}
"""

first_query_part = """
PREFIX wd: <http://www.wikidata.org/entity/> 
PREFIX wdt: <http://www.wikidata.org/prop/direct/>

SELECT ?entity ?gender ?dateOfBirth ?countryOfOrigin ?spouse ?spouseName ?spouseDateOfBirth ?spouseGender ?spouseCountryOfOrigin
WHERE{ 
   ?entity rdfs:label \""""

end_query_part = """"@en . 
    OPTIONAL{   ?entity wdt:P569 ?dateOfBirth. }
    
    OPTIONAL{   ?entity wdt:P21 / rdfs:label ?gender.
                filter(langMatches(lang(?gender),"EN")). }
    
    OPTIONAL{   ?entity wdt:P27 / rdfs:label ?countryOfOrigin.
                filter(langMatches(lang(?countryOfOrigin),"EN")). }
    
    OPTIONAL{   ?entity wdt:P26 ?spouse. 
                ?spouse rdfs:label ?spouseName. 
                OPTIONAL{   ?spouse wdt:P569 ?spouseDateOfBirth. }.
                
                OPTIONAL{   ?spouse wdt:P21 / rdfs:label ?spouseGender.
                            filter(langMatches(lang(?spouseGender), "EN")).}.
                
                OPTIONAL{   ?spouse wdt:P27 / rdfs:label ?spouseCountryOfOrigin.
                            filter(langMatches(lang(?spouseCountryOfOrigin), "EN")).}}
}"""

if __name__ == "__main__":

    git_repo = git.Repo(".", search_parent_directories=True)
    git_root = git_repo.git.rev_parse("--show-toplevel")

    local = Namespace("localhost:imdb/")
    dbpedia = Namespace("http://dbpedia.org/resource/")
    wdt = Namespace("http://www.wikidata.org/prop/direct/")

    g = Graph()

    g.parse(git_root + "/rdfLibs/imdbRdf.ttl", format="ttl")

    imdb_persons_uri = set()

    for person, p, name in g.triples((None, FOAF.name, None)):
        imdb_persons_uri.add((str(person), name))

    print("Persons in imdb dataset: {}".format(len(imdb_persons_uri)))

    found_persons = set()

    g = Graph()

    start_time = time.time()
    total_start_time = time.time()
    print("Starting searching person info")
    for idx, row in enumerate(imdb_persons_uri):
        try:

            if idx % 100 == 0:
                elapsed_time = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))
                print("Idx: {}\tFound Persons: {}\tElapsed time: {}".format(idx, len(found_persons), elapsed_time))
                start_time = time.time()

            query = "{}{}{}".format(first_query_part, row[1], end_query_part)

            r = requests.get(url, params={'format': 'json', 'query': query})

            data = r.json()

            if data['results']['bindings']:

                person_data = data['results']['bindings'][0]

                person_uri = person_data['entity']['value']
                found_persons.add(person_uri)

                temp_person = URIRef(row[0])
                g.add((temp_person, OWL.sameAs, URIRef(person_uri)))
                g.add((temp_person, RDF.type, FOAF.Person))

                if 'dateOfBirth' in person_data:
                    dateOfBirth = parse(person_data['dateOfBirth']['value'])
                    g.add((temp_person, wdt.p569, Literal(dateOfBirth)))

                if 'gender' in person_data:
                    g.add((temp_person, wdt.P21, Literal(person_data['gender']['value'])))

                if 'countryOfOrigin' in person_data:
                    g.add((temp_person, wdt.P27, Literal(person_data['countryOfOrigin']['value'])))

                if 'spouseName' in person_data:
                    temp_married_person = URIRef(person_data['spouse']['value'])

                    g.add((temp_married_person, RDF.type, FOAF.person))
                    g.add((temp_person, FOAF.spouseOf, temp_married_person))

                    g.add((temp_married_person, FOAF.name, Literal(person_data['spouseName']['value'])))
                    if 'spouseDateOfBirth' in person_data:
                        g.add((temp_married_person, wdt.P569, Literal(person_data['spouseDateOfBirth']['value'])))
                    if 'spouseGender' in person_data:
                        g.add((temp_married_person, wdt.P21, Literal(person_data['spouseGender']['value'])))
                    if 'spouseCountryOfOrigin' in person_data:
                        g.add((temp_married_person, wdt.P27, Literal(person_data['spouseCountryOfOrigin']['value'])))
        except KeyboardInterrupt:
            break

    g.serialize(destination=git_root + '/rdfLibs/dbpediaRdf.ttl', format='turtle')

    elapsed_time = time.strftime("%H:%M:%S", time.gmtime(time.time() - total_start_time))
    print("Elapsed time: {}".format(elapsed_time))
