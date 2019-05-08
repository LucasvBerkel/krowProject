import git
import spotlight
import csv
import requests
import time

import urllib.parse
from nltk.corpus import wordnet as wn

from rdflib import URIRef, Graph, Literal, Namespace
from rdflib.namespace import RDF, FOAF


source_file = "/data/rotten-tomatoes/rotten_tomatoes_reviews.csv"

if __name__ == "__main__":

    git_repo = git.Repo(".", search_parent_directories=True)
    git_root = git_repo.git.rev_parse("--show-toplevel")

    only_movie_filter = {'policy': "whitelist",
                         'types': "DBpedia:Film"}

    local = Namespace("localhost:rottenTomatoes/")
    dbpedia = Namespace("http://dbpedia.org/resource/")

    with open(git_root + source_file, 'r') as rottenTomatoesReviews:
            g = Graph()

            reader = csv.DictReader(rottenTomatoesReviews, delimiter=',')

            found_films = set()
            start_time = time.time()
            for idx, row in enumerate(reader):
                if idx % 1000 == 0:
                    elapsed_time = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))
                    print("Idx: {}\tFound Movies: {}\tElapsed time: {}".format(idx, len(found_films), elapsed_time))
                    start_time = time.time()
                try:
                    # annotations = spotlight.annotate('http://api.dbpedia-spotlight.org/en/annotate',
                    #                                  row["Review"],
                    #                                  confidence=0.4, support=20, filters=only_movie_filter)

                    annotations = spotlight.annotate('http://localhost:2222/rest/annotate',
                                                     row["Review"],
                                                     confidence=0.4,
                                                     support=20,
                                                     filters=only_movie_filter,
                                                     spotter='Default')

                    for annotation in annotations:
                        found_films.add(annotation['URI'])
                        title = annotation['surfaceForm'].title()

                        temp = URIRef(local + urllib.parse.quote(title))
                        g.add((temp, RDF.type, dbpedia.film))
                        g.add((temp, FOAF.name, Literal(title)))

                        splitSentence = row['Review'].split()
                        for word in splitSentence:
                            for tmp in wn.synsets(word):
                                if tmp.pos() == "a":
                                    g.add((temp, local.describedAs, Literal(word.title())))
                                    break
                except spotlight.SpotlightException or requests.exceptions.HTTPError:
                    continue
                except KeyboardInterrupt:
                    break
                except BaseException as e:
                    print(e)
                    continue

            g.serialize(destination='rottenTomatoesRdf.ttl', format='turtle')
