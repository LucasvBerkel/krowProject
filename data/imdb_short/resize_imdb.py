import csv


movieTitles = set()
persons = set()


print("Abstracting movies...")
with open('../imdb/title.basics.tsv', 'r') as tsvfileR:
    with open('./title.basics_short.tsv', 'w') as tsvfileW:
        reader = csv.DictReader(tsvfileR, delimiter='\t')
        tsv_writer = csv.DictWriter(tsvfileW, fieldnames=reader.fieldnames, delimiter='\t')

        tsv_writer.writeheader()
        for row in reader:
            if row['titleType'] == 'movie':
                tsv_writer.writerow(row)
                movieTitles.add(row['tconst'])


print("Abstracting crew...")
with open('../imdb/title.crew.tsv') as tsvfile:
    with open('./title.crew_short.tsv', 'w') as tsvfileW:
        reader = csv.DictReader(tsvfile, delimiter='\t')
        tsv_writer = csv.DictWriter(tsvfileW, fieldnames=reader.fieldnames, delimiter='\t')

        tsv_writer.writeheader()
        for row in reader:
            if row['tconst'] in movieTitles:
                tsv_writer.writerow(row)
                for director in row['directors']:
                    persons.add(director)
                for writer in row['writers']:
                    persons.add(writer)


print("Abstracting principles...")
with open('../imdb/title.principals.tsv') as tsvfile:
    with open('./title.principals_short.tsv', 'w') as tsvfileW:
        reader = csv.DictReader(tsvfile, delimiter='\t')
        tsv_writer = csv.DictWriter(tsvfileW, fieldnames=reader.fieldnames, delimiter='\t')

        tsv_writer.writeheader()
        for row in reader:
            if row['tconst'] in movieTitles and (row['category'] == 'actor' or row['category'] == 'actress'):
                tsv_writer.writerow(row)
                persons.add(row['nconst'])


print("Abstracting name info...")
with open('../imdb/name.basics.tsv') as tsvfile:
    with open('./name.basics_short.tsv', 'w') as tsvfileW:
        reader = csv.DictReader(tsvfile, delimiter='\t')
        tsv_writer = csv.DictWriter(tsvfileW, fieldnames=reader.fieldnames, delimiter='\t')

        tsv_writer.writeheader()
        for row in reader:
            if row['nconst'] in persons:
                tsv_writer.writerow(row)
