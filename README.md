# msmpipelines

## Run a pipeline with a release

Software requirements: Bash, Docker, Nextflow.

```sh
NXF_VER=21.10.6 nextflow \
  run https://github.com/czbiohub/mspipelines.git \
  -r 0.1.0 \
  -main-script workflows/maxquant/main.nf \
  --input 'https://zenodo.org/record/4274987/files/Sample1.raw;https://zenodo.org/record/4274987/files/Sample2.raw' \
  --reference 'https://zenodo.org/record/4274987/files/Protein_database.fasta' \
  --publishDir output/ \
  -resume \
  -latest
```

## Installation instructions for developers

First off, you can install Viash and Nextflow using the `bin/init` script. This will download the
right version of Viash and Nextflow to be able to build the Viash components from scratch.

```sh
bin/init
```

Next, you can build all Viash components into containerised Nextflow modules or Bash CLI scripts
by using the `bin/viash_build` command. The first time it might take a long time to build all 
Docker containers from scratch, but afterwards rebuilding the components should be significantly
faster thanks to the caching of Docker layers.

```sh
bin/viash_build
```

If you only need a subset of components, you can use any of the query parameters to selectively
build a subset of components. Check `bin/viash_build --help` for more details.

You can download the test resource data from S3 to `resources_test/` by running:
```sh
target/docker/download/sync_resources_test/sync_resources_test
```

You can test whether the Nextflow pipeline works by running:
```sh
workflows/maxquant/examples/manual.sh
```

You can unit test all components (for which unit tests have been defined) by running:
```sh
bin/viash_test
```