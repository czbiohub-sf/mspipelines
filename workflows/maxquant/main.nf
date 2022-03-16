nextflow.enable.dsl=2

workflowDir = params.rootDir + "/workflows"
targetDir = params.rootDir + "/target/nextflow"

include { maxquant } from targetDir + "/maxquant/maxquant/main.nf" params(params)
include { maxquant_to_h5ad } from targetDir + "/convert/maxquant_to_h5ad/main.nf" params(params)

// include { publish } from targetDir + "/transfer/publish/main.nf" params(params)
include { overrideOptionValue; has_param; check_required_param } from workflowDir + "/utils/utils.nf" params(params)

/*
MaxQuant Processing - CLI workflow

A workflow for running the default MaxQuant processing components.
Exactly one of '--input' and '--csv' must be passed as a parameter.

Parameters:
  --id       ID of the sample, optional.
  --input    Path to the sample.
  --csv      A CSV file with required columns 'input' and optional columns 'id'.
  --output   Path to an output directory.
*/
workflow {
  if (has_param("help")) {
    log.info """TODO: help"""
    exit 0
  }

  if (has_param("input") == has_param("csv")) {
    exit 1, "ERROR: Please provide either an --input parameter or a --csv parameter"
  }
  
  def multirun = has_param("csv")
  if (multirun) {
    input_ch = Channel.fromPath(params.csv)
      | splitCsv(header: true, sep: ",")
  } else {
    input_ch = Channel.value( params.subMap(["input", "reference"]) )
  }

  check_required_param("publishDir", "where output files will be published")

  input_ch
    | run_wf
    // | map { overrideOptionValue(it, "publish", "output", "${params.output}/${it[0]}.h5mu") }
    // | publish
}

/*
TX Processing - Common workflow

A workflow for running the default RNA processing components.

input channel event format: [ id, file, params ]
  value id:                      an event id
  value file:                    an h5mu input file
  value params:                  the params object, which may already have sample specific overrides
output channel event format: [ id, file, params ]
  value id:                      same as input
  value file:                    an h5mu output file
  value params:                  same as input params
*/
workflow run_wf {
  take:
  input_ch

  main:
  output_ch = input_ch 
    | map { li ->
      def multirun = has_param("csv")

      // process input
      if (li.containsKey("input") && li.input) {
        input_path = file(li.input)
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
        id_value = "cli_run"
      } else {
        exit 1, "ERROR: The provided csv file should contain an 'id' column per run"
      }
      [ id_value, [ input: input_path, reference: reference_path ], params ]
    }
    | view { "before maxquant: [${it[0]}, ${it[1]}, params]" }
    | maxquant
    | maxquant_to_h5ad
    | view { "after maxquant: ${it[0]} - ${it[1]}" }

  emit:
  output_ch
}


/*
TX Processing - Integration testing

A workflow for running the default RNA processing components.
*/
workflow test_wf {
  
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
}