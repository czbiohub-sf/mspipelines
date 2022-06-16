#!/bin/bash

aws s3 sync --profile czb "resources_test" "s3://czbiohub-pipelines/resources_test_ms" --delete --dryrun