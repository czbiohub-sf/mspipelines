#!/bin/bash

./$meta_functionality_name \
  --input s3://czbiohub-pipelines/resources_test_ms \
  --output my_output \
  --dryrun > \
  output.txt

if ! grep -q '(dryrun) download: s3://czbiohub.*to.*raw' output.txt; then
  echo Could not find content
  exit 1
fi

echo Test succeeded!