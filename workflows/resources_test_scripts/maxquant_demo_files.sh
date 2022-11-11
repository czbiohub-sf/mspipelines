#!/bin/bash

# Get the root of the directory
REPO_ROOT=$(git rev-parse --show-toplevel)

# Ensure that the command below is run from the root of the repository
cd "$REPO_ROOT"

# Settings
ID="maxquant_11112022"
OUT="resources_test/$ID"
DIR="$OUT"

# Create tempdir
MY_TEMP="${VIASH_TEMP:-/tmp}"
TMPDIR=$(mktemp -d "$MY_TEMP/$ID-XXXXXX")
function clean_up {
  [[ -d "$TMPDIR" ]] && rm -r "$TMPDIR"
}
trap clean_up EXIT

# download bcl data
raw_dir="$OUT/raw"
if [ ! -f "$raw_dir/Sample.raw" ]; then
  mkdir -p "$raw_dir"
  tmp_fasta="$TMPDIR/tmp.fasta"

  wget https://ftp.pride.ebi.ac.uk/pride/data/archive/2014/04/PXD000561/Fetal_Testis_bRP_Elite_26_f20.raw -O "$raw_dir/Sample.raw"
  wget https://zenodo.org/record/4274987/files/Protein_database.fasta -O "$tmp_fasta"

# process the fasta (subsample first 1000) entries
 if [ -f "$raw_dir/reference.fasta" ] ; then
    rm "$raw_dir/reference.fasta"
 fi

i=0
while read -r line; do
if [[ "$line" =~ ^\>.*  ]]; then
    let i++
fi
if (($i < 1000)) then
    echo $line >> "$raw_dir/reference.fasta"
fi
done <$tmp_fasta 
rm $tmp_fasta

fi

maxquant_out="$OUT/maxquant_out"
if [ ! -f "$maxquant_out" ]; then
  mkdir -p "$maxquant_out" 
  target/docker/maxquant/maxquant/maxquant \
    --input "$raw_dir/Sample.raw" \
    --reference "$raw_dir/reference.fasta" \
    --output "$maxquant_out"
fi
