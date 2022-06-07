#!/bin/bash

viash_exec="./$functionality_name"

## VIASH START
viash_exec="viash run src/maxquant/maxquant/config.vsh.yaml --"
## VIASH END

$viash_exec \
    --input "/run/media/rcannood/Data/czb_data/Shared_Robrecht/Medium_TIMSTOF_Sensitivity_MBR_20ng_60min/HeLa_20ng_60min_1_A3_1_311.d" \
    --input "/run/media/rcannood/Data/czb_data/Shared_Robrecht/Medium_TIMSTOF_Sensitivity_MBR_20ng_60min/HeLa_20ng_60min_1_A3_1_312.d" \
    --input "/run/media/rcannood/Data/czb_data/Shared_Robrecht/Medium_TIMSTOF_Sensitivity_MBR_20ng_60min/HeLa_20ng_60min_3_A3_1_313.d" \
    --reference "/run/media/rcannood/Data/czb_data/Shared_Robrecht/uniprot-proteome_UP000005640.fasta" \
    --ref_taxonomy_id "9606" \
    --match_between_runs "true" \
    --ms_instrument "Bruker TIMS" \
    --lcms_run_type "TIMS-DDA" \
    --lfq_mode "LFQ" \
    --output output/dryrun_medium/
    # --dryrun