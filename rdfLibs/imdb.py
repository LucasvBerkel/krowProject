import git
import csv
import time

import urllib.parse

from rdflib import URIRef, Graph, Literal, Namespace
from rdflib.namespace import RDF, FOAF, OWL


source_file_titles = "/data/imdb_short/title.basics_short.tsv"
source_file_crew = "/data/imdb_short/title.crew_short.tsv"
source_file_principals = "/data/imdb_short/title.principals_short.tsv"
source_file_names = "/data/imdb_short/name.basics_short.tsv"


if __name__ == "__main__":

    git_repo = git.Repo(".", search_parent_directories=True)
    git_root = git_repo.git.rev_parse("--show-toplevel")

    local = Namespace("localhost:movieCastingNamespace/")
    dbpedia = Namespace("http://dbpedia.org/resource/")

    g = Graph()

    g.parse(git_root + "/rdfLibs/rottenTomatoesRdf.ttl", format="ttl")

    rot_films = set()
    rot_films_uri_dict = dict()
    found_films = set()
    found_persons = set()

    for rot_films_uri, p, film in g.triples((None, local.hasSurfaceForm, None)):
        rot_films.add(str(film).lower())
        rot_films_uri_dict[str(film).lower()] = rot_films_uri
    print("Films in rot dataset: {}".format(len(rot_films)))

    g = Graph()

    total_start_time = time.time()

    with open(git_root + source_file_titles, 'r') as imdbTitles:
        reader = csv.DictReader(imdbTitles, delimiter='\t')

        start_time = time.time()
        print("Starting converting imdb_titles")
        try:
            for idx, row in enumerate(reader):
                if idx % 100000 == 0:
                    elapsed_time = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))
                    print("Idx: {}\tFound Movies: {}\tElapsed time: {}".format(idx, len(found_films), elapsed_time))
                    start_time = time.time()
                if row['primaryTitle'].lower() in rot_films:
                    rot_films.remove(row['primaryTitle'].lower())

                    rot_films_uri = rot_films_uri_dict[row['primaryTitle'].lower()]
                    del rot_films_uri_dict[row['primaryTitle'].lower()]
                    found_films.add(row['tconst'])

                    title = row['primaryTitle'].title()

                    temp_film = URIRef(local + urllib.parse.quote(row['tconst']))
                    g.add((temp_film, OWL.sameAs, URIRef(rot_films_uri)))
                    g.add((temp_film, local.hasPrimaryName, Literal(title)))
                    g.add((temp_film, local.producedInYear, Literal(row['startYear'])))

                    for genre in row['genres'].split(","):
                        g.add((temp_film, local.hasGenre, Literal(genre)))
        except KeyboardInterrupt:
            pass
    print("Length found films: {}".format(len(found_films)))

    with open(git_root + source_file_crew, 'r') as imdbCrew:
        reader = csv.DictReader(imdbCrew, delimiter='\t')

        start_time = time.time()
        print("Starting converting imdb_crew")
        try:
            for idx, row in enumerate(reader):
                if idx % 100000 == 0:
                    elapsed_time = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))
                    print("Idx: {}\tElapsed time: {}".format(idx, elapsed_time))
                    start_time = time.time()
                if row['tconst'] in found_films:
                    temp_film = URIRef(local + urllib.parse.quote(row['tconst']))
                    if row['directors']:
                        for director in row['directors'].split(","):
                            if director == "\\N":
                                continue
                            temp_person = URIRef(local + urllib.parse.quote(director))
                            g.add((temp_film, local.directedBy, temp_person))
                            found_persons.add(director)
                    if row['writers']:
                        for writer in row['writers'].split(","):
                            if writer == "\\N":
                                continue
                            temp_person = URIRef(local + urllib.parse.quote(writer))
                            g.add((temp_film, local.writtenBy, temp_person))
                            found_persons.add(writer)
        except KeyboardInterrupt:
            pass

    with open(git_root + source_file_principals, 'r') as imdbPrincipals:
        reader = csv.DictReader(imdbPrincipals, delimiter='\t')

        start_time = time.time()
        print("Starting converting imdb_principles")
        try:
            for idx, row in enumerate(reader):
                if idx % 100000 == 0:
                    elapsed_time = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))
                    print("Idx: {}\tElapsed time: {}".format(idx, elapsed_time))
                    start_time = time.time()

                if row['tconst'] in found_films:
                    temp_film = URIRef(local + urllib.parse.quote(row['tconst']))
                    temp_person = URIRef(local + urllib.parse.quote(row['nconst']))
                    g.add((temp_film, local.actingPerfomedBy, temp_person))
                    found_persons.add(row['nconst'])
        except KeyboardInterrupt:
            pass

    with open(git_root + source_file_names, 'r') as imdbNames:
        reader = csv.DictReader(imdbNames, delimiter='\t')

        start_time = time.time()
        print("Starting converting imdb names")
        try:
            for idx, row in enumerate(reader):
                if idx % 100000 == 0:
                    elapsed_time = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))
                    print("Idx: {}\tElapsed time: {}".format(idx, elapsed_time))
                    start_time = time.time()
                if row['nconst'] in found_persons:
                    temp_person = URIRef(local + urllib.parse.quote(row['nconst']))
                    g.add((temp_person, RDF.type, FOAF.Person))
                    g.add((temp_person, FOAF.name, Literal(row['primaryName'])))
        except KeyboardInterrupt:
            pass

    g.serialize(destination=git_root + '/rdfLibs/imdbRdf.ttl', format='turtle')

    elapsed_time = time.strftime("%H:%M:%S", time.gmtime(time.time() - total_start_time))
    print("Elapsed time: {}".format(elapsed_time))
