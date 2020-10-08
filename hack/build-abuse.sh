#!/usr/bin/bash

PODMAN=../bin/podman

iter=0
threads=${1:-10}
while true; do
    for (( i = 0; i < $threads; i++ )); do
        (
            CDir=$(mktemp -d -t build-XXXXXXXXXXXX)
            trap "{ rm -rf $CDir; }" EXIT

            echo -e "from alpine\nenv foo=\"${iter}_${i}\"" > ${CDir}/Containerfile

            id=$($PODMAN build -q -t "iter${iter}thread${i}" $CDir)
            if [[ $? != 0 ]]; then
                exit 1
            fi
            $PODMAN rmi --force $id
            exit 0
        ) &
    done
    if wait; then
        echo 1>&2 Build/Rmi failed on iteration $iter
        exit 2
    fi
   ((iter++))
done
