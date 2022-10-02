#!/bin/bash

echo ">> Testing MS-DIAL LCMS DDA"
$meta_executable \
  --input "$meta_resources_dir/LCMS_DDA/Nega_Ida_QC_1_1.mzML" \
  --input "$meta_resources_dir/LCMS_DDA/Nega_Ida_QC_1_9.mzML" \
  --class_id foo \
  --class_id bar \
  --ms1_data_type Profile \
  --ms2_data_type Profile \
  --ion_mode Negative \
  --minimum_peak_height 1 \
  --adduct_list "[M-H]-,[M+FA-H]-,[M-H2O-H]-" \
  --retention_time_tolerance_for_identification 4 \
  --accurate_ms1_tolerance_for_identification 0.025 \
  --accurate_ms2_tolerance_for_identification 0.25 \
  --output "output2" | \
  tee output2.txt

echo ">>> Checking contents of stdout"
if ! grep -q 'Finalization finished' output2.txt; then
  echo Could not find content
  exit 1
fi

echo ">>> Checking whether output files can be found"
if ! ls output2/Nega_Ida_QC_1_1* > /dev/null 2>&1; then echo "Output file 1_1 could not be found!"; exit 1; fi
if ls output2/Nega_Ida_QC_1_5* > /dev/null 2>&1; then echo "Output file 1_5 found!"; exit 1; fi
if ! ls output2/Nega_Ida_QC_1_9* > /dev/null 2>&1; then echo "Output file 1_9 could not be found!"; exit 1; fi
if ! ls output2/AlignResult-* > /dev/null 2>&1; then echo "Output file alignresult could not be found!"; exit 1; fi
[[ ! -f output2/params.txt ]] && echo "Param file could not be found!" && exit 1


echo ">> Running MS-DIAL LCMS DIA"
$meta_executable \
  --input "$meta_resources_dir/LCMS_DIA/HILIC_SWATH_25Da_10ms_S01.abf" \
  --input "$meta_resources_dir/LCMS_DIA/HILIC_SWATH_25Da_10ms_S03.abf" \
  --dia_file "$meta_resources_dir/LCMS_DIA/Plasma-HILIC-SWATH-Experiment.txt" \
  --ms1_data_type Profile \
  --ms2_data_type Profile \
  --ion_mode Positive \
  --retention_time_begin 1.5 \
  --retention_time_end 25 \
  --ms1_mass_range_begin 55 \
  --ms1_mass_range_end 1200 \
  --ms2_tolerance_for_centroid 0.05 \
  --minimum_peak_height 3000 \
  --amplitude_cutoff 10 \
  --adduct_list "[M+H]+,[M+Na]+,[M+NH4]+" \
  --accurate_ms1_tolerance_for_identification 0.025 \
  --accurate_ms2_tolerance_for_identification 0.25 \
  --identification_score_cutoff 70 \
  --retention_time_tolerance_for_post_identification 0.25 \
  --output "output3" | \
  tee output3.txt

echo ">>> Checking contents of stdout"
if ! grep -q 'Finalization finished' output3.txt; then
  echo Could not find content
  exit 1
fi

echo ">>> Checking whether output files can be found"
if ! ls output3/HILIC_SWATH_25Da_10ms_S01* > /dev/null 2>&1; then echo "Output file S01 could not be found!"; exit 1; fi
if ls outoutput3put2/HILIC_SWATH_25Da_10ms_S02* > /dev/null 2>&1; then echo "Output file S02 found!"; exit 1; fi
if ! ls output3/HILIC_SWATH_25Da_10ms_S03* > /dev/null 2>&1; then echo "Output file S03 could not be found!"; exit 1; fi
if ! ls output3/AlignResult-* > /dev/null 2>&1; then echo "Output file alignresult could not be found!"; exit 1; fi
[[ ! -f output3/params.txt ]] && echo "Param file could not be found!" && exit 1


echo ">> All tests succeeded!"