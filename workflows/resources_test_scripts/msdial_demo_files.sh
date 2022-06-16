#!/bin/bash

# get the root of the directory
REPO_ROOT=$(git rev-parse --show-toplevel)

# ensure that the command below is run from the root of the repository
cd "$REPO_ROOT"

# settings
ID=msdial_demo_files
OUT="resources_test/$ID/"
DIR="$OUT"

# create tempdir
MY_TEMP="${VIASH_TEMP:-/tmp}"
TMPDIR=$(mktemp -d "$MY_TEMP/$ID-XXXXXX")
function clean_up {
  [[ -d "$TMPDIR" ]] && rm -r "$TMPDIR"
}
trap clean_up EXIT

# download zip file
raw_dir="$OUT/raw"
if [ ! -f "$raw_dir/MsdialConsoleApp.bat" ]; then
  wget http://prime.psc.riken.jp/compms/msdial/download/demo/MsdialConsoleApp%20demo%20files.zip -O "$TMPDIR/msdial_demo_files.zip"
  unzip "$TMPDIR/msdial_demo_files.zip" -d "$TMPDIR"
  mv "$TMPDIR/MsdialConsoleApp demo files/" "$raw_dir"
fi
