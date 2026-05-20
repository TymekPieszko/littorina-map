import pandas as pd
import numpy as np
import argparse, requests

def remove_whitespace(df):
    for i in df.columns:
        if df[i].dtype == 'object':
            df[i] = df[i].str.strip()

# First-stage parser: sheet URL
parser = argparse.ArgumentParser()
parser.add_argument("--sheet_url", type=str, required=True)
args, remaining = parser.parse_known_args()

# Convert sheet URL
sheet_url = (
    args.sheet_url
    .replace("/edit?", "/export?format=csv&")
    .split("#")[0]
)
 
df = pd.read_csv(sheet_url, header=3)
df = df.drop(columns=['Timestamp', 'Corresponder', 'Latitude', 'Longitude', 'Targeted_coverage'])
df.columns = df.columns.str.lower()
remove_whitespace(df)
# print(df.columns)

# Second-stage parser: arguments from df columns
parser = argparse.ArgumentParser()
# parser.add_argument(f"--data", type=str, required=True)
for column in df.columns:
    parser.add_argument(f"--{str(column).lower()}", type=str, required=False)
args = vars(parser.parse_args(remaining))

# Filter
for column, category in args.items():
    if category is None:
        continue
    df = df.loc[np.isin(df[column], category.split(","))]

# Useful info
n = len(df)
ids = len(df["biosample_id"].unique())
print("-" * 50)
print(f"Fetching URLs for {n} samples with {ids} unique BioSample IDs...")
print("-" * 50)
if ids < n:
    print("WARNING: duplicate BioSample IDs detected.")
    duplicates = df["biosample_id"][df["biosample_id"].duplicated()]
    print(",".join(duplicates))
    print("-" * 50)

# Get target accessions
fastq_urls = {}
accessions = df["biosample_id"]
for acc in accessions:
    acc = str(acc).strip()
    # print(acc)

    # ENA query
    if acc.startswith(("SRR", "ERR", "DRR")):
        query = f"run_accession={acc}"
    elif acc.startswith("SRS"):
        query = f"secondary_sample_accession={acc}"
    else:
        query = f"sample_accession={acc}"

    url = (
        "https://www.ebi.ac.uk/ena/portal/api/search"
        "?result=read_run"
        f"&query={query}"
        "&fields=run_accession,fastq_ftp"
        "&format=json"
    )

    r = requests.get(url)
    rows = r.json()
    
    fastq_urls[acc] = []
    for row in rows:
        ftp_field = row.get("fastq_ftp", "")
        if ftp_field:
            for ftp in ftp_field.split(";"):
                fastq_urls[acc].append("https://" + ftp)

# Write URLs
with open(f"fastq_urls.tsv", "w") as f:
    for acc in fastq_urls.keys():
        for url in fastq_urls[acc]:
            f.write(df.loc[df["biosample_id"] == acc, "sample_id"].values[0] + "\t")
            f.write(df.loc[df["biosample_id"] == acc, "species"].values[0] + "\t")
            f.write(acc + "\t")
            f.write(url + "\n")

# Write report
with open(f"fastq_report.tsv", "w") as f:
    f.write("sample_id\tspecies\tbiosample_id\tfastq_num\n")
    for acc in fastq_urls.keys():
        f.write(df.loc[df["biosample_id"] == acc, "sample_id"].values[0] + "\t")
        f.write(df.loc[df["biosample_id"] == acc, "species"].values[0] + "\t")
        f.write(acc + "\t")
        f.write(f"{len(fastq_urls[acc])}" + "\n") 

# Useful info
print(f"Collected {sum([len(x) for x in fastq_urls.values()])} FASTQ URLs.")
print("-" * 50)