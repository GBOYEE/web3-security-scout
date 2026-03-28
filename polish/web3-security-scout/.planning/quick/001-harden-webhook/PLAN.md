<task type="auto">
<name>Harden PR reviewer webhook: signature verification and rate limiting</name>
<files> webapp/main.py requirements.txt </files>
<action>
- Add HMAC signature verification using GitHub secret
- Add rate limiting (e.g., 10 req/min per IP) using slowapi
- Write tests for signature validation and rate limit
- Update README with deployment instructions
</action>
<verify>
- Unit tests pass
- Manual test: invalid signature returns 401
- Manual test: exceeding rate limit returns 429
</verify>
<done>Webhook secure and production-ready</done>
</task>
