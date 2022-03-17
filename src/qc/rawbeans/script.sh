#!/bin/bash

## VIASH START
# par_input="resources_test/zenodo_4274987/raw/Sample1.raw:resources_test/zenodo_4274987/raw/Sample2.raw"
par_input="resources_test/zenodo_4274987/raw/Sample1.raw"
par_output="output/"
## VIASH END

if [ ! -d "$par_output" ]; then
   mkdir -p "$par_output"
fi

# todo: convert to mzML

create-qc-report.py --input "$par_input" --output-dir "$par_output"