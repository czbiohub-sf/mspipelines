#!/bin/bash

echo ">> Running MSDial"
./$meta_functionality_name \
  --input "$resources_dir/GCMS" \
  --output "output" \
  --ri_index_file "$resources_dir/GCMS/FAMEs RT.txt" | \
  tee output.txt

echo ">> Checking contents of stdout"
if ! grep -q 'All processing finished' output.txt; then
  echo Could not find content
  exit 1
fi

echo ">> Checking whether output files can be found"
if ! ls output/AlignResult-* > /dev/null 2>&1; then echo "Output file could not be found!"; exit 1; fi
[[ ! -f output/params.txt ]] && echo "Param file could not be found!" && exit 1
[[ ! -f output/ri_index_paths.txt ]] && echo "RI Index file could not be found!" && exit 1

echo Test succeeded!