nextflow.enable.dsl=2

workflowDir = params.rootDir + "/workflows"
targetDir = params.rootDir + "/target/nextflow"

include { maxquant } from targetDir + "/maxquant/maxquant/main.nf" params(params)
include { maxquant_to_h5ad } from targetDir + "/convert/maxquant_to_h5ad/main.nf" params(params)
include { thermo_to_mzml } from targetDir + "/convert/thermo_to_mzml/main.nf" params(params)
include { rawbeans } from targetDir + "/qc/rawbeans/main.nf" params(params)
include { overrideOptionValue; has_param; check_required_param } from workflowDir + "/utils/utils.nf" params(params)

/*
MaxQuant Processing - CLI workflow

A workflow for running the default MaxQuant processing components.

Arguments:
  --id:                           an event id (optional)
  --input:                        one or more raw files (required)
  --reference:                    a reference fasta file (required)
  --csv                           above parameters can also be passed as a .csv file.
*/
workflow {
  if (has_param("help")) {
    log.info """MaxQuant Processing - CLI workflow

A workflow for running the default MaxQuant processing components.

Arguments:
  --id:                           an event id (optional)
  --input:                        one or more raw files (required)
  --reference:                    a reference fasta file (required)
  --csv                           above parameters can also be passed as a .csv file."""
    exit 0
  }

  if (has_param("input") == has_param("csv")) {
    exit 1, "ERROR: Please provide either an --input parameter or a --csv parameter"
  }
  
  check_required_param("publishDir", "where output files will be published")

  def multirun = has_param("csv")
  if (multirun) {
    input_ch = Channel.fromPath(params.csv)
      | splitCsv(header: true, sep: ",")
  } else {
    input_ch = Channel.value( params.subMap(["input", "reference"]) )
  }

  input_ch
    | map { li ->
      // process input
      if (li.containsKey("input") && li.input) {
        input_path = li.input.split(";").collect { path -> file(path) }.flatten()
      } else {
        exit 1, multirun ? 
          "ERROR: The provided csv file should contain an 'input' column" : 
          "ERROR: Please specify an '--input' parameter pointing to the raw files. Example: '--input raw_files/*.raw'"
      }

      // process reference
      if (li.containsKey("reference") && li.reference) {
        reference_path = file(li.reference)
      } else if (params.containsKey("reference") && params.reference) {
        reference_path = file(params.reference)
      } else {
        exit 1, multirun ? 
          "ERROR: The provided csv file should contain a 'reference' column, or alternatively a '--reference' parameter should be specified." : 
          "ERROR: Please specify an '--reference' parameter pointing to the reference. Example: '--input raw_files/reference.fa'"
      }
      // process id
      if (li.containsKey("id") && li.id) {
        id_value = li.id
      } else if (!multirun) {
        id_value = "run"
      } else {
        exit 1, "ERROR: The provided csv file should contain an 'id' column per run"
      }
      [ id_value, [ input: input_path, reference: reference_path ], params ]
    }
    | view { "before maxquant: [${it[0]}, ${it[1]}, params]" }
    | run_wf
    | view { "after maxquant: ${it[0]} - ${it[1]}" }
}

/*
MaxQuant Processing - Common workflow

A workflow for running the default MaxQuant processing components.

input channel event format: [ id, data, params ]
  value id:                      an event id
  map data:
    value input:                 one or more raw files (required)
    value reference:             a reference fasta file (required)
  value params:                    
output channel event format: [ id, data, params ]
  value id:                      same as input
  map data:
    value raw:                   raw data
    value mzml:                  raw data as an mzml
    value maxquant:              maxquant output directory
    value rawbeans:              rawbeans output directory
    value h5ad:                  maxquant output as an h5ad file
  value params:                  same as input params
*/
workflow run_wf {
  take:
  input_ch

  main:
  mzml_out = input_ch 
    | flatMap{ it -> it[1].input.withIndex().collect{in, ix -> [ it[0] + "_" + ix, in, it[2] ]}}
    | thermo_to_mzml 
    | map { it -> [ it[0].replaceFirst(/_[0-9]+$/, ""), it[1] ] }
    | groupTuple()
    | map { it -> [ it[0], it[1], params ]}
  maxquant_out = input_ch | maxquant
  rawbeans_out = mzml_out | rawbeans
  h5ad_out = maxquant_out | maxquant_to_h5ad

  output_ch = input_ch | map { it -> [ it[0], [ raw: it[1] ], it[2] ] }
    | join(mzml_out | map { it -> [ it[0], [ mzml: it[1] ] ] }, remainder: true)
    | join(maxquant_out | map { it -> [ it[0], [ maxquant: it[1] ] ] }, remainder: true)
    | join(rawbeans_out | map { it -> [ it[0], [ rawbeans: it[1] ] ] }, remainder: true)
    | join(h5ad_out | map { it -> [ it[0], [ h5ad: it[1] ] ] }, remainder: true)
    | map { id, raw, params, mzml, maxquant, rawbeans, h5ad -> [id, raw + mzml + maxquant + rawbeans + h5ad, params] }

  emit:
  output_ch
}


/*
TX Processing - Integration testing

A workflow for running the default RNA processing components.
*/
/*workflow test_wf {
  
  output_ch =
    Channel.value(
      [
        "foo",
        file(params.rootDir + "/resources_test/pbmc_1k_protein_v3/pbmc_1k_protein_v3_filtered_feature_bc_matrix.h5mu"),
        params
      ]
    )
    | view { "Input: [${it[0]}, ${it[1]}, params]" }
    | run_wf
    | view { output ->
      assert output.size() == 3 : "outputs should contain three elements; [id, file, params]"
      assert output[1].toString().endsWith(".h5mu") : "Output file should be a h5mu file. Found: ${output_list[0][1]}"
      "Output: [${output[0]}, ${output[1]}, params]"
    }
    | toList()
    | map { output_list ->
      assert output_list.size() == 1 : "output channel should contain one event"
      assert output_list[0][0] == "foo" : "Output ID should be same as input ID"
    }
    //| check_format(args: {""}) // todo: check whether output h5mu has the right slots defined
}*/
// TODO: update