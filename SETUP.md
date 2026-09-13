# Setup guide

## Standalone portfolio analysis

Install Python 3.12, extract the full repository and open a terminal in its folder.

```console
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python analyze.py
```

On macOS/Linux, use `.venv/bin/python` instead of `.venv\Scripts\python`.
The analysis produces reports, chart and CSV summaries in `reports/` without starting a server.

## Interactive preview

On Windows, double-click `run.bat`. First launch installs dependencies and needs internet. Keep the terminal open while viewing the dashboard. Stop it with Ctrl+C.

Alternatively:

```console
.venv\Scripts\python -m streamlit run app.py
```

Open the local URL printed in the terminal, normally http://localhost:8501.

## Choose a season

The sidebar has navigation and a single Season dropdown. It defaults to the latest bundled season, 2024. Choosing another season updates all analytics. Open Season Winner to see the champion photo and final details; no other page or sidebar shows that photo. Open Player Comparison to choose Batting or Bowling and compare two distinct players in the same season.

The previous dataset-upload feature, match-team filter, source summary, visible credits and technical footer have been removed. Data and photo attribution remain in README.md. No user-supplied screenshots are included in the repository.

## Data and images

Keep `data/matches.csv` and `data/deliveries.csv` together. Paths are relative to the Python files, so there are no machine-specific paths to edit. Photos are loaded directly from the URLs in `champion_photos.py`; internet is required for photos. The winner text and statistics still work without an image connection.

To replace the data, use a compatible CSV pair in the data folder and restart the dashboard to clear its cache. `python download_data.py` can re-fetch the source. Updated data may require new season photo mappings, snapshot test expectations and regenerated README findings.

## Tests

```console
.venv\Scripts\python -m unittest -v test_analytics.py
```

See README.md for metric definitions, limitations, data provenance and sources.
