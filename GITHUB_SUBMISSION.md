# GitHub submission guide

Submit `AI_Data_Scientist_Agent_Final.zip` to the class portal. Add the **real GitHub repository URL** in the portal's **Add Comments** box after publishing the project. A GitHub repository link shows the source code; it is not a live web application URL.

## Create the repository

1. Sign in to your own GitHub account and create a new repository named `ai-data-scientist-agent`. Select **Public** only if your tutor needs to open the link without GitHub access. Do not add a README, `.gitignore`, or license through the GitHub creation form; this project already has a README and `.gitignore`.
2. Open Terminal inside the **extracted** `AI_Data_Scientist_Agent_Final` folder. Check that `ls FastAPI_Main_Server.py requirements.txt` lists both files.
3. Run the following commands one line at a time. Replace `YOUR_GITHUB_USERNAME` with your account name:

```bash
git init
git add .
git status --short
git commit -m "Submit AI Data Scientist Agent final project"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/ai-data-scientist-agent.git
git push -u origin main
```

If Git asks for your identity before committing, set it with your own name and email:

```bash
git config user.name "Your Name"
git config user.email "your-email@example.com"
git commit -m "Submit AI Data Scientist Agent final project"
```

GitHub may ask you to sign in through your browser. Do not paste a password or access token into the class portal or project files.

4. Open your new repository in a browser. Confirm that `FastAPI_Main_Server.py`, `requirements.txt`, `README.md`, `PROJECT_REPORT.md`, `static/`, `api/`, `services/`, `sample_data/`, and `OUTPUT_PREVIEW.html` appear. Copy the browser URL of that repository. **Do not submit a guessed URL before the push succeeds.**

## Class portal

- Upload the single final ZIP file in **Upload your submission here**. The ZIP includes code, documentation, sample data, and the sample output preview.
- Paste this comment after replacing the URL with your working repository link:

> AI Data Scientist Agent is a Python/FastAPI data science web app. It uploads CSV/XLSX data, reports quality, cleans data, creates visualizations and insights, and trains regression/classification models for predictions. Source code and run instructions: https://github.com/YOUR_GITHUB_USERNAME/ai-data-scientist-agent

- Click **Submit** and confirm the submission appears under **Your Submissions**.

The app is currently runnable on the local computer. The GitHub source link will not open a running dashboard; a separate Python host and domain setup is required for a public app URL. See `RENDER_DEPLOYMENT.md` for that later deployment.
