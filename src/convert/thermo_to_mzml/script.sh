#!/bin/bash

## VIASH START
par_input="resources_test/zenodo_4274987/raw/Sample1.raw"
par_output="output.hzML"
## VIASH END


# need to copy file because tool doesn't work with symlinks

# create tempdir
MY_TEMP="${VIASH_TEMP:-/tmp}"
TMPDIR=$(mktemp -d "$MY_TEMP/$meta_functionality_name-XXXXXX")
function clean_up {
  [[ -d "$TMPDIR" ]] && rm -r "$TMPDIR"
}
trap clean_up EXIT

tmp_input="$TMPDIR/`basename "$par_input"`"
cp "$par_input" "$tmp_input"

mono /var/local/thermorawfileparser/ThermoRawFileParser.exe "-i=$tmp_input" "-b=$par_output"

# mono /var/local/thermorawfileparser/ThermoRawFileParser.exe "-i=$par_input" "-b=$par_output"