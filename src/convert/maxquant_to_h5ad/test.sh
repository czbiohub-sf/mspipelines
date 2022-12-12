set -eo pipefail

echo ">> Running $meta_functionality_name"
"$meta_executable" \
    --input "zenodo_4274987/maxquant_out" \
    --output "output.h5ad" 

echo ">> Checking whether output files can be found"
[[ ! -f "output.h5ad" ]] && echo "output.h5ad does not exist" && exit 1

echo ">> All tests succeeded!"