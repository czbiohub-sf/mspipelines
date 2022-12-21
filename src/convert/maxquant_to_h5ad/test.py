from unittest import main, TestCase
import subprocess
from pathlib import Path
import anndata as ad

## VIASH START
meta = {
    'executable': './target/docker/convert/maxquant_to_h5ad',
    'resources_dir': './resources_test/zenodo_4274987',
}
## VIASH END

target ="output.h5ad"
resources_dir, executable = meta["resources_dir"], meta["executable"]
conversion_output = f"{resources_dir}/{target}]"

class TestMaxQuantToHAD(TestCase):
    def _run_and_check_output(self, args_as_list, expected_raise=False):
        try:
            subprocess.check_output([meta['executable']] + args_as_list, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            if not expected_raise:
                print(e.stdout.decode("utf-8"))
            raise e

    def test_maxquant_convert(self):
        self._run_and_check_output(["--input", "zenodo_4274987/maxquant_out",
                                    "--output", target])
        self.assertTrue(Path(target).is_file())
        converted_data = ad.read_h5ad(target)

        #Check if the specified data layers are present in the output
        self.assertListEqual(list(converted_data.layers),['intensity', 'peptides', 'razor_and_unique_peptides', 'sequence_coverage', 'unique_peptides'])
        #Check the number of observations (should be 2: Sample1 & Sample2)
        self.assertEqual(len(converted_data.obs),2)
        #Check the number of metadata columns (proteingroups), should be 270 in the given example
        self.assertEqual(len(converted_data.var),270)
        #TODO is it worth testing further in depth?

if __name__ == "__main__":
    main()