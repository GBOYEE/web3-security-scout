<task type="auto">
<name>Deploy OpenClaw gateway (FastAPI) behind Nginx</name>
<files> /etc/systemd/system/openclaw.service /etc/nginx/sites-available/openclaw </files>
<action>
- Write FastAPI app with rate limiting, HMAC validation, health endpoint
- Create systemd service to run it on port 8080
- Configure Nginx to proxy / to 127.0.0.1:8080 with SSL
- Reload systemd and nginx; verify HTTPS endpoint returns 200
</action>
<verify>
curl -k https://localhost/health returns {"status":"ok"}
</verify>
<done>Gateway deployed and responding</done>
</task>
