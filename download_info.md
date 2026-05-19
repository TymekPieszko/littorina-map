## Download instructions for *Littorina* sequence collection

Questions: t.pieszko@ucl.ac.uk

Download the `get_fastq_urls.py` script:

```
wget 
```

You can filter the download by categorical columns (i.e., not 'Timestamp', 'Latitude', 'Longitude') and request multiple categories as a comma-delimited list.

```
# Fetch URLs
python get_fastq_urls.py \
--sheet_url paste-url-here \
--project_id NRS --species saxatilis,arcana --sequence_type WGS_single_individual
```

This writes a file with all the target URLs. You can download into a new directory as:

```bash
mkdir fastq
cd ./fastq

while IFS=$'\t' read -r biosample_id species url; do

    filename=$(basename "$url")

    wget -O "${biosample_id}.${species}.${filename}" "$url"

done < ../fastq_urls.txt
```