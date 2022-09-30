#!/bin/bash

# testing individual files
echo ">> Running MSDial"
$meta_executable \
  --input "$meta_resources_dir/GCMS/140428actsa25_1.cdf" \
  --input "$meta_resources_dir/GCMS/140428actsa27_1.cdf" \
  --class_id foo \
  --class_id bar \
  --ri_index_file "$meta_resources_dir/GCMS/FAMEs RT.txt" \
  --output "output2" | \
  tee output2.txt

echo ">>> Checking contents of stdout"
if ! grep -q 'All processing finished' output2.txt; then
  echo Could not find content
  exit 1
fi

echo ">>> Checking whether output files can be found"
if ! ls output2/140428actsa25_* > /dev/null 2>&1; then echo "Output file 25 could not be found!"; exit 1; fi
if ls output2/140428actsa26_* > /dev/null 2>&1; then echo "Output file 26 found!"; exit 1; fi
if ! ls output2/140428actsa27_* > /dev/null 2>&1; then echo "Output file 27 could not be found!"; exit 1; fi
if ! ls output2/AlignResult-* > /dev/null 2>&1; then echo "Output file alignresult could not be found!"; exit 1; fi
[[ ! -f output2/params.txt ]] && echo "Param file could not be found!" && exit 1
[[ ! -f output2/ri_index_paths.txt ]] && echo "RI Index file could not be found!" && exit 1

echo ">> All test succeeded!"