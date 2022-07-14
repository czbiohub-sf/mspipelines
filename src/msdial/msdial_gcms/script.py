import os
import csv
import re
import tempfile
import shutil
import subprocess
import pandas as pd

msdial_path="/msdial"
## VIASH START
input_dir='resources_test/msdial_demo_files/raw/GCMS/'
par = {
  'input': [f'{input_dir}/140428actsa25_1.cdf', f'{input_dir}/140428actsa26_1.cdf'],
  'output': 'output_test/GCMS_output',
  'name': ['foo', 'bar'],
  'type': ['Sample', 'Sample'],
  'class_id': ['1', '2'],
  'batch': [1, 1],
  'analytical_order': [1, 2],
  'inject_volume': [1.0, 1.0],
  'data_type': 'Centroid',
  'ion_mode': 'Positive',
  'accuracy_type': 'IsNominal',
  'retention_time_begin': int('4'),
  'retention_time_end': int('25'),
  'mass_range_begin': int('85'),
  'mass_range_end': int('600'),
  'smoothing_method': 'LinearWeightedMovingAverage',
  'smoothing_level': int('3'),
  'average_peak_width': int('20'),
  'minimum_peak_height': int('200'),
  'mass_slice_width': float('0.5'),
  'mass_accuracy': float('0.5'),
  'sigma_window_value': float('0.5'),
  'amplitude_cutoff': int('50'),
  'msp_file': None,
  'ri_index_file': None,
  'retention_type': 'RI',
  'ri_compound': 'Alkanes',
  'retention_time_tolerance_for_identification': float('0.5'),
  'retention_index_tolerance_for_identification': int('20'),
  'ei_similarity_tolerance_for_identification': int('70'),
  'identification_score_cutoff': int('70'),
  'alignment_index_type': 'RT',
  'retention_time_tolerance_for_alignment': float('0.075'),
  'retention_index_tolerance_for_alignment': int('20'),
  'ei_similarity_tolerance_for_alignment': int('70'),
  'retention_time_factor_for_alignment': float('0.5'),
  'ei_similarity_factor_for_alignment': float('0.5'),
  'peak_count_filter': int('0'),
  'qc_at_least_filter': 'true'.lower() == 'true'
}
msdial_path="../msdial_build"
## VIASH END

assert len(par["input"]) > 0, "Need to specify at least one --input."

# Create input csv file
csv_vars = {
  'file_path': 'input', 
  'file_name': 'name', 
  'type': 'type', 
  'class_id': 'class_id',
  'batch': 'batch', 
  'analytical_order': 'analytical_order', 
  'inject_volume': 'inject_volume',
}

csv_file = os.path.join(par["output"], "input.csv")
for par_key, par_name in csv_vars.items():
   assert par.get(par_name) is None or len(par["input"]) == len(par[par_name]), f"--{par_name} should be of same length as --input"

# Create params file
param_file = os.path.join(par["output"], "params.txt")
ri_index_file = os.path.join(par["output"], "ri_index_paths.txt")

param_content = f"""# Data type
Data type: {par["data_type"]}
Ion mode: {par["ion_mode"]}
Accuracy type: {par["accuracy_type"]}

# Data correction parameters
Retention time begin: {par["retention_time_begin"]}
Retention time end: {par["retention_time_end"]}
Mass range begin: {par["mass_range_begin"]}
Mass range end: {par["mass_range_end"]}

# Peak detection parameters
Smoothing method: {par["smoothing_method"]}
Smoothing level: {par["smoothing_level"]}
Average peak width: {par["average_peak_width"]}
Minimum peak height: {par["minimum_peak_height"]}
Mass slice width: {par["mass_slice_width"]}
Mass accuracy: {par["mass_accuracy"]}

# MS1Dec parameters
Sigma window value: {par["sigma_window_value"]}
Amplitude cut off: {par["amplitude_cutoff"]}

# Identification
{"MSP file: " + par["msp_file"] if par["msp_file"] else "# MSP file: none"}
{"RI index file pathes: " + ri_index_file if par["ri_index_file"] else "# RI index file pathes: none"}
Retention type: {par["retention_type"]}
RI compound: {par["ri_compound"]}
Retention time tolerance for identification: {par["retention_time_tolerance_for_identification"]}
Retention index tolerance for identification: {par["retention_index_tolerance_for_identification"]}
EI similarity tolerance for identification: {par["ei_similarity_tolerance_for_identification"]}
Identification score cut off: {par["identification_score_cutoff"]}
Use retention information for identification scoring: {par["use_retention_information_for_identification_scoring"]}
Use retention information for identification filtering: {par["use_retention_information_for_identification_filtering"]}
Only report top hit: {par["only_report_top_hit"]}

# Alignment parameters setting
Alignment index type: {par["alignment_index_type"]}
Retention time tolerance for alignment: {par["retention_time_tolerance_for_alignment"]}
Retention index tolerance for alignment: {par["retention_index_tolerance_for_alignment"]}
EI similarity tolerance for alignment: {par["ei_similarity_tolerance_for_alignment"]}
Retention time factor for alignment: {par["retention_time_factor_for_alignment"]}
EI similarity factor for alignment: {par["ei_similarity_factor_for_alignment"]}
Peak count filter: {par["peak_count_filter"]}
Remove feature based on peak height fold-change: {par["remove_feature_based_on_peak_height_fold_change"]}
N% detected in at least one group: {par["pct_detected_in_at_least_one_group"]}
Sample max / blank average: {par["sample_max_over_blank_average"]}
Sample average / blank average: {par["sample_average_over_blank_average"]}
Keep identified and annotated metabolites: {par["keep_identified_metabolites"]}
Keep removable features and assign the tag for checking: {par["keep_removable_features"]}
Replace true zero values with 1/10 of minimum peak height over all samples: {par["replace_true_zero"]}
"""

with tempfile.TemporaryDirectory() as temp_dir:
   # copy input files to tempdir
   # because MSDial otherwise generates a lot
   # of temporary files in the input dir.
   sources = par["input"]
   dests = [ os.path.join(temp_dir, os.path.basename(file)) for file in par["input"] ]

   for src,dst in zip(par["input"], dests):
      print(f"Copying {src} to {dst}", flush=True)
      shutil.copyfile(src, dst)

   par["input"] = dests

   # create output dir if not exists
   if not os.path.exists(par["output"]):
      os.makedirs(par["output"])
   
   # write input csv file
   data = {new: par[key] for new, key in csv_vars.items() if par.get(key) is not None}
   data_df = pd.DataFrame(data)
   data_df.to_csv(csv_file, index=False)
   
   # create ri index file paths file
   # (if needed)
   if par["ri_index_file"]:
      assert len(par["ri_index_file"]) == 1 or len(par["ri_index_file"]) == len(par["input"]), "Length of --ri_index_file must be one or equal to the length of --input"
      if len(par["ri_index_file"]) == 1:
         par["ri_index_file"] = len(par["input"]) * par["ri_index_file"]

      with open(ri_index_file, 'w') as out_file:
         tsv_writer = csv.writer(out_file, delimiter="\t")
         ri_file_data = zip(dests, par["ri_index_file"])
         tsv_writer.writerows(ri_file_data)

   # write params file
   with open(param_file, "w") as f:
      f.write(param_content)

   # run msdial
   p = subprocess.Popen(
      [
         f"{msdial_path}/MsdialConsoleApp", 
         "gcms", 
         "-i", csv_file,
         "-o", par["output"],
         "-m", param_file,
         "-p"
      ]
   )
   p.wait()

if p.returncode != 0:
   raise Exception(f"MS-DIAL finished with exit code {p.returncode}") 
