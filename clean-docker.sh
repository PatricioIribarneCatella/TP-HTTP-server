for id in $(docker ps -a | awk '{print $1}') ; do docker rm -v $id ; done

