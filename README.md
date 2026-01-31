# Blood Donation System

A web app to connect blood donors, receivers, and hospitals with location-based matching and request management.

## Features
- Donor, receiver, and hospital registration/login
- Location selection with Google Maps
- Request sending, acceptance, and rejection workflow
- Email notification on request acceptance
- Distance calculation using Haversine formula

## Tech Stack
- **Backend:** Flask, SQLite, Flask-Mail
- **Frontend:** HTML/CSS/JavaScript

## Project Structure
```
backend/
  app.py
  requirements.txt
  schema.sql
frontend/
  index.html
  login.html
  signup_donor.html
  signup_receiver.html
  signup_hospital.html
  dashboard_donor.html
  dashboard_receiver.html
  dashboard_hospital.html
static/
  (images, css, js)
```

## Prerequisites
- Python 3.10+
- Google Maps API key (for signup pages)
- SMTP credentials (for email notifications)

## Environment Variables
Create a `.env` file at the project root:
```
FLASK_SECRET_KEY=your_secret_key
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
PORT=8081
```

> `.env` is ignored by git. See `.env.example` for reference.

## Setup
```bash
# from project root
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r backend/requirements.txt
```

## Run
```bash
python backend/app.py
```
Open http://localhost:8081

## Deployment Notes
- Set the same environment variables in your hosting platform.
- Never commit real API keys or passwords.

## License
MIT
