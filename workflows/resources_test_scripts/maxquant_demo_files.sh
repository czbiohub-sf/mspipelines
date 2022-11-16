#!/bin/bash

# Get the root of the directory
REPO_ROOT=$(git rev-parse --show-toplevel)

# Ensure that the command below is run from the root of the repository
cd "$REPO_ROOT"

# Settings
ID="maxquant_demo_files"
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
  echo "Preparing sample RAW file..."
  mkdir -p "$raw_dir"
  wget https://ftp.pride.ebi.ac.uk/pride/data/archive/2014/04/PXD000561/Fetal_Testis_bRP_Elite_26_f20.raw -O "$raw_dir/Sample.raw"
fi

if [ ! -f "$raw_dir/reference.fasta" ] ; then
  echo "Preparing sample FASTA file..."
  tmp_fasta="$TMPDIR/tmp.fasta"
  wget https://zenodo.org/record/4274987/files/Protein_database.fasta -O "$tmp_fasta"

  if ! command -v seqkit &> /dev/null; then
    echo "This script requires seqkit. Please make sure the binary is added to your PATH."
  # process the fasta (subsample first 1000) entries TODO keep this as a plan B strat in case the binaries are missing?
  # i=0
  # while read -r line; do
  #   if [[ "$line" =~ ^\>.*  ]]; then
  #     let i++
  #   fi
  #   if (($i < 1000)); then
  #     echo $line >> "$raw_dir/reference.fasta"
  #   fi
  # done <$tmp_fasta 
    exit 1
  fi
  seqkit head -n 1000 $tmp_fasta -o "$raw_dir/reference.fasta"
  rm $tmp_fasta
fi