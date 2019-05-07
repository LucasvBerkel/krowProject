import git
import spotlight
import csv
import requests

import urllib.parse

from rdflib import URIRef, Graph, Literal, Namespace
from rdflib.namespace import RDF, FOAF


source_file = "/data/rotten-tomatoes/rotten_tomatoes_reviews.csv"

if __name__ == "__main__":

    git_repo = git.Repo(".", search_parent_directories=True)
    git_root = git_repo.git.rev_parse("--show-toplevel")

    only_movie_filter = {'policy': "whitelist",
                         'types': "DBpedia:Film"}

    local = Namespace("localhost:temp")
    dbpedia = Namespace("http://dbpedia.org/resource/")

    with open(git_root + source_file, 'r') as rottenTomatoesReviews:
            g = Graph()

            reader = csv.DictReader(rottenTomatoesReviews, delimiter=',')

            found_films = set()
            for idx, row in enumerate(reader):
                if idx % 1000 == 0:
                    print("Idx: {}\tFound Movies: {}".format(idx, len(found_films)))

                try:
                    annotations = spotlight.annotate('http://api.dbpedia-spotlight.org/en/annotate',
                                                     row["Review"],
                                                     confidence=0.4, support=20, filters=only_movie_filter)

                    for annotation in annotations:
                        found_films.add(annotation['URI'])

                        temp = URIRef(local + "/" + urllib.parse.quote(annotation['surfaceForm']))
                        g.add((temp, RDF.type, dbpedia.film))
                        g.add((temp, FOAF.name, Literal(annotation['surfaceForm'])))
                        print("CHECK")
                except spotlight.SpotlightException or requests.exceptions.HTTPError:
                    continue
                except KeyboardInterrupt:
                    break

            g.serialize(destination='rottenTomatoesRdf.ttl', format='turtle')
