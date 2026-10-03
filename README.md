# AI Data Scientist Agent

For the class portal ZIP upload and a GitHub source-code link, see [GITHUB_SUBMISSION.md](GITHUB_SUBMISSION.md). Open [OUTPUT_PREVIEW.html](OUTPUT_PREVIEW.html) locally to see actual sample output from the included diamonds dataset.

A complete educational web application that uploads CSV/XLSX datasets, summarizes data quality, cleans missing values and duplicates, creates charts, generates statistical insights, trains regression/classification models, evaluates them, and makes predictions.

## Why this version

The original prototype had duplicated current-dataset logic, Excel/CSV format mismatches, dashboard indentation errors, and incompatible prediction request formats. Version 2 keeps dataset state in one manager and serves the dashboard and API from one FastAPI process.

## Technology

- Python 3.12
- FastAPI and Uvicorn
- Pandas and NumPy
- Matplotlib and Seaborn
- Scikit-learn pipelines
- HTML, CSS and JavaScript frontend

No paid language model or API key is required. Statistical insights are generated locally, so normal app usage consumes no AI tokens.

For a public deployment, set `APP_USERNAME` and `APP_PASSWORD`. The browser will request these credentials before showing the app.

Hostinger Cloud/Web plans do not run Python applications. For a no-VPS deployment with large uploads, use the included **paid 2 GB Render service and persistent disk** and point the chosen Hostinger subdomain to Render. Review the charges before activating it. See `RENDER_DEPLOYMENT.md`.

## Run on macOS

```bash
cd AI_Data_Scientist_Agent_Final
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn FastAPI_Main_Server:app --reload --host 127.0.0.1 --port 8010
```

Open <http://127.0.0.1:8010>. API documentation is at <http://127.0.0.1:8010/docs>.

## Demo workflow

1. Upload `sample_data/diamonds_sample.csv`.
2. Review row count, column types, missing values and preview.
3. Clean the dataset and compare the report.
4. Create a histogram for `price`, scatter plot for `carat` vs `price`, and correlation heatmap.
5. Open Insights and explain correlation and outlier observations.
6. Train a regression model with target `price` and Random Forest.
7. Explain MAE, RMSE and R², then enter sample values and predict a price.

## ML model choices

| Need | Recommended model | Reason |
| --- | --- | --- |
| Baseline numeric prediction | Linear Regression | Easy to explain in a viva |
| Better numeric prediction | Random Forest Regressor | Captures nonlinear relationships |
| Baseline category prediction | Logistic Regression | Interpretable classification baseline |
| Better category prediction | Random Forest Classifier | Handles nonlinear patterns and mixed features |

The app automatically imputes numeric and categorical missing values and one-hot encodes categories inside the saved pipeline. The same pipeline is used for training and prediction.

## Important limits

- This is a single-user educational application. The latest uploaded dataset becomes current for the whole instance.
- Uploads are limited to 200 MB by default. Set `MAX_UPLOAD_MB` between 1 and 250 to change the limit.
- Analysis, cleaning, and ML use at most the first 50,000 rows; the UI labels partial results. The production Blueprint trains on at most 15,000 of those rows. Metrics are not representative of the full file if data order is biased.
- Files and trained models must be stored on a persistent volume when deployed in a container.
- The app adds security headers, validates file types and filenames, limits upload size, and rejects oversized expanded Excel workbooks.
