#!/bin/bash

# get the root of the directory
REPO_ROOT=$(git rev-parse --show-toplevel)

# ensure that the command below is run from the root of the repository
cd "$REPO_ROOT"

# settings
ID=zenodo_4274987
OUT="resources_test/$ID/"
DIR="$OUT"
S3DIR="s3://czbiohub-pipelines/resources_test_ms/$DIR"

# create tempdir
MY_TEMP="${VIASH_TEMP:-/tmp}"
TMPDIR=$(mktemp -d "$MY_TEMP/$ID-XXXXXX")
function clean_up {
  [[ -d "$TMPDIR" ]] && rm -r "$TMPDIR"
}
trap clean_up EXIT

# download bcl data
raw_dir="$OUT/raw"
if [ ! -f "$raw_dir/Sample1.raw" ]; then
  mkdir -p "$raw_dir"
  
  wget https://zenodo.org/record/4274987/files/Protein_database.fasta -O "$raw_dir/reference.fasta"
  wget https://zenodo.org/record/4274987/files/Sample1.raw -O "$raw_dir/Sample1.raw"
  wget https://zenodo.org/record/4274987/files/Sample2.raw -O "$raw_dir/Sample2.raw"
fi

maxquant_out="$OUT/maxquant_out"
if [ ! -f "$maxquant_out" ]; then
  mkdir -p "$maxquant_out"

  target/docker/maxquant/maxquant/maxquant \
    --input "$raw_dir/Sample1.raw" \
    --input "$raw_dir/Sample2.raw" \
    --reference "$raw_dir/reference.fasta" \
    --output "$maxquant_out"
fi

h5ad_file="${OUT}/zenodo_4274987.h5ad"
if [ ! -f "$h5ad_file" ]; then

  target/docker/convert/maxquant_to_h5ad/maxquant_to_h5ad \
    --input "$maxquant_out" \
    --output "$h5ad_file"
fi

# aws s3 sync --profile czb "$DIR" "$S3DIR"
