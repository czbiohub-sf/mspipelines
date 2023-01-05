#!/bin/bash

# Get the root of the directory
REPO_ROOT=$(git rev-parse --show-toplevel)

# Ensure that the command below is run from the root of the repository
cd "$REPO_ROOT"

# Settings
ID="msgf_demo_files"
OUT="resources_test/$ID"

# Create tempdir
MY_TEMP="${VIASH_TEMP:-/tmp}"
TMPDIR=$(mktemp -d "$MY_TEMP/$ID-XXXXXX")
function clean_up {
  [[ -d "$TMPDIR" ]] && rm -r "$TMPDIR"
}
trap clean_up EXIT

mkdir -p $OUT
#download spectra
echo "Verifying input spectra file..."
if [ ! -f "$OUT/sample.mzml" ]; then
  echo "Preparing sample mzml file..."
  #TODO find a proper example
  wget https://ftp.pride.ebi.ac.uk/pride/data/archive/2021/03/PXD017345/StS-Pili-wt-5-ISF80-20072015.mzML -O "$OUT/sample.mzML"
fi

#download fasta
echo "Verifying input fasta file..."
#if [ ! -f "$raw_dir/reference.fasta" ] ; then
  echo "Preparing sample FASTA file..."
  tmp_fasta="$TMPDIR/tmp.fasta"
  wget https://zenodo.org/record/4274987/files/Protein_database.fasta -O $tmp_fasta

  if ! command -v seqkit &> /dev/null; then
    echo "This script requires seqkit. Please make sure the binary is added to your PATH."
    echo "Defaulting to native strategy, please revise ASAP"
  # process the fasta (subsample first 1000) entries TODO keep this as a plan B strat in case the binaries are missing?
    i=0
    while read -r line; do
      if [[ "$line" =~ ^\>.*  ]]; then
        let i++
      fi
      if (($i < 1000)); then
        echo $line >> "$OUT/reference.fasta"
      fi
    done <$tmp_fasta 
  else
    seqkit head -n 1000 $tmp_fasta -o "$OUT/reference.fasta"
  fi

  rm $tmp_fasta

#fi

#download msgf example parameter
echo "Verifying input parameters file..."
if [ ! -f "$OUT/param.txt" ] ; then
  echo "Preparing sample parameter file..."
  wget  https://raw.githubusercontent.com/MSGFPlus/msgfplus/master/docs/ParameterFiles/MSGFPlus_Tryp_MetOx_15ppmParTol.txt -O "$OUT/param.txt"
fi

