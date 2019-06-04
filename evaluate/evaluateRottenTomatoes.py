import time
import spotlight
import requests
import git
import csv

from nltk.corpus import wordnet as wn


source_file = "/data/rotten-tomatoes/rotten_tomatoes_reviews.csv"


def analyse_line(line_of_text):
    only_movie_filter = {'policy': "whitelist",
                         'types': "DBpedia:Film"}

    info = {}

    try:
        annotations = spotlight.annotate('http://localhost:2222/rest/annotate',
                                         line_of_text,
                                         confidence=0.4,
                                         support=20,
                                         filters=only_movie_filter,
                                         spotter='Default')

        for annotation in annotations[:1]:
            title = annotation['surfaceForm'].title()

            info['title'] = title
            info['URI'] = annotation['URI']

            info['adjectives'] = []

            # Abstract adjectives from review
            local_split_sentence = line_of_text.split()
            for word in local_split_sentence:
                for tmp in wn.synsets(word):
                    if tmp.pos() == "a":
                        info['adjectives'].append(word.title())
                    break
    except KeyboardInterrupt:
        raise KeyboardInterrupt
    except spotlight.SpotlightException or requests.exceptions.HTTPError:
        pass
    except BaseException:
        pass
    return info


def analyse_all_reviews():
    git_repo = git.Repo(".", search_parent_directories=True)
    git_root = git_repo.git.rev_parse("--show-toplevel")

    idx = 0

    total_start_time = time.time()

    with open(git_root + source_file, 'r') as rottenTomatoesReviews:

        reader = csv.DictReader(rottenTomatoesReviews, delimiter=',')

        found_films = set()
        valid_reviews = []
        number_of_adjectives = 0
        start_time = time.time()
        try:
            for idx, row in enumerate(reader):
                if idx % 100000 == 0:
                    elapsed_time = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))
                    print("Idx: {}\tFound Movies: {}\tElapsed time: {}".format(idx, len(found_films), elapsed_time))
                    start_time = time.time()

                found_info = analyse_line(row['Review'])

                if found_info:
                    found_films.add(found_info['URI'])
                    valid_reviews.append(found_info)
                    number_of_adjectives += len(found_info['adjectives'])
        except KeyboardInterrupt:
            pass

        print("Analysed reviews: {}".format(idx))
        print("Found films: {}".format(len(found_films)))
        print("Number of reviews containing filmname: {}".format(len(valid_reviews)))
        print("Number of found adjectives in all reviews: {}".format(number_of_adjectives))

        elapsed_time = time.strftime("%H:%M:%S", time.gmtime(time.time() - total_start_time))
        print("Elapsed time: {}".format(elapsed_time))


def analyse_handanalysed_data():
    git_repo = git.Repo(".", search_parent_directories=True)
    git_root = git_repo.git.rev_parse("--show-toplevel")

    idx = 0

    total_start_time = time.time()

    with open(git_root + source_file, 'r') as rottenTomatoesReviews:

        reader = csv.DictReader(rottenTomatoesReviews, delimiter=',')

        found_films = set()
        valid_reviews = []
        number_of_adjectives = 0
        start_time = time.time()
        try:
            for idx, row in enumerate(reader):
                if idx % 100000 == 0:
                    elapsed_time = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))
                    print("Idx: {}\tFound Movies: {}\tElapsed time: {}".format(idx, len(found_films), elapsed_time))
                    start_time = time.time()

                found_info = analyse_line(row['Review'])

                if found_info:
                    found_films.add(found_info['URI'])
                    valid_reviews.append(found_info)
                    number_of_adjectives += len(found_info['adjectives'])

        except KeyboardInterrupt:
            pass

        print("Analysed reviews: {}".format(idx))
        print("Found films: {}".format(len(found_films)))
        print("Number of reviews containing filmname: {}".format(len(valid_reviews)))
        print("Number of found adjectives in all reviews: {}".format(number_of_adjectives))

        elapsed_time = time.strftime("%H:%M:%S", time.gmtime(time.time() - total_start_time))
        print("Elapsed time: {}".format(elapsed_time))


if __name__ == "__main__":
    analyse_all_reviews()
