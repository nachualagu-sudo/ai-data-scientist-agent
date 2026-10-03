# AI Data Scientist Agent — Project Report

## Abstract

The AI Data Scientist Agent is a web application for automated tabular-data analysis. A user can upload a CSV or Excel file, inspect its structure and quality, clean common data problems, create visualizations, receive statistical insights, train a regression or classification model, evaluate it on unseen test data, and make new predictions. The application demonstrates an end-to-end data-science workflow through a simple browser interface.

## Problem statement

Beginning data-science users often run separate scripts for loading, cleaning, visualizing and modelling data. This makes it easy to use stale files, apply inconsistent preprocessing, or evaluate a model incorrectly. The project combines these stages into one controlled workflow and ensures that training and prediction use the same preprocessing pipeline.

## Objectives

- Accept CSV and XLSX datasets through a web interface.
- Report rows, columns, types, missing values, duplicates and descriptive statistics.
- Remove duplicate rows and fill missing numeric and categorical values safely.
- Generate useful charts based on the selected column types.
- Produce statistical insights without requiring a paid AI API.
- Automatically support regression and classification tasks.
- Evaluate models using a held-out test set.
- Save the complete preprocessing and model pipeline for consistent prediction.

## System architecture

```text
Browser dashboard
       |
       v
FastAPI endpoints
       |
       +-- Dataset manager --> CSV/XLSX files
       +-- Analysis service --> Summary and insights
       +-- Cleaning service --> Cleaned dataset
       +-- Visualization service --> PNG charts
       +-- ML service --> Preprocessing + trained model
```

## Technology stack

| Layer | Technology |
| --- | --- |
| Programming language | Python 3.12 |
| Web backend | FastAPI, Uvicorn |
| Data processing | Pandas, NumPy |
| Visualization | Matplotlib, Seaborn |
| Machine learning | Scikit-learn |
| Frontend | HTML, CSS, JavaScript |
| Deployment | Docker, reverse proxy, HTTPS |

## Modules

### Dataset upload and management

The upload endpoint accepts only CSV and XLSX files, limits file size, creates a random internal filename, validates the content, and records the latest successful upload as the current dataset. All other modules retrieve data through the same dataset manager.

### Dataset summary

The summary provides shape, column names, data types, missing counts, duplicate count, numeric/categorical columns, descriptive statistics and a preview.

### Data cleaning

Duplicate rows are removed. Column names are normalized and made unique. Numeric missing values use the median because it is less sensitive to outliers than the mean. Text missing values use the mode, with `Unknown` as a safe fallback. The cleaned dataset becomes current and can be downloaded.

### Visualization

The application supports histogram, bar, scatter, line, box and correlation heatmap charts. Column types are checked before generating a chart. Chart files include the dataset identifier and a random suffix, preventing stale results from being reused.

### Statistical insights

The application reports dataset size, missing values, duplicates, strongest absolute numeric correlation, common categorical values and potential IQR outliers. These calculations run locally and do not consume language-model tokens.

### Machine learning

The user selects a target. The app detects likely regression or classification, separates numeric and categorical features, imputes missing values, scales numeric features, and one-hot encodes categories. Preprocessing and the estimator are stored in one Scikit-learn `Pipeline`.

The data is split into 80% training and 20% testing with a fixed random seed. Classification uses stratification when the class distribution permits it.

## Algorithms

| Task | Baseline | Advanced option |
| --- | --- | --- |
| Regression | Linear Regression | Random Forest Regressor |
| Classification | Logistic Regression | Random Forest Classifier |

Linear/Logistic Regression provides an explainable baseline. Random Forest captures nonlinear relationships and interactions. Comparing a baseline with a stronger model is more meaningful than selecting one algorithm without evaluation.

## Evaluation metrics

- **MAE:** average absolute prediction error; lower is better.
- **RMSE:** penalizes large regression errors more strongly; lower is better.
- **R²:** proportion of target variance explained; closer to 1 is better.
- **Accuracy:** fraction of correct classifications.
- **Weighted F1:** balances precision and recall while considering class frequency.

On the included 3,001-row diamond sample, the Random Forest regression workflow produced an R² of approximately **0.97** in the validation run. Results can vary with the dataset and selected features.

## Validation

- Python compilation completed successfully.
- Ruff static quality checks passed.
- Bandit source security scan passed with no reported issue.
- Dependency audit reported no known vulnerabilities for the required packages at validation time.
- Automated service and ML tests passed.
- The full API workflow passed: upload, summary, clean, cleaned-file download, visualization, insights, training and prediction.
- CSV and XLSX upload/cleaning paths were both verified.
- Uvicorn reached `Application startup complete`.

## Security and reliability controls

- Optional deployment username and password.
- Safe internal filenames and path traversal prevention.
- CSV/XLSX allowlist and request-size limit.
- Expanded Excel workbook limit to reduce decompression attacks.
- Escaped dataset values in the browser.
- Browser security headers.
- Server-side column and input validation.
- Training-row and chart-row limits to control memory use.

## Limitations

The application is designed as a single-user educational project. One current dataset and one current model are stored per running instance. A multi-user product would require accounts, per-user database records, object storage and background job processing.

## Future scope

- Per-user projects and saved analysis history.
- Automated model comparison and cross-validation.
- Explainability using feature importance or SHAP.
- Natural-language dataset chat as an optional module.
- Database and cloud object storage for production scale.
