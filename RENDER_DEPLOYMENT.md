# Deploy without a VPS — Render + Hostinger subdomain

Render runs the Python FastAPI application. Hostinger continues to manage the existing domain and its DNS records.

## Why this works

Render supports Python web services and its official FastAPI setup uses:

- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn FastAPI_Main_Server:app --host 0.0.0.0 --port $PORT --workers 1`

This project includes `render.yaml` and `.python-version`. The Blueprint selects Render's **paid 1c-2g web service (2 GB RAM)** and a **paid 5 GB persistent disk**. Review the charges in Render before creating it. These resources are selected for files around 143 MB; a 512 MB free service is not a supported large-file deployment. No deployment or charge occurs merely by downloading the project.

## Step 1 — Put the project on GitHub

Create an empty GitHub repository named `ai-data-scientist-agent`. Open Terminal inside the extracted project folder and run:

```bash
git init
git add .
git commit -m "Initial AI Data Scientist Agent"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ai-data-scientist-agent.git
git push -u origin main
```

Replace `YOUR_USERNAME` with the GitHub username.

## Step 2 — Create the Render service

1. Sign in at <https://dashboard.render.com/> using GitHub.
2. Select **New → Blueprint**.
3. Connect the `ai-data-scientist-agent` repository.
4. Render reads `render.yaml` and shows one Python web service.
5. Enter secure values when it requests the environment variables:
   - `APP_USERNAME`: the login name for the project.
   - `APP_PASSWORD`: a password containing at least 12 characters.
6. Create the service and wait for the deploy to finish.
7. Open the generated `onrender.com` URL and test the login, upload and model workflow.

Set `APP_USERNAME` and `APP_PASSWORD` only in the Render secret prompts, never in GitHub. `APP_ENV=production` requires both credentials at startup. Keep one instance/worker. Upload data is private to this one shared login, so use a separate account or service for unrelated people.

## Step 3 — Connect a Hostinger subdomain

Example subdomain: `datascience.yourdomain.com`

1. In the Render service, open **Settings → Custom Domains**.
2. Click **Add Custom Domain** and enter the full subdomain.
3. Render displays the required DNS target.
4. Open Hostinger hPanel → **Domains → DNS / Nameservers**.
5. Add the CNAME record supplied by Render. It normally has this structure:

| DNS field | Example |
| --- | --- |
| Type | CNAME |
| Name | datascience |
| Target | your-service.onrender.com |
| TTL | Default |

6. Remove a conflicting record for the same subdomain, if one exists. Render also recommends removing conflicting `AAAA` records while configuring the domain.
7. Return to Render and click **Verify**.
8. Render automatically provisions HTTPS after verification.

Use the exact target displayed in the Render dashboard instead of copying the example target above.

## Large-file behaviour and limits

Uploads accept CSV/XLSX up to 200 MiB. For datasets exceeding 50,000 rows, analysis, cleaning, charts, and ML work on the first 50,000 rows, and the UI labels the results as partial. The original upload remains available internally for training the raw sample; the cleaned download contains the sampled rows. ML trains on at most 15,000 rows and one request at a time is recommended. Very wide or unusually complex Excel workbooks can still need more memory or time; test the actual file before presenting. The application is a single-user educational tool, not an unrestricted multi-user data platform.

The persistent disk retains the current dataset and model across restarts. Keep a backup of important source files elsewhere; Render disks are not an independent backup.

## Final verification

Test these in order after deployment:

1. `/health`
2. Dashboard login
3. CSV upload
4. Dataset summary
5. Cleaning and download
6. Chart generation
7. Insights
8. Model training
9. Prediction

For a cross-site request protection check, a POST from another origin should return 403. Verify that an unauthenticated dashboard/API request returns 401 and that credentials are never committed to the repository.

Official references:

- <https://render.com/docs/deploy-fastapi>
- <https://render.com/docs/free>
- <https://render.com/docs/custom-domains>
