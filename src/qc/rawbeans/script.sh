#!/bin/bash

## VIASH START
par_input="output/run_0/run_0.thermo_to_mzml.output.mzML:output/run_1/run_1.thermo_to_mzml.output.mzML"
par_output="output/rawbeans/"
## VIASH END

command_builder=()

# process inputs
command_builder+=( "--input" )
IFS=:
set -f
for val in $par_input; do
   unset IFS
   command_builder+=("$val")
done
set +f

# process batch
if [ "$par_batch" == "true" ]; then 
  command_builder+=( "--batch" )
fi

# process no_report
if [ "$par_no_report" == "true" ]; then 
  command_builder+=( "--no-report" )
fi

# process mass
if [ ! -z "$par_mass" ]; then
   command_builder+=( "--masses" )
   IFS=:
   set -f
   for val in $par_mass; do
      unset IFS
      command_builder+=("$val")
   done
   set +f
fi

# process output
command_builder+=( "--output-dir" "$par_output" )

if [ ! -d "$par_output" ]; then
   mkdir -p "$par_output"
fi

create-qc-report.py "${command_builder[@]}"