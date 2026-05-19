## Download instructions for *Littorina* sequence collection

Contact: t.pieszko@ucl.ac.uk

Download the `get_fastq_urls.py` script:

```bash
wget https://raw.githubusercontent.com/TymekPieszko/littorina-seq/main/get_fastq_urls.py
```

The only required argument is `--sheet_url` - just paste the Google Docs URL! You can filter the dataset by categorical columns (i.e., not 'Timestamp', 'Latitude', 'Longitude' or 'Targeted_coverage') and request multiple categories (comma-delimited).

```
# Fetch URLs
python get_fastq_urls.py \
--sheet_url paste-url-here \
--project_id NRS --species saxatilis,arcana --sequence_type WGS_single_individual
```

The script writes a file with all the target URLs. You can download FASTQ files into a new directory as:

```bash
mkdir fastq
cd ./fastq

while IFS=$'\t' read -r biosample_id species url; do

    filename=$(basename "$url")

    wget -O "${biosample_id}.${species}.${filename}" "$url"

done < ../fastq_urls.txt
```