#!/bin/bash

## VIASH START
par_input="resources_test/zenodo_4274987/raw/Sample1.raw"
par_output="output.mzML"
## VIASH END

# need to copy file because tool doesn't work with symlinks

# create tempdir
MY_TEMP="${VIASH_TEMP:-/tmp}"
TMPDIR=$(mktemp -d "$MY_TEMP/$meta_functionality_name-XXXXXX")
function clean_up {
  [[ -d "$TMPDIR" ]] && rm -r "$TMPDIR"
}
trap clean_up EXIT

# copy input files to tempdir
cp "$par_input" "$TMPDIR"
new_input="$TMPDIR/"$(basename "$par_input")

# create output directory if not exists
out_dir=`dirname "$par_output"`
[ -d "$out_dir" ] || mkdir -p "$out_dir"

# run converter
mono /var/local/thermorawfileparser/ThermoRawFileParser.exe "-i=$new_input" "-b=$par_output"