# Deployment guide

## Hostinger Cloud Professional limitation

Hostinger's current official documentation states that Python applications are supported exclusively on VPS Hosting because Web and Cloud plans do not provide the required root access. Therefore, a Cloud Professional plan can manage the domain/subdomain and DNS, but it cannot run this FastAPI application itself.

Available deployment paths:

1. Run the included Docker application on a Hostinger VPS and point the subdomain to that VPS.
2. Run it on another managed Python/container platform and point the Hostinger DNS record to that platform.
3. Keep the Cloud Professional plan for the main website while using a separate Python host for this project.

For the no-VPS deployment with 143 MB uploads, follow `RENDER_DEPLOYMENT.md`. It uses paid Render compute and disk; review charges before creating the Blueprint.

Official reference: <https://www.hostinger.com/support/which-programming-languages-and-frameworks-are-supported-at-hostinger/>

## Docker deployment

The application runs as one web process and stores uploaded datasets, charts and the trained model under `/app/data`.

```bash
docker compose up -d --build
```

The app listens on port `8010`. Put Nginx or the hosting platform's reverse proxy in front of it, enable HTTPS, and connect the chosen subdomain to the server.

Example Nginx site:

```nginx
server {
    listen 80;
    server_name datasci.example.com;
    client_max_body_size 210M;

    location / {
        proxy_pass http://127.0.0.1:8010;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Use Certbot or the hosting control panel to enable SSL after DNS points to the server.

## Managed Python platform

Use:

- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn FastAPI_Main_Server:app --host 0.0.0.0 --port $PORT --workers 1`
- Python version: `3.12`
- Persistent disk path: `/app/data` or set `APP_DATA_DIR` to the platform's persistent path
- Environment variables: set strong values for `APP_USERNAME` and `APP_PASSWORD`

Do not run multiple workers with this educational single-current-dataset design because the current dataset and model are file-backed.

## Subdomain checklist

1. Create a subdomain such as `datascience.example.com` in the hosting control panel.
2. If using a VPS, point its A record to the server IP; if using Render, add the CNAME target shown by Render.
3. For a VPS only, configure the reverse proxy to port `8010`.
4. Enable SSL/HTTPS.
5. Add `APP_USERNAME` and a strong `APP_PASSWORD` before making the app public.
6. Confirm `/health`, the dashboard, file upload, cleaning, chart creation and model prediction.
