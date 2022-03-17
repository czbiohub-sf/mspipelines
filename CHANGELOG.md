# mspipeline 0.1.0

Initial commit of mspipeline 

Components:
 * `maxquant/maxquant`: Running a MaxQuant analysis with mostly default parameters.
 * `convert/maxquant_to_h5ad`: Converting a MaxQuant output folder to an AnnData file. 
 * `download/sync_resources_test`: Download testing resources from S3 to the `resources_test/` directory.

 Nextflow workflows:
 * `maxquant`: Starting from Thermo Raw files, run MaxQuant and convert the outputs to AnnData.