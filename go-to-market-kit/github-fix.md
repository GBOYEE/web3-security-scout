# Fix GitHub Push Issues (Permanent)

## Problem
Intermittent push failures (`gh failed: Unknown JSON field`, 500/502 errors, token expiry).

## Root Cause
- Token authentication instability
- Credential helper caching old tokens
- Missing scopes on PAT
- Using HTTPS with token vs SSH

## Permanent Fix: Use SSH (Recommended)

### 1. Generate SSH key (if you don’t have one)
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
# Press Enter for default location (~/.ssh/id_ed25519)
# Optionally set passphrase (recommended)
```

### 2. Add SSH key to GitHub
```bash
cat ~/.ssh/id_ed25519.pub
```
Copy output → GitHub → Settings → SSH and GPG keys → New SSH key → paste

### 3. Switch repo remotes to SSH
```bash
cd /root/.openclaw/workspace
git remote set-url origin git@github.com:GBOYEE/web3-security-scout.git
# Verify:
git remote -v
```

### 4. Test push
```bash
git add . && git commit -m "test ssh" && git push origin main
```
Should succeed without prompts.

## Alternative: Use PAT with proper scopes

If you prefer HTTPS:

1. Create PAT with scopes: `repo`, `workflow`, `read:org`, `gist`
2. Update remote with token (once):
```bash
git remote set-url origin https://YOUR_TOKEN@github.com/GBOYEE/web3-security-scout.git
```
3. Or configure credential helper:
```bash
git config --global credential.helper store
```
Then push once and enter credentials.

## Cleanup old credentials (if needed)
```bash
git config --global --unset credential.helper
rm -f ~/.git-credentials
```

## Verify GitHub auth
```bash
gh auth status
```
Should show `Logged in to github.com` and `account: GBOYEE`.

---

**Bottom line:** SSH is the most reliable. Set it once and forget it.
