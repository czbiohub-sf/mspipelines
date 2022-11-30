set -eo pipefail

echo ">> Running $meta_functionality_name"
"$meta_executable" \
    --input "$meta_resources_dir/maxquant_demo_files/raw/Sample.raw" \
    --reference "$meta_resources_dir/maxquant_demo_files/raw/reference.fasta" \
    --ref_taxonomy_id "9606" \
    --match_between_runs "true" \
    --ms_instrument "Orbitrap" \
    --lcms_run_type "Standard" \
    --lfq_mode "LFQ" \
    --peptides_for_quantification "unique+razor" \
    --main_search_max_combinations "150" \
    --output "output" \
    ---cpus 4 

echo ">> Checking whether output files can be found"
[[ ! -f "output/mqpar.xml" ]] && echo "Output mqpar.xml does not exist" && exit 1
[[ ! -f "output/combined/txt/proteinGroups.txt" ]] && echo "Output proteinGroups.txt does not exist" && exit 1

echo ">> All tests succeeded!"