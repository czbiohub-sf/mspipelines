"""This Module is used to convert MaxQuant output to anndata"""
import pandas as pd
import anndata as ad

## VIASH START
par = {
    "input": "resources_test/zenodo_4274987/maxquant_out",
    "output": "resources_test/zenodo_4274987/maxquant_out/output.h5ad",
}
## VIASH END


# helper function for transforming column names in proteingroups
# to snakecase
def fix_headers(dataframe_old:pd.DataFrame)->pd.DataFrame:
    """Fixes the headers by unescaping and converting to
    snakecase and replacing booleans with integers"""
    dataframe = dataframe_old.copy(deep=True)

    dataframe.columns = dataframe.columns.str.lower()

    replaces={  "+":("and",False),
                "%":("and",False),
                " ":("and",False),
                "[^a-z0-9_]*":("",True)
             }

    for old, (new,use_regex) in replaces.items():
        dataframe.columns = dataframe.columns.str.replace(old, new, regex=use_regex)
    #TODO figure out which are causing the issues
    for column_name,column in dataframe.items():
        print(f"Removing booleans for : {column_name} ")
        column.replace([False, True], [0, 1])
    return dataframe

# helper function to collate layer data from proteingroups
def get_layer_data(_protein_groups:pd.DataFrame, template:str,
                    sample_ids:pd.DataFrame)->pd.DataFrame:
    """Retrieves data for the protein group layers"""
    headers = []
    for sample_id in sample_ids:
        headers.append(template.format(sample_id=sample_id))
    dataframe = _protein_groups.loc[:, _protein_groups.columns.isin(headers)]
    dataframe.columns = sample_ids
    dataframe = dataframe.transpose()
    return dataframe

# read sample metadata
summary = pd.read_table(f"{par['input']}/combined/txt/summary.txt")
# this is the only working, confirmed way
summary_nt = summary[summary["Raw file"].str.contains("Total")==False]
# read protein group info
protein_groups = pd.read_table(f"{par['input']}/combined/txt/proteinGroups.txt")

# use hardcoded templates
#TODO evaluate strategy (alternative = dynamically load column headers)
templates = {
    "peptides": "Peptides {sample_id}",
    "razor_and_unique_peptides": "Razor + unique peptides {sample_id}",
    "unique_peptides": "Unique peptides {sample_id}",
    "sequence_coverage": "Sequence coverage {sample_id} [%]",
    "intensity": "Intensity {sample_id}",
}

# The sample IDs
sampleIDs = summary_nt.loc[:, "Experiment"]

layers = {}
for key, value in templates.items():
    x = get_layer_data(protein_groups, value, sampleIDs)
    layers[key] = x

# set sample metadata as observations
obs=fix_headers(summary_nt)
# set protein identifications as metadata
var = fix_headers(protein_groups)

# Create an AnnData object
adata = ad.AnnData(None, obs, var)
for key, value in layers.items():
    adata.layers[key] = layers[key]

# Export data to file...
adata.write_h5ad(par["output"])
