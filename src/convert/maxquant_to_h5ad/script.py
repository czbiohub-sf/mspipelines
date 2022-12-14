import pandas as pd
import anndata as ad

## VIASH START
par = {
    "input" : "resources_test/zenodo_4274987/maxquant_out",
    "output": "resources_test/zenodo_4274987/maxquant_out/output.h5ad"
    }
## VIASH END

# helper function for transforming column names in proteingroups
# to snakecase
def fix_headers(df):
    df.columns=df.columns.str.replace("+","and",regex=False)
    df.columns=df.columns.str.replace("%","pct",regex=False)
    df.columns=df.columns.str.replace(" ","_",regex=False)
    df.columns=df.columns.str.lower()
    df.columns=df.columns.str.replace("[^a-z0-9_]*","",regex=True)

# helper function to transform booleans in the dataframes to 
# integers (anndata crashes when parsing 'False' or 'True')
def fix_booleans(df):
    #TODO figure out which are causing the issues
    for column in df.columns:
        df[column] = df[column].replace([False,True], [0,1])

# helper function to collate layer data from proteingroups
def get_layer_data(protein_groups,template,sampleIDs):
    column_names = []
    for sampleID in sampleIDs:
        column_names.append(template.format(sample_id=sampleID))
    x = protein_groups.loc[:,protein_groups.columns.isin(column_names)]
    x.columns=sampleIDs
    x= x.transpose()
    return x

# read sample metadata
summary = pd.read_table(f"{par['input']}/combined/txt/summary.txt")
summary_nt = summary[summary["Raw file"].str.contains("Total")==False]
#read protein group info
protein_groups = pd.read_table(f"{par['input']}/combined/txt/proteinGroups.txt")

#use hardcoded templates
#TODO evaluate if this is the best strategy (alternative = original version, dynamically read the column headers)
templates = {
   'peptides' : "Peptides {sample_id}",
   'razor_and_unique_peptides' : "Razor + unique peptides {sample_id}",
   'unique_peptides' : "Unique peptides {sample_id}",
   'sequence_coverage' : "Sequence coverage {sample_id} [%]",
   'intensity' : "Intensity {sample_id}"
}

#The sample IDs
sampleIDs = summary_nt.loc[:,"Experiment"]

layers={}
for template in templates:
    x=get_layer_data(protein_groups,templates[template],sampleIDs)
    layers[template]=x

#set sample metadata as observations
obs = summary_nt
fix_headers(obs)
fix_booleans(obs)
#set protein identifications as metadata
var = protein_groups
fix_headers(var)
fix_booleans(var)

#Create an AnnData object
adata=ad.AnnData(None,obs,var)
for layer in layers:
    adata.layers[layer]=layers[layer]

#Export data to file...
adata.write_h5ad(par['output'])