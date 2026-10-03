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

The included `render.yaml` runs a **free Render demo** with a 10 MB upload limit, 10,000 analysis rows, and 3,000 training rows. It has no persistent disk: uploaded datasets and trained models disappear when Render restarts or spins down the service. Use sample or non-sensitive data. See `RENDER_DEPLOYMENT.md`.

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
- The free demo limits uploads to 10 MB, analysis to the first 10,000 rows, and model training to 3,000 rows. Local backend defaults can be adjusted with environment variables; the included frontend is labeled for the free demo.
- The UI labels partial results. Metrics may not represent the full file if data order is biased.
- The free demo uses temporary storage. Back up anything you need; files and models are deleted on restart or spin-down.
- The app adds security headers, validates file types and filenames, limits upload size, and rejects oversized expanded Excel workbooks.
