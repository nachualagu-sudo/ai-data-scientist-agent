# Viva Guide — AI Data Scientist Agent

## Explain the project in one sentence

“The AI Data Scientist Agent is a web application that accepts CSV or Excel datasets and performs summary analysis, data cleaning, visualization, statistical insights, machine-learning training, evaluation and prediction in one workflow.”

## Why did you choose this project?

Data-science beginners often run separate programs for loading, cleaning, visualization and modelling. This can cause inconsistent preprocessing and accidental use of older datasets. This application keeps the complete workflow together and uses the same current dataset and preprocessing pipeline at every stage.

## What are the main modules?

1. **Upload:** Accepts and validates CSV or XLSX files.
2. **Summary:** Shows rows, columns, data types, missing values, duplicates and descriptive statistics.
3. **Cleaning:** Removes duplicate rows, normalizes column names, and handles missing values.
4. **Visualization:** Creates histogram, bar, scatter, line, box and heatmap charts.
5. **Insights:** Calculates correlation, common categories and potential outliers.
6. **Machine Learning:** Trains regression or classification models based on a selected target.
7. **Prediction:** Uses the saved preprocessing and model pipeline to predict a new value.

## Common viva questions and answers

### Why did you use the median for numeric missing values?

The mean can change significantly when a column contains outliers. The median is more resistant to extreme values, so it is a safe general choice for filling missing numeric values.

### What is the mode?

The mode is the value that occurs most frequently in a column. I use it to fill missing categorical or text values. If no mode exists, the application uses `Unknown`.

### Why is a train-test split required?

The training set is used to teach the model. The test set contains unseen records and measures whether the model can generalize to new data. Evaluating the same records used for training can give a misleading score.

### Why did you use a Scikit-learn Pipeline?

The pipeline groups imputation, scaling, categorical encoding and the model. It guarantees that training and prediction apply exactly the same preprocessing steps and prevents inconsistent feature preparation.

### What is the difference between regression and classification?

Regression predicts a continuous numeric value, such as diamond price. Classification predicts a category, such as Fraud or Not Fraud.

### What is Linear Regression?

Linear Regression models a continuous target as a weighted linear combination of input features. It is useful as a simple and explainable baseline.

### What is Logistic Regression?

Logistic Regression is a classification algorithm. It estimates the probability of a class and is a useful baseline for categorical prediction tasks.

### Why did you use Random Forest?

Random Forest combines the results of many decision trees. It can learn nonlinear relationships and interactions between features and usually requires less feature tuning than a single linear model.

### What is one-hot encoding?

Machine-learning models require numeric inputs. One-hot encoding converts each category into binary indicator columns while avoiding an artificial numeric order between categories.

### What is R²?

R² is a regression metric that measures how much of the variation in the target is explained by the model. A value closer to 1 generally indicates a better fit on the test data.

### What is MAE?

Mean Absolute Error is the average absolute difference between actual and predicted values. It is expressed in the same unit as the target, and a lower value is better.

### What is RMSE?

Root Mean Squared Error gives more weight to large errors than MAE. It is useful when large prediction mistakes are especially important, and a lower value is better.

### What is accuracy?

Accuracy is the proportion of classification predictions that are correct. It may be misleading for imbalanced data, so the application also reports weighted F1.

### What is correlation?

Correlation measures the strength and direction of a linear relationship between two numeric variables. Values are between -1 and 1. Correlation does not prove causation.

### How does the application find potential outliers?

It uses the Interquartile Range method. Values below `Q1 - 1.5 × IQR` or above `Q3 + 1.5 × IQR` are marked as potential outliers for review.

### Does the application use an LLM?

The core application does not require an LLM. Insights are calculated locally with Pandas and NumPy. Therefore, the project needs no API key and consumes no language-model tokens during normal use.

### How did you reduce security risks?

The application limits file size, accepts only CSV and XLSX files, creates safe internal filenames, checks expanded Excel size, validates selected columns, escapes data displayed in the browser, sets browser security headers and supports password protection for deployment.

### What are the limitations?

This version is designed for a single-user educational demo. It stores one current dataset and one trained model. A multi-user production system would require user accounts, per-user storage, a database, background training jobs and stronger resource isolation.

## Recommended demonstration order

1. Upload `sample_data/diamonds_sample.csv`.
2. Show the row count, column types, missing values, duplicates and preview.
3. Click **Clean Dataset** and explain the before/after report.
4. Create a `price` histogram.
5. Create a scatter plot using `carat` as X and `price` as Y.
6. Create a correlation heatmap.
7. Open the Insights tab and explain correlation and possible outliers.
8. Select `price` as the target and Random Forest as the model.
9. Train the model and explain MAE, RMSE and R².
10. Enter sample diamond values and show the predicted price.

## Closing explanation

“This project demonstrates the complete data-science lifecycle: data ingestion, understanding, cleaning, exploratory analysis, model preparation, training, evaluation and prediction. The main design strength is that one validated dataset manager and one saved preprocessing pipeline keep every stage consistent.”
