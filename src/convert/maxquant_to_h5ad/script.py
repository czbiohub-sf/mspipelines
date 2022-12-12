import pandas as pd
import anndata as ad

## VIASH START
par = {
    "input" : "zenodo_4274987/maxquant_out/",
    "output": "output.h5ad"
    }
## VIASH END

summary = pd.read_table(f"{par['input']}/combined/txt/summary.txt")
summary_nt = summary[summary["Raw file"].str.contains("Total")==False]

protein_groups = pd.read_table(f"{par['input']}/combined/txt/proteinGroups.txt")

first_exp = summary_nt.iloc[0]

#print(summary_nt)
print(protein_groups.head())
#print(first_exp)

