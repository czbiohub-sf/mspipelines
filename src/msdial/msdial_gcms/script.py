import os
import csv
import re
import tempfile
import shutil
import subprocess

msdial_path="/msdial"
## VIASH START
par = {
  'input': ['/home/rcannood/Data Intuitive Dropbox/Robrecht Cannoodt/msdial/demo/GCMS'],
  'output': '/home/rcannood/Data Intuitive Dropbox/Robrecht Cannoodt/msdial/demo/GCMS_output',
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
is_dir = [ os.path.isdir(file) for file in par["input"] ]

if len(par["input"]) > 1:   
   assert not any(is_dir), "Either pass to --input a single directory or a set of files."

dir_mode=all(is_dir)

# Create params file
param_file = os.path.join(par["output"], "params.txt")
ri_index_file = os.path.join(par["output"], "ri_index_paths.txt")

param_content = f"""# Data type
Data type: {par["data_type"]}
Ion mode: {par["ion_mode"]}
Accuracy type: {par["accuracy_type"]}

# Data collection parameters
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

# Alignment parameters setting
Alignment index type: {par["alignment_index_type"]}
Retention time tolerance for alignment: {par["retention_time_tolerance_for_alignment"]}
Retention index tolerance for alignment: {par["retention_index_tolerance_for_alignment"]}
EI similarity tolerance for alignment: {par["ei_similarity_tolerance_for_alignment"]}
Retention time factor for alignment: {par["retention_time_factor_for_alignment"]}
EI similarity factor for alignment: {par["ei_similarity_factor_for_alignment"]}
Peak count filter: {par["peak_count_filter"]}
QC at least filter: {par["qc_at_least_filter"]}
"""

with tempfile.TemporaryDirectory() as temp_dir:
   # copy input files to tempdir
   # because MSDial otherwise generates a lot
   # of temporary files in the input dir.
   if dir_mode:
      shutil.copytree(par["input"][0], temp_dir, dirs_exist_ok=True)
   else:
      for file in par["input"]:
         dest = os.path.join(temp_dir, os.path.basename(file))
         print(f"Copying {file} to {dest}")
         shutil.copyfile(file, dest)

   # create output dir if not exists
   if not os.path.exists(par["output"]):
      os.makedirs(par["output"])
   
   # create ri index file paths file
   # (if needed)
   if par["ri_index_file"]:
      with open(ri_index_file, 'w') as out_file:
         tsv_writer = csv.writer(out_file, delimiter="\t")

         for top, dirs, files in os.walk(temp_dir):
            input_files = [ os.path.join(top, file) for file in files if re.match('.*\.(abf|cdf|mzml|ibf|wiff|wiff2|raw|d)$', file)]
            tsv_writer.writerows([[file, par["ri_index_file"]] for file in input_files])

   # write params file
   with open(param_file, "w") as f:
      f.write(param_content)

   # run msdial
   p = subprocess.Popen(
      [
         f"{msdial_path}/MsdialConsoleApp", 
         "gcms", 
         "-i", temp_dir,
         "-o", par["output"],
         "-m", param_file,
         "-p"
      ]
   )
   p.wait()

if p.returncode != 0:
   raise Exception(f"MS-DIAL finished with exit code {p.returncode}") 
