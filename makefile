docker-image:
#		docker inspect -f '{{.State.Running}}' moviedb
		docker stop moviedb
		docker run --name moviedb --rm -p 8890:8890 -p 1111:1111 -e DBA_PASSWORD=dba -v /var/lib/virtuoso-opensource-6.1/db/toLoad/:/data -d tenforce/virtuoso
