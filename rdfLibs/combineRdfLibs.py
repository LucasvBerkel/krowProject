import time

from rdflib import Graph

if __name__ == "__main__":
    start_time = time.time()
    total_start_time = time.time()

    g = Graph()

    print("Loading rottentomatoes...")
    g.parse("rottenTomatoesRdf.ttl", format="ttl")
    elapsed_time = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))
    print("Elapsed time: {}".format(elapsed_time))
    start_time = time.time()

    print("Loading imdb...")
    g.parse("imdbRdf.ttl", format="ttl")
    elapsed_time = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))
    print("Elapsed time: {}".format(elapsed_time))
    start_time = time.time()

    print("Loading dbpedia...")
    g.parse("dbpediaRdf.ttl", format="ttl")
    elapsed_time = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))
    print("Elapsed time: {}".format(elapsed_time))
    start_time = time.time()

    print("Serializing to tuplestore...")
    g.serialize(destination='tupleStore.ttl', format='turtle')
    elapsed_time = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))
    print("Elapsed time: {}".format(elapsed_time))

    elapsed_time = time.strftime("%H:%M:%S", time.gmtime(time.time() - total_start_time))
    print("Total elapsed time: {}\tNumber of tuples: {}".format(elapsed_time, len(g)))
