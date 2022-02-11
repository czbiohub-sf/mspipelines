Install Viash & Nextflow
```sh
bin/init
```

Build container
```sh
bin/viash run src/category/maxquant/config.vsh.yaml -- ---setup cb
```

Example run
```sh
resources_test=resources_test/maxquant_test_data

bin/viash run src/category/maxquant/config.vsh.yaml -- \
  --input "$resources_test/Raw/" \
  --fasta "$resources_test/Fasta/20211015_Kistler_Human.Cow.ZEBOV_NP_P2A_VP35_P2A_VP30.fasta" \
  --output output
```

Specify raw files.
```sh
bin/viash run src/category/maxquant/config.vsh.yaml -- \
  --input "$resources_test/Raw/FL0031914.raw" \
  --input "$resources_test/Raw/FL0031916.raw" \
  --input "$resources_test/Raw/FL0031920.raw" \
  --input "$resources_test/Raw/FL0031924.raw" \
  --fasta "$resources_test/Fasta/20211015_Kistler_Human.Cow.ZEBOV_NP_P2A_VP35_P2A_VP30.fasta" \
  --output output
```