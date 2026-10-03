# Deploy the free demo on Render

The `render.yaml` Blueprint creates one free Python web service. It runs the FastAPI backend and dashboard together. The service has no persistent disk or paid compute plan.

## Deploy

1. Connect the GitHub repository `nachualagu-sudo/ai-data-scientist-agent` to Render.
2. In Render choose **New → Blueprint**, select that repository, and review the proposed web service. Confirm that the plan is **Free** and no disk is listed.
3. Enter private `APP_USERNAME` and `APP_PASSWORD` values when Render prompts for them. The password must have at least 12 characters. Do not commit credentials to GitHub.
4. Deploy and wait for Render to show a successful status. Open its generated `onrender.com` URL and sign in.
5. Test `/health`, upload `sample_data/diamonds_sample.csv`, then run summary, cleaning, chart, insights, model training, and prediction.

The app limits uploads to 10 MB, reads at most 10,000 rows and 30 columns for analysis, and trains on at most 3,000 rows. The UI labels partial data. Very complex spreadsheets or models can still exceed a free service's memory; use the included small CSV for the class demo.

Render spins a free service down after 15 minutes of inactivity. It can take about a minute to wake up. Datasets, charts, and models stored on its temporary filesystem are lost when it restarts, redeploys, or spins down. Each new session should upload the dataset again. Do not upload private data to this shared educational demo.

The login protects the app from casual public access. The latest uploaded dataset is shared by everyone using that same login, so share it only with trusted reviewers.

Official references: [FastAPI deployment](https://render.com/docs/deploy-fastapi) and [free service limits](https://render.com/docs/free).
