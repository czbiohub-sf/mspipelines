#!/bin/bash

# testing whole directories
echo ">> Running MSDial (dir mode)"
./$meta_functionality_name \
  --input "$resources_dir/GCMS" \
  --output "output1" \
  --ri_index_file "$resources_dir/GCMS/FAMEs RT.txt" | \
  tee output1.txt

echo ">>> Checking contents of stdout"
if ! grep -q 'All processing finished' output1.txt; then
  echo Could not find content
  exit 1
fi

echo ">>> Checking whether output files can be found"
if ! ls output1/140428actsa25_* > /dev/null 2>&1; then echo "Output file 25 could not be found!"; exit 1; fi
if ! ls output1/140428actsa26_* > /dev/null 2>&1; then echo "Output file 26 could not be found!"; exit 1; fi
if ! ls output1/140428actsa27_* > /dev/null 2>&1; then echo "Output file 27 could not be found!"; exit 1; fi
if ! ls output1/AlignResult-* > /dev/null 2>&1; then echo "Output file alignresult could not be found!"; exit 1; fi
[[ ! -f output1/params.txt ]] && echo "Param file could not be found!" && exit 1
[[ ! -f output1/ri_index_paths.txt ]] && echo "RI Index file could not be found!" && exit 1


# testing individual files
echo ">> Running MSDial (file mode)"
./$meta_functionality_name \
  --input "$resources_dir/GCMS/140428actsa25_1.cdf" \
  --input "$resources_dir/GCMS/140428actsa27_1.cdf" \
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
[[ -f output2/ri_index_paths.txt ]] && echo "RI Index file found!" && exit 1

echo ">> All test succeeded!"