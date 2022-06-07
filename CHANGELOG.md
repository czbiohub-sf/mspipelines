# mspipeline 0.3.0

Minor changes:

* `convert/thermo_to_mzml`: Allow also processing whole directories instead of 
  individual raw files.


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