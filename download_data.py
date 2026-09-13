"""Re-download the two public Kaggle CSV files, independent of working directory."""
import io
import zipfile
import urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parent
import pandas as pd

URL = 'https://www.kaggle.com/api/v1/datasets/download/patrickb1912/ipl-complete-dataset-20082020'


def main():
    try:
        request = urllib.request.Request(URL, headers={'User-Agent': 'IPL-Analytics/1.0'})
        with urllib.request.urlopen(request, timeout=120) as response:
            payload = response.read()
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            files = {name: archive.read(name) for name in ['matches.csv', 'deliveries.csv']}
        matches = pd.read_csv(io.BytesIO(files['matches.csv']))
        deliveries = pd.read_csv(io.BytesIO(files['deliveries.csv']))
        if matches.empty or deliveries.empty or not deliveries.match_id.isin(matches.id).all():
            raise ValueError('Downloaded CSV files are empty or do not match.')
        destination = ROOT / 'data'
        destination.mkdir(exist_ok=True)
        for name, content in files.items():
            temporary = destination / (name + '.tmp')
            temporary.write_bytes(content)
            temporary.replace(destination / name)
        print('Downloaded and validated matches.csv and deliveries.csv from Kaggle.')
    except Exception as exc:
        raise SystemExit(f'Download failed: {exc}\nUse the bundled files or download the CSV pair from the Kaggle page in README.md.') from exc


if __name__ == '__main__':
    main()
