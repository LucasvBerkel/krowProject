import git
import time
import csv
from ast import literal_eval

source_file = "/data/rotten-tomatoes/rotten_tomatoes_reviews.csv"


def createHandEvaluatedData():
    git_repo = git.Repo(".", search_parent_directories=True)
    git_root = git_repo.git.rev_parse("--show-toplevel")

    idx = 0

    total_start_time = time.time()

    found_films = set()
    valid_reviews = []
    number_of_adjectives = 0
    current_idx = 0

    with open(git_root + source_file, 'r') as rottenTomatoesReviews:
        with open(git_root + "/evaluate/handEvaluated.tsv", 'r') as evalFile:
            for row in csv.DictReader(evalFile, delimiter='\t'):
                found_films.add(row['movieTitle'])
                valid_reviews.append(row['movieTitle'])
                if row['adjectives']:
                    number_of_adjectives += len(literal_eval(row['adjectives']))
                current_idx = row['idx']

        with open(git_root + "/evaluate/handEvaluated.tsv", 'a') as evalFile:

            reader = csv.DictReader(rottenTomatoesReviews, delimiter=',')

            writer = csv.DictWriter(evalFile, fieldnames=['idx', 'movieTitle', 'adjectives'], delimiter='\t')

            if not int(current_idx) > 0:
                writer.writeheader()

            try:
                for idx, row in enumerate(reader):
                    if idx <= int(current_idx):
                        continue

                    print(row['Review'])

                    movie_name = input("\nMovie? ")
                    if movie_name:
                        found_films.add(movie_name)
                        valid_reviews.append(movie_name)
                        row = {'movieTitle': movie_name,
                               'idx': idx,
                               'adjectives': []}
                        adjective = input("Adjective? ")
                        while adjective:
                            row['adjectives'] += [adjective]
                            adjective = input("Adjective? ")
                        number_of_adjectives += len(row['adjectives'])
                        writer.writerow(row)
            except KeyboardInterrupt:
                pass

    print("Analysed reviews: {}".format(idx))
    print("Found films: {}".format(len(found_films)))
    print("Number of reviews containing filmname: {}".format(len(valid_reviews)))
    print("Number of found adjectives in all reviews: {}".format(number_of_adjectives))

    elapsed_time = time.strftime("%H:%M:%S", time.gmtime(time.time() - total_start_time))
    print("Elapsed time: {}".format(elapsed_time))


if __name__ == "__main__":
    createHandEvaluatedData()
