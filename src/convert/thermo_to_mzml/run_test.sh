#!/bin/bash

# testing whole directories
echo ">> Running $meta_functionality_name (dir mode)"
./$meta_functionality_name \
  --input "$resources_dir/raw" \
  --output "output1" | \
  tee output1.txt

echo ">>> Checking contents of stdout"
if ! grep -q 'INFO Finished parsing.*Sample1' output1.txt; then
  echo Could not find content
  exit 1
fi
if ! grep -q 'INFO Finished parsing.*Sample2' output1.txt; then
  echo Could not find content
  exit 1
fi

echo ">>> Checking whether output files can be found"
[[ ! -f output1/Sample1.mzML ]] && echo "Sample1 file could not be found!" && exit 1
[[ ! -f output1/Sample2.mzML ]] && echo "Sample2 file could not be found!" && exit 1


# testing individual files
echo ">> Running $meta_functionality_name (file mode)"
./$meta_functionality_name \
  --input "$resources_dir/raw/Sample2.raw" \
  --output "output2/Sample2.mzML" | \
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



# testing individual files
echo ">> Running $meta_functionality_name (file mode 2)"
./$meta_functionality_name \
  --input "$resources_dir/raw/Sample1.raw" \
  --output "output3/" | \
  tee output3.txt

echo ">>> Checking contents of stdout"
if ! grep -q 'INFO Finished parsing.*Sample1' output3.txt; then
  echo Cound not find content
  exit 1
fi
if grep -q 'INFO Finished parsing.*Sample2' output3.txt; then
  echo Found content
  exit 1
fi

echo ">>> Checking whether output files can be found"
[[ ! -f output3/Sample1.mzML ]] && echo "Sample1 file could not be found!" && exit 1
[[ -f output3/Sample2.mzML ]] && echo "Sample2 file found!" && exit 1


echo ">> All test succeeded!"