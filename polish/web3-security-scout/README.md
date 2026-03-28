# AI PR Reviewer

Autonomous GitHub Pull Request reviewer with HMAC verification and rate limiting.

## Features

- Receives GitHub `pull_request` webhooks
- Validates HMAC signatures using `GITHUB_WEBHOOK_SECRET`
- Rate limits requests per IP (configurable)
- Health endpoint (`/health`) for monitoring
- Ready for deployment behind Nginx

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment
export GITHUB_WEBHOOK_SECRET="your-secret"
export REVIEW_RATE_LIMIT="10"   # requests per minute

# Run locally
python webhook.py
```

## Deployment

### Systemd service

Create `/etc/systemd/system/web3-security-scout.service`:

```ini
[Unit]
Description=AI PR Reviewer
After=network.target

[Service]
Type=simple
WorkingDirectory=/path/to/web3-security-scout
Environment="GITHUB_WEBHOOK_SECRET=your-secret"
ExecStart=/usr/bin/python3 /path/to/web3-security-scout/webhook.py
Restart=on-failure
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now web3-security-scout
```

### Nginx reverse proxy

Add site config:

```nginx
server {
    listen 80;
    server_name pr.207.180.223.192.nip.io;

    location / {
        proxy_pass http://127.0.0.1:8081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Reload Nginx.

### GitHub webhook configuration

In your repository settings → Webhooks → Add webhook:

- Payload URL: `http://pr.207.180.223.192.nip.io/hooks/github`
- Content type: `application/json`
- Secret: the same as `GITHUB_WEBHOOK_SECRET`
- Events: “Pull requests”

## Testing

Run pytest:
```bash
pytest tests/test_webhook.py
```

The tests cover HMAC validation and rate limiting.

## Next Steps

- Integrate with xander-operator to actually analyze PRs (fetch diff, LLM synthesis)
- Add persistent task storage
- Add HTTPS (Let’s Encrypt)
- Add logging to file
