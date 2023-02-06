"""Module to run the msdial algorithm for lcms"""

import os
import tempfile
import shutil
import subprocess
import pandas as pd

MSDIAL_PATH = "/msdial"

## VIASH START
# use the following instructions to install msdial_app locally:
#   mkdir src/msdial/msdial_app
#   wget -q https://www.dropbox.com/s/6fn2tjfyudbrg3o/foo.zip?dl=1 -O "msdial.zip"
#   unzip "msdial.zip" -d src/msdial/msdial_app
#   rm msdial.zip
#   chmod +x msdial_app/MsdialConsoleApp
MSDIAL_PATH = "src/msdial/msdial_app"
INPUT_DIR = os.getcwd() + '/resources_test/msdial_demo_files/raw/LCMS_DDA/'
par = {
  'input': [f'{INPUT_DIR}/Nega_Ida_QC_1_1.mzML', f'{INPUT_DIR}/Nega_Ida_QC_1_9.mzML'],
  'name': ["foo", "bar"],
  'type': None,
  'class_id': None,
  'batch': None,
  'analytical_order': None,
  'inject_volume': None,
  'output': 'foo',
  'ms1_data_type': 'Profile',
  'ms2_data_type': 'Profile',
  'ion_mode': r'Positive',
  'dia_file': None,
  'retention_time_begin': float(r'0.0'),
  'retention_time_end': float(r'100.0'),
  'ms1_mass_range_begin': float(r'0.0'),
  'ms1_mass_range_end': float(r'2000.0'),
  'ms2_mass_range_begin': float(r'0.0'),
  'ms2_mass_range_end': float(r'2000.0'),
  'ms1_tolerance_for_centroid': float(r'0.01'),
  'ms2_tolerance_for_centroid': float(r'0.025'),
  'max_charged_number': int(r'2'),
  'execute_rt_correction': r'false'.lower() == 'true',
  'rt_correction_smoothing': r'false'.lower() == 'true',
  'user_setting_intercept': float(r'0.0'),
  'rt_diff_calc_method': r'SampleMinusSampleAverage',
  'extrapolation_method_begin': r'UserSetting',
  'extrapolation_method_end': r'lastpoint',
  'istd_file': None,
  'smoothing_method': r'LinearWeightedMovingAverage',
  'smoothing_level': int(r'3'),
  'minimum_peak_width': int(r'5'),
  'minimum_peak_height': int(r'1000'),
  'mass_slice_width': float(r'0.1'),
  'sigma_window_value': float(r'0.5'),
  'amplitude_cutoff': float(r'0.0'),
  'exclude_after_precursor': r'true'.lower() == 'true',
  'keep_isotope_until': float(r'0.5'),
  'keep_original_precursor_isotopes': r'false'.lower() == 'true',
  'adduct_list': r'[M+H]+,[M+Na]+,[M+NH4]+'.split(','),
  'msp_file': None,
  'retention_time_tolerance_for_identification': float(r'100.0'),
  'accurate_ms1_tolerance_for_identification': float(r'0.01'),
  'accurate_ms2_tolerance_for_identification': float(r'0.05'),
  'identification_score_cutoff': float(r'80.0'),
  'use_retention_information_for_identification_scoring': r'false'.lower() == 'true',
  'use_retention_information_for_identification_filtering': r'false'.lower() == 'true',
  'post_identification_library_file': None,
  'retention_time_tolerance_for_post_identification': float(r'0.1'),
  'accurate_ms1_tolerance_for_post_identification': float(r'0.01'),
  'post_identification_score_cutoff': float(r'85.0'),
  'retention_time_tolerance_for_alignment': float(r'0.05'),
  'ms1_tolerance_for_alignment': float(r'0.015'),
  'retention_time_factor_for_alignment': float(r'0.5'),
  'ms1_factor_for_alignment': float(r'0.5'),
  'peak_count_filter': float(r'0.0'),
  'gap_filling_by_compulsion': r'true'.lower() == 'true',
  'alignment_reference_file_id': int(r'0'),
  'remove_feature_based_on_peak_height_fold_change': r'false'.lower() == 'true',
  'pct_detected_in_at_least_one_group': float(r'0.0'),
  'sample_max_over_blank_average': float(r'5.0'),
  'sample_average_over_blank_average': float(r'5.0'),
  'keep_identified_metabolites': r'true'.lower() == 'true',
  'keep_removable_features': r'true'.lower() == 'true',
  'replace_true_zero': r'false'.lower() == 'true',
  'tracking_isotope_label': r'false'.lower() == 'true',
  'set_fully_labeled_reference_file': r'false'.lower() == 'true',
  'non_labeled_reference_id': int(r'0'),
  'fully_labeled_reference_id': int(r'0'),
  'isotope_tracking_dictionary_id': int(r'0'),
  'corrdec_execute': r'true'.lower() == 'true',
  'corrdec_ms2_tolerance': float(r'0.01'),
  'corrdec_minimum_ms2_peak_height': float(r'1000.0'),
  'corrdec_min_detected_samples': float(r'3.0'),
  'corrdec_exclude_highly_correlated_spots': float(r'0.9'),
  'corrdec_min_corr_ms2': float(r'0.7'),
  'corrdec_margin_1': float(r'0.2'),
  'corrdec_margin_2': float(r'0.7'),
  'corrdec_min_detected_rate': float(r'0.5'),
  'corrdec_min_ms2_relative_intensity': float(r'2.0'),
  'corrdec_remove_peaks_larger_than_precursor': r'true'.lower() == 'true',
  'accumulated_rt_range': float(r'0.2'),
  'ccs_search_tolerance': float(r'10.0'),
  'mobility_axis_alignment_tolerance': float(r'0.02'),
  'use_ccs_for_identification_scoring': r'false'.lower() == 'true',
  'use_ccs_for_identification_filtering': r'true'.lower() == 'true'
}
## VIASH END

MODE = "lcmsdia" if par["dia_file"] else "lcmsdda"

print(f"Running MS-DIAL {MODE}", flush=True)

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
Ms1 data type: {par["ms1_data_type"]}
Ms2 data type: {par["ms2_data_type"]}
Ion mode: {par["ion_mode"]}
{ "Dia file: " + par["dia_file"] if par["dia_file"] else "# Dia file: none"}

# Data correction parameters
Retention time begin: {par["retention_time_begin"]}
Retention time end: {par["retention_time_end"]}
Mass range begin: {par["ms1_mass_range_begin"]}
Mass range end: {par["ms1_mass_range_end"]}
Ms2 mass range begin: {par["ms2_mass_range_begin"]}
Ms2 mass range end: {par["ms2_mass_range_end"]}

# Centroid arguments
ms1 tolerance for centroid: {par["ms1_tolerance_for_centroid"]}
ms2 tolerance for centroid: {par["ms2_tolerance_for_centroid"]}

# Isotope arguments
maximum charged number: {par["max_charged_number"]}

# Retention time correction arguments
excute rt correction: {par["execute_rt_correction"]}
rt correction with smoothing for rt diff: {par["rt_correction_smoothing"]}
user setting intercept: {par["user_setting_intercept"]}
{ "rd diff calc method: " + par["rt_diff_calc_method"] if par["rt_diff_calc_method"] else "# rd diff calc method: none"}
{ "extrapolation method (begin): " + par["extrapolation_method_begin"] if par["extrapolation_method_begin"] else "# extrapolation method (begin): none"}
{ "extrapolation method (end): " + par["extrapolation_method_end"] if par["extrapolation_method_end"] else "# extrapolation method (end): "}
{ "istd file: " + par["istd_file"] if par["istd_file"] else "# istd file: none"}

# Peak detection parameters
Smoothing method: {par["smoothing_method"]}
Smoothing level: {par["smoothing_level"]}
Minimum peak width: {par["minimum_peak_width"]}
Minimum peak height: {par["minimum_peak_height"]}
Mass slice width: {par["mass_slice_width"]}

# Deconvolution parameters
Sigma window value: {par["sigma_window_value"]}
Amplitude cut off: {par["amplitude_cutoff"]}
exclude after precursor: {par["exclude_after_precursor"]}
keep isotope until: {par["amplitude_cutoff"]}
keep original precursor isotopes: {par["amplitude_cutoff"]}

# Adduct list
Adduct list: {','.join(par["adduct_list"])}

# Identification
{"MSP file: " + par["msp_file"] if par["msp_file"] else "# MSP file: none"}
Retention time tolerance for identification: {par["retention_time_tolerance_for_identification"]}
accurate ms1 tolerance for identification: {par["accurate_ms1_tolerance_for_identification"]}
accurate ms2 tolerance for identification: {par["accurate_ms2_tolerance_for_identification"]}
Identification score cut off: {par["identification_score_cutoff"]}
Use retention information for identification scoring: {par["use_retention_information_for_identification_scoring"]}
Use retention information for identification filtering: {par["use_retention_information_for_identification_filtering"]}

# Post identification
{ "text file: " + par["post_identification_library_file"] if par["post_identification_library_file"] else "# text file: none"}
retention time tolerance for post identification: {par["retention_time_tolerance_for_post_identification"]}
accurate ms1 tolerance for post identification: {par["accurate_ms1_tolerance_for_post_identification"]}
post identification score cut off: {par["post_identification_score_cutoff"]}

# Alignment arguments
Retention time tolerance for alignment: {par["retention_time_tolerance_for_alignment"]}
Ms1 tolerance for alignment: {par["ms1_tolerance_for_alignment"]}
Retention time factor for alignment: {par["retention_time_factor_for_alignment"]}
Ms1 factor for alignment: {par["ms1_factor_for_alignment"]}
Peak count filter: {par["peak_count_filter"]}
Gap filling by compulsion: {par["gap_filling_by_compulsion"]}
alignment reference file id: {par["alignment_reference_file_id"]}
Remove feature based on peak height fold-change: {par["remove_feature_based_on_peak_height_fold_change"]}
N% detected in at least one group: {par["pct_detected_in_at_least_one_group"]}
Sample max / blank average: {par["sample_max_over_blank_average"]}
Sample average / blank average: {par["sample_average_over_blank_average"]}
Keep identified and annotated metabolites: {par["keep_identified_metabolites"]}
Keep removable features and assign the tag for checking: {par["keep_removable_features"]}
Replace true zero values with 1/10 of minimum peak height over all samples: {par["replace_true_zero"]}

# isotope tracking arguments
tracking isotope label: {par["tracking_isotope_label"]}
set fully labeled reference file: {par["set_fully_labeled_reference_file"]}
non labeled reference id: {par["non_labeled_reference_id"]}
fully labeled reference id: {par["fully_labeled_reference_id"]}
isotope tracking dictionary id: {par["isotope_tracking_dictionary_id"]}

# corrdec arguments
corrdec excute: {par["corrdec_execute"]}
corrdec ms2 tolerance: {par["corrdec_ms2_tolerance"]}
corrdec minimum ms2 peak height: {par["corrdec_minimum_ms2_peak_height"]}
corrdec minimum number of detected samples: {par["corrdec_min_detected_samples"]}
corrdec exclude highly correlated spots: {par["corrdec_exclude_highly_correlated_spots"]}
corrdec minimum correlation coefficient (ms2): {par["corrdec_min_corr_ms2"]}
corrdec margin 1 (target precursor): {par["corrdec_margin_1"]}
corrdec margin 2 (coeluted precursor): {par["corrdec_margin_2"]}
corrdec minimum detected rate: {par["corrdec_min_detected_rate"]}
corrdec minimum ms2 relative intensity: {par["corrdec_min_ms2_relative_intensity"]}
corrdec remove peaks larger than precursor: {par["corrdec_remove_peaks_larger_than_precursor"]}

# ion mobility arguments
accumulated rt ragne: {par["accumulated_rt_range"]}
ccs search tolerance: {par["ccs_search_tolerance"]}
mobility axis alignment tolerance: {par["mobility_axis_alignment_tolerance"]}
use ccs for identification scoring: {par["use_ccs_for_identification_scoring"]}
use ccs for identification filtering: {par["use_ccs_for_identification_filtering"]}
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

    # write params file
    with open(param_file, "w", encoding='utf-8') as f:
        f.write(param_content)

    # run msdial
    args = [
        f"{MSDIAL_PATH}/MsdialConsoleApp",
        MODE,
        "-i", csv_file,
        "-o", par["output"],
        "-m", param_file,
        "-p"
    ]
    with subprocess.Popen(args) as p:
        p.wait()

if p.returncode != 0:
    raise Exception(f"MS-DIAL finished with exit code {p.returncode}")
