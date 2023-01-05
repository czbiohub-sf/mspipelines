#!/bin/bash

## VIASH START
par_input="resources_test/zenodo_4274987/raw/Sample1.raw"
par_output="output.mzML"
par_fasta="human.fasta"
par_conf="sample.param.txt"
## VIASH END

# create output directory if not exists
out_dir=`dirname "$par_output"`
[ -d "$out_dir" ] || mkdir -p "$out_dir"

# run msgf+
java -Xmx3500M -jar /msgf/MSGFPlus.jar -s $par_input -d $par_fasta -conf $par_conf -o $par_output