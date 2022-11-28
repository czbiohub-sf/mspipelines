import os
import re
import requests
from requests.adapters import HTTPAdapter, Retry

## VIASH START
par = {
   "taxid": "9606",
   "output":"fastas"
    }

re_next_link = re.compile(r'<(.+)>; rel="next"')
retries = Retry(total=5, backoff_factor=0.25, status_forcelist=[500, 502, 503, 504])
session = requests.Session()
session.mount("https://", HTTPAdapter(max_retries=retries))

def get_next_link(headers):
    if "Link" in headers:
        match = re_next_link.match(headers["Link"])
        if match:
            return match.group(1)

def get_batch(batch_url):
    while batch_url:
        response = session.get(batch_url)
        response.raise_for_status()
        total = response.headers["x-total-results"]
        yield response, total
        batch_url = get_next_link(response.headers)

taxid=par["taxid"]
fastafile=f'{par["output"]}/{taxid}.fasta'

if not os.path.exists(par["output"]):
   # Create a new directory if it does not exist
   os.makedirs(par["output"])

print("Storing fasta at "+fastafile)

url = f"https://rest.uniprot.org/uniprotkb/search?format=fasta&query=%28organism_id%3A{taxid}%29%20AND%20%28reviewed%3Atrue%29&size=500"
progress = 0

with open(fastafile, 'w+') as f:
    for batch, total in get_batch(url):
        lines = batch.text.splitlines()
        for line in lines:
            print(line, file=f)
            if(line.startswith('>')):
                progress=progress+1
        print(f'{progress} / {total}')

print("Done !")