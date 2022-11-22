import os
import re
import subprocess
import tempfile
import shutil
import pandas as pd
from jinja2 import FileSystemLoader, Environment

## VIASH START
par = {
   "input": ["resources_test/zenodo_4274987/raw/Sample1.raw", "resources_test/zenodo_4274987/raw/Sample2.raw"],
   "output":"output/",
   "reference": ["resources_test/maxquant_test_data/Fasta/20211015_Kistler_Human.Cow.ZEBOV_NP_P2A_VP35_P2A_VP30.fasta"],
   "match_between_runs": True,
   "ref_taxonomy_id": None,
   "ms_instrument": "Bruker TIMS",
   "lcms_run_type": "Standard",
   "dryrun": True,
   "quantMode":1,
   "mainSearchMaxCombinations":200
}
meta = {
   "resources_dir": "src/maxquant/maxquant/",
   "cpu": None
}
## VIASH END

# if par_input is a directory, look for raw files
if len(par["input"]) == 1 and os.path.isdir(par["input"][0]):
   par["input"] = [os.path.join(dp, f) 
                   for dp, _, filenames in os.walk(par["input"])
                   for f in filenames if re.match(r'.*\.raw', f)]

# set taxonomy id to empty string if not specified
if not par["ref_taxonomy_id"]:
   par["ref_taxonomy_id"] = ["" for _ in par["reference"]]

# # use absolute paths
# for par_key in ("input", "reference", "output"):
#    par[par_key] = [os.path.abspath(f) for f in par[par_key]]

# use absolute paths
par["input"] = [ os.path.abspath(f) for f in par["input"] ]
par["reference"] = [ os.path.abspath(f) for f in par["reference"] ]
par["output"] = os.path.abspath(par["output"])

# auto set experiment names
experiment_names = [re.sub(r"_\d+$", "", os.path.basename(file))
                    for file in par["input"]]

# Load parameters that which are defined in tsv files.
def load_tsv(file_path, loc_selector):
   df = pd.read_table(
            f"{meta['resources_dir']}/settings/{file_path}",
            sep="\t",
            index_col="id",
            dtype=str,
            keep_default_na=False,
            na_values=['_']
         )
   if loc_selector:
      return df.loc[par[loc_selector]]
   return df
   

tsv_dispatcher = {
   "match_between_runs_settings": ("match_between_runs.tsv", "match_between_runs"),
   "ms_instrument_settings": ("ms_instrument.tsv", "ms_instrument"),
   "group_type_settings":  ("group_type.tsv", "lcms_run_type")
}
for var_name, (filepath, selector) in tsv_dispatcher.items():
   tsv_dispatcher[var_name] = load_tsv(filepath, selector)

# check reference metadata
assert len(par["reference"]) == len(par["ref_taxonomy_id"]), \
       "--ref_taxonomy_id must have same length as --reference"

# copy input files to tempdir
with tempfile.TemporaryDirectory() as temp_dir:
   # prepare to copy input files to tempdir
   old_inputs = par["input"]
   new_inputs = [os.path.join(temp_dir, os.path.basename(f)) for f in old_inputs]
   par["input"] = new_inputs

   # create output dir if not exists
   if not os.path.exists(par["output"]):
      os.makedirs(par["output"])

   # Create params file
   param_file = os.path.join(par["output"], "mqpar.xml")
   file_loader = FileSystemLoader(f"{meta['resources_dir']}/templates/")
   environment = Environment(loader=file_loader)
   template = environment.get_template("fastafileinfo.xml.jinja", parent="root.xml.jinja")

   param_content = template.render(
                  input=par['input'],
                  output=par['output'],
                  fastas=zip(par['reference'],par['ref_taxonomy_id']),
                  experiments=experiment_names,
                  match_between_runs=par['match_between_runs'],
                  match_between_runs_settings=tsv_dispatcher['match_between_runs_settings'],
                  ms_instrument_settings=tsv_dispatcher['ms_instrument_settings'],
                  group_type_settings=tsv_dispatcher['group_type_settings'],
                  quantMode=par['quantMode'],
                  mainSearchMaxCombinations=par['mainSearchMaxCombinations']
                 )

   # Strip empty lines from the file 
   # No proper jinja-solution for the very first line of the file
   param_content = os.linesep.join([s for s in param_content.splitlines() if s])


   with open(param_file, "w") as f:
      f.write(param_content)

   if not par["dryrun"]:
      # copy input files
      for old, new in zip(old_inputs, new_inputs):
         if (os.path.isdir(old)):
            shutil.copytree(old, new)
         else:
            shutil.copyfile(old, new)
         
      try:
         # run maxquant
         p = subprocess.check_call(
            ["dotnet", "/maxquant/bin/MaxQuantCmd.exe", os.path.basename(param_file)], 
            cwd=os.path.dirname(param_file)
         )
      except subprocess.CalledProcessError as e:
         raise RuntimeError(f"MaxQuant finished with exit code {e.returncode}") from e