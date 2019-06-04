import time
import git
import csv
from rdfLibs import rottenTomatoes

source_file = "/data/rotten-tomatoes/rotten_tomatoes_reviews.csv"

if __name__ == "__main__":
    print("Hello")

    # git_repo = git.Repo(".", search_parent_directories=True)
    # git_root = git_repo.git.rev_parse("--show-toplevel")
    #
    # only_movie_filter = {'policy': "whitelist",
    #                      'types': "DBpedia:Film"}
    #
    # total_start_time = time.time()
    #
    # with open(git_root + source_file, 'r') as rottenTomatoesReviews:
    #
    #     reader = csv.DictReader(rottenTomatoesReviews, delimiter=',')
    #
    #     found_films = set()
    #     start_time = time.time()
    #     for idx, row in enumerate(reader):
    #         if idx % 100000 == 0:
    #             elapsed_time = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))
    #             print("Idx: {}\tFound Movies: {}\tElapsed time: {}".format(idx, len(found_films), elapsed_time))
    #             start_time = time.time()
