"""This module hosts a maxquant process"""
import os
import re
import subprocess
import tempfile
import shutil
import pandas as pd
from jinja2 import FileSystemLoader, Environment

## VIASH START
par = {
    "input": [
        "resources_test/zenodo_4274987/raw/Sample1.raw",
        "resources_test/zenodo_4274987/raw/Sample2.raw"
    ],
    "input_experiment": [],
    "input_fraction": [],
    "input_ptm": [],
    "output":"output/",
    "reference": ["resources_test/maxquant_test_data/Fasta/20211015_Kistler_Human.Cow.ZEBOV_NP_P2A_VP35_P2A_VP30.fasta"],
    "ref_identifier_rule": [ ">.*\\|(.*)\\|" ],
    "ref_description_rule": [ ">(.*)" ],
    "ref_taxonomy_rule": [ "" ],
    "ref_taxonomy_id": [ "" ],
    "match_between_runs": True,
    "ms_instrument": "Bruker TIMS",
    "lcms_run_type": "Standard",
    "dryrun": True,
    "peptides_for_quantification":"unique+razor",
    "main_search_max_combinations":200,
    "dia_library_type": "tsv",
    "dia_library": None
}
meta = {
   "resources_dir": "src/maxquant/maxquant/",
   "cpus":"4"
}
## VIASH END

# if par_input is a directory, look for raw files
if len(par["input"]) == 1 and os.path.isdir(par["input"][0]):
    par["input"] = [os.path.join(dp, f)
                   for dp, _, filenames in os.walk(par["input"])
                   for f in filenames if re.match(r'.*\.raw', f)]

# use absolute paths
par["input"] = [ os.path.abspath(f) for f in par["input"] ]
par["reference"] = [ os.path.abspath(f) for f in par["reference"] ]
par["output"] = os.path.abspath(par["output"])
if par["dia_library"]:
    par["dia_library"] = [ os.path.abspath(f) for f in par["dia_library"] ]
else:
    par["dia_library"] = []
    
# Load parameter sets from tsv files
def load_tsv(file_path:str, loc_selector:str)->pd.DataFrame:
    """Loads a TSV file into a dataframe"""
    dataframe = pd.read_table(
            f"{meta['resources_dir']}/settings/{file_path}",
            sep="\t",
            index_col="id",
            dtype=str,
            keep_default_na=False,
            na_values=['_']
         )
    if loc_selector:
        return dataframe.loc[par[loc_selector]]
    return dataframe

tsv_dispatcher = {
   "match_between_runs_settings": ("match_between_runs.tsv", "match_between_runs"),
   "ms_instrument_settings": ("ms_instrument.tsv", "ms_instrument"),
   "group_type_settings":  ("group_type.tsv", "lcms_run_type")
}
for var_name, (filepath, selector) in tsv_dispatcher.items():
    tsv_dispatcher[var_name] = load_tsv(filepath, selector)

# set defaults of input related args
if not par["input_experiment"]:
    par["input_experiment"] = [
        re.sub(r"_\d+$", "", os.path.basename(file)) for file in par["input"]
    ]
if not par["input_fraction"]:
    par["input_fraction"] = [ 32767 ]
if not par["input_ptm"]:
    par["input_ptm"] = [ False ]

# check length of all input related args
inp_args = ["input", "input_experiment", "input_fraction", "input_ptm"]
for inp_arg in inp_args:
    if len(par[inp_arg]) == 1 and len(par["input"]) > 1:
        par[inp_arg] = par[inp_arg] * len(par["input"])

    assert len(par["input"]) == len(par[inp_arg]), \
        f"--{inp_arg} must have same length as --input"

# check length of all reference related args
# including reference in it as well for ease of use later on
ref_args = ["reference", "ref_identifier_rule", "ref_description_rule",
            "ref_taxonomy_rule", "ref_taxonomy_id"]
for ref_arg in ref_args:
    if len(par[ref_arg]) == 1 and len(par["reference"]) > 1:
        par[ref_arg] = par[ref_arg] * len(par["reference"])

    assert len(par["reference"]) == len(par[ref_arg]), \
        f"--{ref_arg} must have same length as --reference"

fastas = [dict(zip(ref_args, values)) for values in zip(*[par[arg] for arg in ref_args])]

# process quant mode parameter
# this information was derived by toggling through parameters in the MaxQuant GUI
# and inspecting the difference in mqpar.xml contents
quant_mode_options = ["all", "unique+razor", "unique"]
quant_mode = quant_mode_options.index(par["peptides_for_quantification"])

# process dia library type
par["dia_library_type"] = {"MaxQuant": "0", "tsv": "1"}[par["dia_library_type"]]

# copy input files to tempdir
with tempfile.TemporaryDirectory() as temp_dir:
    # prepare to copy input files to tempdir
    old_inputs = par["input"]
    new_inputs = [os.path.join(temp_dir, os.path.basename(f)) for f in old_inputs]
    par["input"] = new_inputs
    inputs = [dict(zip(inp_args, values)) for values in zip(*[par[arg] for arg in inp_args])]

    # create output dir if not exists
    if not os.path.exists(par["output"]):
        os.makedirs(par["output"])

    # Create params file
    param_file = os.path.join(par["output"], "mqpar.xml")
    file_loader = FileSystemLoader(f"{meta['resources_dir']}/templates/")
    environment = Environment(loader=file_loader, )
    template = environment.get_template("root.xml.jinja")

    if meta['cpus'] is None:
        meta['cpus']=1

    # create new dict
    new_pars = {
        "inputs": inputs,
        "fastas": fastas,
        "match_between_runs_settings": tsv_dispatcher['match_between_runs_settings'],
        "ms_instrument_settings": tsv_dispatcher['ms_instrument_settings'],
        "group_type_settings": tsv_dispatcher['group_type_settings'],
        "quant_mode": quant_mode,
        "cpus": meta["cpus"]
    }
    render_kwargs = par | new_pars

    param_content = template.render(** render_kwargs)

    with open(param_file, "w", encoding='utf-8') as f:
        f.write(param_content)

    if not par["dryrun"]:
        # copy input files
        for old, new in zip(old_inputs, new_inputs):
            if os.path.isdir(old):
                shutil.copytree(old, new)
            else:
                shutil.copyfile(old, new)
        try:
            # run maxquant
            PROCESS = subprocess.check_call(
              ["dotnet", "/maxquant/bin/MaxQuantCmd.exe", os.path.basename(param_file)],
              cwd=os.path.dirname(param_file)
           )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"MaxQuant finished with exit code {e.returncode}") from e
