set -eo pipefail

echo ">> Running $meta_functionality_name"
"$meta_executable" \
    --taxid "9606" \
    --output "output" \
    --include_contaminants true

echo ">> Checking whether output files can be found"
[[ ! -f "output/9606.fasta" ]] && echo "Output 9606.fasta does not exist" && exit 1

echo ">> All tests succeeded!"