#!/bin/bash


# testing individual files
echo ">> Running $meta_functionality_name (file mode)"
$meta_executable \
  --input "$resources_dir/raw/Sample2.raw" \
  --output "output2/Sample2.mzML" 2>&1 | \
  tee output2.txt

echo ">>> Checking contents of stdout"

if grep -q 'INFO Finished parsing.*Sample1' output2.txt; then
  echo Found content
  exit 1
fi
if ! grep -q 'INFO Finished parsing.*Sample2' output2.txt; then
  echo Could not find content
  exit 1
fi

echo ">>> Checking whether output files can be found"
[[ -f output2/Sample1.mzML ]] && echo "Sample1 found!" && exit 1
[[ ! -f output2/Sample2.mzML ]] && echo "Sample2 file could not be found!" && exit 1

echo ">> All test succeeded!"