<task type="auto">
<name>Polish portfolio site: meta tags, favicon, screenshots</name>
<files> index.html assets/ </files>
<action>
- Add Open Graph and Twitter Card meta tags
- Generate favicon (SVG) and link in head
- Take three project screenshots (Xander, OpenClaw, PR Reviewer) and place in assets/
- Update project links to point to correct repos
- Verify mobile layout via Chrome devtools
</action>
<verify>
- curl https://207.180.223.192.nip.io/portfolio/ contains og:title and og:image
- /favicon.ico returns image
- Screenshots display correctly on page
</verify>
<done>Portfolio polished and SEO-ready</done>
</task>
