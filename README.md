# Tkinter Honeypot Project (Frontend + Backend)
This project provides a **desktop GUI (Tkinter)** that controls a low-interaction honeypot backend.
It includes:
- `backend_app.py` : the honeypot server (SSH/HTTP/FTP on 2222/8080/2121)
- `gui.py` : Tkinter GUI to start/stop the honeypot, view logs, and a fake login trap
- `logs/connections.csv` : captured connections
- `logs/credentials.csv` : fake login captures (for demo)
- Reference to original synopsis: /mnt/data/normal format cns synopsis.docx

## Quick start (Windows)
1. Ensure Python 3.8+ is installed.
2. Open PowerShell and `cd` into the project folder.
3. Run:
```
python gui.py
```
4. Use GUI buttons: Start Honeypot, then switch to Logs tab to view activity. Use Fake Login tab to simulate captured credentials.

## Notes
- This is intentionally low-interaction and safe for lab demo.
- Do **NOT** deploy this on a public-facing server in production.
