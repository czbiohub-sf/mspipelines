import os, re, sys, requests
from requests.adapters import HTTPAdapter, Retry

## VIASH START
# par = {
#    'taxid': "9606",
#    'output': "fastas",
#    'include_contaminants': True
#     }

cRAPUrl="http://ftp.thegpm.org/fasta/cRAP/crap.fasta"

taxid=par["taxid"]
fastafile=f'{par["output"]}/{taxid}.fasta'

re_next_link = re.compile(r'<(.+)>; rel="next"')
retries = Retry(total=5, backoff_factor=0.25, status_forcelist=[500, 502, 503, 504])
session = requests.Session()
session.mount("https://", HTTPAdapter(max_retries=retries))

if not os.path.exists(par["output"]):
   # Create a new directory if it does not exist
   os.makedirs(par["output"])

print(f"Storing fasta at {fastafile}")
#UNIPROT METHODS
def get_next_link(headers):
    if "Link" in headers:
        match = re_next_link.match(headers["Link"])
        if match:
            return match.group(1)

def get_batch(batch_url):
    while batch_url:
        response = session.get(batch_url)      
        if response.status_code==400 or response.status_code==404:
            print("Invalid UNIPROT query, please verify this taxonomyID exists")
            response.raise_for_status()
        total = response.headers["x-total-results"]
        yield response, total
        batch_url = get_next_link(response.headers)

#DOWNLOADING THE UNIPROT SEQUENCE DATABASE
url = f"https://rest.uniprot.org/uniprotkb/search?format=fasta&query=%28organism_id%3A{taxid}%29%20AND%20%28reviewed%3Atrue%29&size=500"
print("Downloading sequences ...")
with open(fastafile, 'w+') as f:
    for batch, total in get_batch(url):
        lines = batch.text.splitlines()
        for line in lines:
            print(line, file=f)

    #APPENDING CONTAMINANTS
    if par["include_contaminants"]:
        print("Appending contaminants")
        response = requests.get(cRAPUrl)
        if response.status_code==400 or response.status_code==404:
            print(f"Could not reach cRAP database at {cRAPUrl}")
            response.raise_for_status()
        data = response.text
        #there is a typo in the official cRAP (don't know why :)
        data=data.replace(">KKA1_ECOLX",">sp|KKA1_ECOLX|")
        print(data,file=f)

print("Done")


