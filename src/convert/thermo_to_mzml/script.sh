#!/bin/bash

## VIASH START
par_input="resources_test/zenodo_4274987/raw/Sample1.raw"
par_output="output.hzML"
## VIASH END

mono /var/local/thermorawfileparser/ThermoRawFileParser.exe "-i=$par_input" "-b=$par_output"