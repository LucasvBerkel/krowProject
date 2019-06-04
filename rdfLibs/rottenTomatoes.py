import git
import spotlight
import csv
import requests
import time

from nltk.corpus import wordnet as wn

from rdflib import URIRef, Graph, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL


source_file = "/data/rotten-tomatoes/rotten_tomatoes_reviews.csv"


def create_rot_graph():
    git_repo = git.Repo(".", search_parent_directories=True)
    git_root = git_repo.git.rev_parse("--show-toplevel")

    only_movie_filter = {'policy': "whitelist",
                         'types': "DBpedia:Film"}

    local = Namespace("localhost:movieCastingNamespace/")

    total_start_time = time.time()

    with open(git_root + source_file, 'r') as rottenTomatoesReviews:
        g = Graph()

        g.add((URIRef(local + "Review"), RDFS.subClassOf, OWL.Class))

        reader = csv.DictReader(rottenTomatoesReviews, delimiter=',')

        found_films = set()
        start_time = time.time()
        for idx, row in enumerate(reader):
            if idx % 100000 == 0:
                elapsed_time = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))
                print("Idx: {}\tFound Movies: {}\tElapsed time: {}".format(idx, len(found_films), elapsed_time))
                start_time = time.time()
            try:
                annotations = spotlight.annotate('http://localhost:2222/rest/annotate',
                                                 row["Review"],
                                                 confidence=0.4,
                                                 support=20,
                                                 filters=only_movie_filter,
                                                 spotter='Default')

                for annotation in annotations[:1]:
                    found_films.add(annotation['URI'])
                    title = annotation['surfaceForm'].title()

                    # Add surface label to film
                    g.add((URIRef(annotation['URI']), local.hasSurfaceForm, Literal(title)))

                    # Initiate review
                    temp_review = URIRef(local + "review_{}".format(idx))
                    g.add((temp_review, RDF.type, URIRef(local + "Review")))

                    # Link review to film
                    g.add((temp_review, local.describesAsReview, URIRef(annotation['URI'])))

                    # Add text to review
                    # g.add((temp_review, local.hasText, Literal(row['Review'])))

                    # Abstract adjectives from review
                    split_sentence = row['Review'].split()
                    for word in split_sentence:
                        for tmp in wn.synsets(word):
                            if tmp.pos() == "a":
                                g.add((temp_review, local.hasAdjective, Literal(word.title())))
                            break
            except spotlight.SpotlightException or requests.exceptions.HTTPError:
                continue
            except KeyboardInterrupt:
                break
            except BaseException as e:
                print(e)
                continue

        g.serialize(destination=git_root + '/rdfLibs/rottenTomatoesRdf.ttl', format='turtle')

        elapsed_time = time.strftime("%H:%M:%S", time.gmtime(time.time() - total_start_time))
        print("Elapsed time: {}".format(elapsed_time))


if __name__ == "__main__":
    create_rot_graph()
