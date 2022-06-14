import os
import re
import tempfile
import shutil
import subprocess
import pandas as pd

## VIASH START
par = {
   "input": ["resources_test/zenodo_4274987/raw/Sample1.raw", "resources_test/zenodo_4274987/raw/Sample2.raw"],
   "output": "output/",
   "analysis_type": "gcms"
}
meta = {
   "resources_dir": "src/maxquant/maxquant/"
}
## VIASH END

templ = os.path.join(meta["resources_dir"], "templates/gcms.txt")

# Create params file
param_file = os.path.join(par["output"], "params.txt")
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
{"MSP file: " + par["msp_file"] if par["msp_file"] else "# MSP file:"}
{"RI index file pathes: " + par["ri_index"] if par["ri_index"] else "# RI index file pathes:"}
Retention type: {par["retention_type"]}
RI compound: {par["ri_compound"]}
Retention time tolerance for identification: {par["retention_time_tolerance_for_identification"]}
Retention index tolerance for identification: {par["retention_index_tolerance_for_identification"]}
EI similarity tolerance for identification: {par["ei_similarity_tolerance_for_identification"]}
Identification score cut off: {par["identification_score_cutoff"]}

# Alignment parameters setting
Alignment index type: {par["alignment_index_type"]}
Retention time tolerance for alignment: {par["retention_time_tolerance_for_alignment"]}
#Retention index tolerance for alignment: {par["retention_index_tolerance_for_alignment"]}
EI similarity tolerance for alignment: {par["ei_similarity_tolerance_for_alignment"]}
Retention time factor for alignment: {par["retention_time_factor_for_alignment"]}
EI similarity factor for alignment: {par["ei_similarity_factor_for_alignment"]}
Peak count filter: {par["peak_count_filter"]}
QC at least filter: {par["qc_at_least_filter"]}
"""

# copy input files to tempdir
with tempfile.TemporaryDirectory() as temp_dir:
   shutil.copytree(par["input"], temp_dir, dirs_exist_ok=True)
   par["input"] = temp_dir

   # create output dir if not exists
   if not os.path.exists(par["output"]):
      os.makedirs(par["output"])

      with open(param_file, "w") as f:
         f.write(param_content)

   # run msdial
   p = subprocess.Popen(
      [
         "/msdial/MsdialConsoleApp", 
         "gcms", 
         "-i", par["input"],
         "-o", par["output"],
         "-m", param_file,
         "-p"
      ]
   )
   p.wait()

   if p.returncode != 0:
      raise Exception(f"MS-DIAL finished with exit code {p.returncode}") 