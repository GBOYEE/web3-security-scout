<task type="auto">
<name>Update dashboard queries to match current operator schema</name>
<files> app.py queries.sql </files>
<action>
- Inspect xander-operator tasks.db schema (params, next_action)
- Update Streamlit queries to read latest task fields
- Add simple HTTP basic auth config
- Deploy behind nginx with password protection
</action>
<verify>
- Dashboard loads and displays tasks from operator DB
- Auth prompt appears in browser
</verify>
<done>Dashboard functional and secured</done>
</task>
