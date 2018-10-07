for id in $(docker ps -a | awk '{print $1}') ; do docker rm $id ; done

