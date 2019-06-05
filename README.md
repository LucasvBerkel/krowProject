Product repostitory of the construction of a movie casting triplestore and research to structuring raw text data to rdf triples

Run 'make docker-image' to start docker image, might be necessary to load files in triplestore/ manually to start the sparql queries
This starts a docker localhost on port 8890, where you can log in with username:password dba:dba. Navigate to Linked-Data -> Quad Store Upload to upload the triplefiles. Perform sparql queries in Linked-Data -> SPARQL.
 

/data contains the raw datafiles

/demo contains files for the given demopresentation

/docker contains sample files of initiating a custom docker image --> deprecated

/evaluate contains the scripts used to evaluate the unstructured data -> triple part of the system

/paperReport contains files for the given paperreport presentation

/proposal contains files for the written project proposal

/rdfLibs contains the scripts and separate triple instances used to construct the entire triplestore instances from the raw datafiles

/triplestore, here the triplestore files (the instances and the ontology) can be found

/sampleQueries shows examples of tested and performed queries
