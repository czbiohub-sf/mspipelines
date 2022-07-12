# mspipeline 0.3.1

## Breaking changes

* `msdial/msdial_gcms`: Now only accepts one or more input files. Directories are
  no longer accepted.

## Major changes

* `msdial/msdial_gcms`: Added support for setting the name, type, class_id, batch, analytical_order and inject_volume of input files.

## Minor changes

* `convert/thermo_to_mzml`: Revert being able to process input directories. Only allow
  processing individual input files.

## Bug fixes

* `maxquant/maxquant`: Fix refactoring error in script.

# mspipeline 0.3.0

Added components:

* `msdial/msdial_gcms`: Added MSDial GC/MS component.

Major changes:

* `maxquant/maxquant`: Refactored Bash script into a Python script.

* `maxquant/maxquant`: Added parameters to tweak the analysis.

Minor changes:

* `convert/thermo_to_mzml`: Allow also processing whole directories instead of 
  individual raw files.

* `convert/thermo_to_mzml`: Added unit test.


# mspipeline 0.2.0

Added components:

* `convert/thermo_to_mzml`: Convert a Thermo raw file to mzML.
* `qc/rawbeans`: Perform QC analysis on mzML file.

Major changes:

* Pipeline `maxquant`: Added `rawbeans` to pipeline.

# mspipeline 0.1.0

Initial release of mspipeline.

Added components:
 * `maxquant/maxquant`: Running a MaxQuant analysis with mostly default parameters.
 * `convert/maxquant_to_h5ad`: Converting a MaxQuant output folder to an AnnData file. 
 * `download/sync_resources_test`: Download testing resources from S3 to the `resources_test/` directory.

Nextflow workflows:
 * `maxquant`: Starting from Thermo Raw files, run MaxQuant and convert the outputs to AnnData.