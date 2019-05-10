import git
import csv
import time

import urllib.parse

from rdflib import URIRef, Graph, Literal, Namespace
from rdflib.namespace import RDF, FOAF


source_file_titles = "/data/imdb_short/title.basics_short.tsv"
source_file_crew = "/data/imdb_short/title.crew_short.tsv"
source_file_principals = "/data/imdb_short/title.principals_short.tsv"
source_file_names = "/data/imdb_short/name.basics_short.tsv"


if __name__ == "__main__":

    git_repo = git.Repo(".", search_parent_directories=True)
    git_root = git_repo.git.rev_parse("--show-toplevel")

    local = Namespace("localhost:imdb/")
    dbpedia = Namespace("http://dbpedia.org/resource/")

    g = Graph()

    g.parse("rottenTomatoesRdf.ttl", format="ttl")

    rot_films = set()
    found_films = set()
    found_persons = set()

    for s, p, film in g.triples((None, FOAF.name, None)):
        rot_films.add(str(film).lower())
    print("Films in rot dataset: {}".format(len(rot_films)))

    g = Graph()

    with open(git_root + source_file_titles, 'r') as imdbTitles:
        reader = csv.DictReader(imdbTitles, delimiter='\t')

        start_time = time.time()
        print("Starting converting imdb_titles")
        for idx, row in enumerate(reader):
            if idx % 100000 == 0:
                elapsed_time = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))
                print("Idx: {}\tFound Movies: {}\tElapsed time: {}".format(idx, len(found_films), elapsed_time))
                start_time = time.time()

            try:
                if row['primaryTitle'].lower() in rot_films:
                    rot_films.remove(row['primaryTitle'].lower())

                    found_films.add(row['tconst'])
                    title = row['primaryTitle'].title()

                    temp = URIRef(local + urllib.parse.quote(row['tconst']))
                    g.add((temp, RDF.type, dbpedia.film))
                    g.add((temp, FOAF.name, Literal(title)))
            except KeyboardInterrupt:
                break
    print("Length found films: {}".format(len(found_films)))

    with open(git_root + source_file_crew, 'r') as imdbCrew:
        reader = csv.DictReader(imdbCrew, delimiter='\t')

        start_time = time.time()
        print("Starting converting imdb_crew")
        for idx, row in enumerate(reader):
            if idx % 100000 == 0:
                elapsed_time = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))
                print("Idx: {}\tElapsed time: {}".format(idx, elapsed_time))
                start_time = time.time()
            try:
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
                break

    with open(git_root + source_file_principals, 'r') as imdbPrincipals:
        reader = csv.DictReader(imdbPrincipals, delimiter='\t')

        start_time = time.time()
        print("Starting converting imdb_principles")
        for idx, row in enumerate(reader):
            if idx % 100000 == 0:
                elapsed_time = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))
                print("Idx: {}\tElapsed time: {}".format(idx, elapsed_time))
                start_time = time.time()

            try:
                if row['tconst'] in found_films:
                    temp_film = URIRef(local + urllib.parse.quote(row['tconst']))
                    temp_person = URIRef(local + urllib.parse.quote(row['nconst']))
                    g.add((temp_film, local.actingPerfomedBy, temp_person))
                    found_persons.add(row['nconst'])
            except KeyboardInterrupt:
                break

    with open(git_root + source_file_names, 'r') as imdbNames:
        reader = csv.DictReader(imdbNames, delimiter='\t')

        start_time = time.time()
        print("Starting converting imdb names")
        for idx, row in enumerate(reader):
            if idx % 100000 == 0:
                elapsed_time = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))
                print("Idx: {}\tElapsed time: {}".format(idx, elapsed_time))
                start_time = time.time()

            try:
                if row['nconst'] in found_persons:
                    temp_person = URIRef(local + urllib.parse.quote(row['nconst']))
                    g.add((temp_person, FOAF.name, Literal(row['primaryName'])))
            except KeyboardInterrupt:
                break

    g.serialize(destination='imdbRdf.ttl', format='turtle')
