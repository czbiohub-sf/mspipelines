"""This module is used to download and preprocess a protein sequence database"""
import os
import re
import requests
from requests.adapters import HTTPAdapter, Retry

## VIASH START
par = {
     'taxid': "694009",
     'output': "fastas",
     'include_contaminants': True
      }
## VIASH END

BASE_URL="https://rest.uniprot.org/uniprotkb/search?format=fasta&query="
CRAP_URL="http://ftp.thegpm.org/fasta/cRAP/crap.fasta"
TAXON_ID=par["taxid"]
fastafile=f'{par["output"]}/{TAXON_ID}.fasta'

re_next_link = re.compile(r'<(.+)>; rel="next"')
retries = Retry(total=5, backoff_factor=0.25, status_forcelist=[500, 502, 503, 504])
session = requests.Session()
session.mount("https://", HTTPAdapter(max_retries=retries))

if not os.path.exists(par["output"]):
   # Create a new directory if it does not exist
    os.makedirs(par["output"])

print(f"Storing fasta at {fastafile}")
#UNIPROT METHODS
def get_next_link(headers:str)->str:
    """Retrieve the next entry in the FASTA string"""
    if "Link" in headers:
        match = re_next_link.match(headers["Link"])
        if match:
            return match.group(1)
    return ""

def get_batch(batch_url:str):
    """Retrieve a batch of entries to include in the FASTA database"""
    while batch_url:
        batch_response = session.get(batch_url)
        if batch_response.status_code in(400,404):
            print("Invalid UNIPROT query, please verify this taxonomyID exists")
            batch_response.raise_for_status()
        batch_total = batch_response.headers["x-total-results"]
        yield batch_response, batch_total
        batch_url = get_next_link(batch_response.headers)

#DOWNLOADING THE UNIPROT SEQUENCE DATABASE

url = f"{BASE_URL}%28organism_id%3A{TAXON_ID}%29%20AND%20%28reviewed%3Atrue%29&size=500"
print("Downloading sequences ...")
with open(fastafile, 'w+', encoding='utf-8') as f:
    for batch, total in get_batch(url):
        lines = batch.text.splitlines()
        for line in lines:
            print(line, file=f)

    #APPENDING CONTAMINANTS
    if par["include_contaminants"]:
        print("Appending contaminants")
        response = requests.get(CRAP_URL,timeout=30)
        if response.status_code in(400,404):
            print(f"Could not reach cRAP database at {CRAP_URL}")
            response.raise_for_status()
            #there is a typo in the final entry of the official cRAP (don't know why :)
        data = response.text
        data=data.replace(">KKA1_ECOLX",">sp|KKA1_ECOLX|")
        lines = data.splitlines()
        for line in lines:
            if line.endswith('|'):
                line=line+"Known Contaminant"
            print(line,file=f)

print("Done")
