#!/bin/bash

echo "This script is not meant to be run! Run the commands separately, please." && exit 1

TAG=0.1.0


rm -r target
git fetch origin
git merge origin/main

# build target folder and docker containers
bin/viash_build -m release -t $TAG --max_threads 10

# run unit tests (when done right, these should all pass)
bin/viash_test -m release -t $TAG

# push docker containers to docker hub
bin/viash_push -m release -t $TAG --max_threads 10

# commit current code to release branch
git add target
git commit -m "Release $TAG"
git push 

# create new tag
git tag -a "$TAG" -m "Release $TAG"
git push --tags
