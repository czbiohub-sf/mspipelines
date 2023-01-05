set -eo pipefail

echo ">> Running $meta_functionality_name"
"$meta_executable" \
    --input "$meta_resources_dir/msgf_demo_files/sample.mzML" \
    --output "output/sample.mzid" \
    --fasta "$meta_resources_dir/msgf_demo_files/reference.fasta" \
    --conf "$meta_resources_dir/msgf_demo_files/param.txt" \

#!/bin/bash
echo ">>> Checking whether output files can be found"
[[! -f output/sample.mzid ]] && echo "Output file not found!" && exit 1

echo ">> All tests succeeded!"