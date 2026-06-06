# 🛡️ Vigilant — Community Crime Awareness Platform

> **Location-based crime reporting, emergency SOS, community alerts, and AI-powered authority coordination — built entirely with Django.**

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python) ![Django](https://img.shields.io/badge/Django-5.0-green?logo=django) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql) ![Gemini AI](https://img.shields.io/badge/Gemini-AI-purple?logo=google) ![Render](https://img.shields.io/badge/Deployed_on-Render-46E3B7?logo=render)

---

## ✨ Features

| Feature | Description |
|---|---|
| 🗺️ **Interactive Crime Map** | Leaflet.js map showing all reports colour-coded by severity |
| 📢 **Community Reporting** | Citizens submit crime reports with GPS location, images, and details |
| 🆘 **Emergency SOS** | One-tap SOS button captures GPS and alerts authorities in real time |
| 🤖 **Gemini AI Analysis** | Auto-analyses every report — risk score, summary, recommendations |
| 📊 **Command Dashboard** | Charts for trends, categories, severity, top areas (Chart.js) |
| 🧠 **AI Insights** | Ask Gemini free-form questions about crime patterns in your database |
| 👮 **Authority Coordination** | Officers can manage SOS alerts, update statuses, add notes |
| 🔒 **Role-Based Access** | Citizen / Police Officer / Administrator roles |
| 👤 **Anonymous Reporting** | Option to submit reports without identity |

---

## 🏗️ Project Structure

```
vigilant/
├── vigilant/               # Django project settings & URLs
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/                   # User auth, profiles, home page
│   ├── models.py           # UserProfile (role, phone, badge)
│   ├── views.py            # Home, register, profile
│   └── forms.py
├── reports/                # Crime reporting module
│   ├── models.py           # CrimeReport, ReportComment
│   ├── views.py            # List, detail, submit, AI analysis
│   └── forms.py
├── emergency/              # SOS alerts module
│   ├── models.py           # SOSAlert, SafeZone
│   └── views.py            # SOS page, AJAX trigger, authority list
├── dashboard/              # Analytics and AI insights
│   └── views.py            # Stats, charts, Gemini AI query
├── templates/              # Django HTML templates
│   ├── base.html           # Navbar, footer, messages
│   ├── core/
│   ├── reports/
│   ├── emergency/
│   ├── dashboard/
│   └── registration/       # Login page
├── static/
│   ├── css/vigilant.css    # Full design system (dark tactical theme)
│   └── js/vigilant.js      # Maps, geolocation, SOS logic
├── requirements.txt
├── build.sh                # Render build script
├── render.yaml             # Render Blueprint (one-click deploy)
└── manage.py
```

---

## 🚀 Local Development Setup

### Prerequisites

- Python 3.11+
- PostgreSQL (or use SQLite for local dev)
- A [Gemini API key](https://aistudio.google.com/app/apikey) (free)

### Step 1 — Clone the project

```bash
git clone https://github.com/your-username/vigilant.git
cd vigilant
```

### Step 2 — Create a virtual environment

```bash
python -m venv venv

# Activate:
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in your values:

```env
SECRET_KEY=your-very-secret-django-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# For local dev with SQLite, comment out DATABASE_URL
# DATABASE_URL=postgresql://user:password@localhost:5432/vigilant_db

GEMINI_API_KEY=your-gemini-api-key
```

> **For local SQLite** (easiest): In `vigilant/settings.py`, temporarily change the DATABASES block to:
> ```python
> DATABASES = {
>     'default': {
>         'ENGINE': 'django.db.backends.sqlite3',
>         'NAME': BASE_DIR / 'db.sqlite3',
>     }
> }
> ```

### Step 5 — Run migrations

```bash
python manage.py migrate
```

### Step 6 — Create a superuser

```bash
python manage.py createsuperuser
```

### Step 7 — Run the development server

```bash
python manage.py runserver
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

---

## ☁️ Deployment on Render

### Prerequisites

- A [Render account](https://render.com) (free tier works)
- Your project pushed to a **GitHub repository**
- A Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

---

### Method A — Automatic with render.yaml (Recommended)

This is the fastest method. The `render.yaml` file in the project root defines both the web service and database automatically.

**Step 1** — Push your code to GitHub

```bash
git init
git add .
git commit -m "Initial commit — Vigilant Django app"
git remote add origin https://github.com/your-username/vigilant.git
git push -u origin main
```

**Step 2** — Connect to Render

1. Go to [render.com](https://render.com) and sign in
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub account and select your `vigilant` repository
4. Render will detect `render.yaml` and show you a preview of resources to create:
   - `vigilant` — Web Service (Python)
   - `vigilant-db` — PostgreSQL database (free)
5. Click **"Apply"**

**Step 3** — Add your Gemini API key

After services are created:
1. Go to your **vigilant** Web Service → **Environment**
2. Add: `GEMINI_API_KEY` = `your-key-here`
3. Click **Save Changes** — Render will auto-redeploy

**Step 4** — Create admin user

In your Vigilant Web Service dashboard:
1. Go to **Shell**
2. Run: `python manage.py createsuperuser`

**Done! 🎉** Your app is live at `https://vigilant.onrender.com`

---

### Method B — Manual Setup on Render

Follow these steps if you prefer to configure services yourself.

#### Step 1 — Create a PostgreSQL database

1. In Render dashboard → **"New +"** → **"PostgreSQL"**
2. Name: `vigilant-db`
3. Plan: **Free**
4. Click **"Create Database"**
5. Copy the **Internal Database URL** — you'll need it next

#### Step 2 — Create the Web Service

1. **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure:

| Field | Value |
|---|---|
| **Name** | `vigilant` |
| **Runtime** | `Python 3` |
| **Build Command** | `./build.sh` |
| **Start Command** | `gunicorn vigilant.wsgi:application` |
| **Plan** | Free |

#### Step 3 — Set Environment Variables

In the Web Service → **Environment** tab, add:

| Key | Value |
|---|---|
| `SECRET_KEY` | Click **"Generate"** — Render will create a secure random key |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `vigilant.onrender.com` (replace with your actual subdomain) |
| `DATABASE_URL` | Paste the **Internal Database URL** from Step 1 |
| `GEMINI_API_KEY` | Your key from [aistudio.google.com](https://aistudio.google.com/app/apikey) |

#### Step 4 — Deploy

Click **"Create Web Service"**. Render will:
1. Clone your repository
2. Run `./build.sh` → installs requirements, collects static files, runs migrations
3. Start the app with Gunicorn

Watch the build logs. When you see `Your service is live 🎉`, your app is deployed.

#### Step 5 — Create superuser

Go to the **Shell** tab in your Render service and run:

```bash
python manage.py createsuperuser
```

---

### Post-Deployment Checklist

After deployment, verify these steps:

- [ ] Visit `https://your-app.onrender.com` — home page loads
- [ ] Register a new account at `/register/`
- [ ] Submit a test crime report at `/reports/submit/`
- [ ] Check the crime map at `/reports/`
- [ ] Test the SOS page at `/emergency/`
- [ ] Visit `/dashboard/` — charts and stats display correctly
- [ ] Visit `/dashboard/ai-insights/` → click "Auto Analysis" — Gemini AI responds
- [ ] Log in to `/admin/` with your superuser credentials
- [ ] Add a Safe Zone in admin: Emergency → Safe Zones → Add

---

## 🔧 Admin Panel

Access Django admin at `/admin/` with your superuser account.

From admin you can:
- **Manage users** and assign roles (citizen, officer, admin)
- **Moderate crime reports** — update status, assign officers
- **Manage SOS alerts** — view all emergency alerts
- **Add Safe Zones** — police stations, hospitals, fire stations shown on SOS map
- **View AI analysis** on any report

---

## 🤖 Gemini AI Integration

Vigilant uses the **Gemini 2.0 Flash** model for three features:

| Feature | When it runs | What it produces |
|---|---|---|
| **Report Analysis** | When a new crime report is submitted | Risk score (1-100), summary, recommendations |
| **SOS Dispatch Note** | When an SOS alert is triggered | Professional dispatch note for first responders |
| **AI Insights** | When analyst clicks "Generate Analysis" | Crime patterns, hotspots, resource allocation advice |

The AI is **best-effort** — if the API key is missing or the call fails, the app continues to work normally without AI features.

To get a Gemini API key:
1. Go to [aistudio.google.com](https://aistudio.google.com/app/apikey)
2. Click **"Create API key"**
3. Copy it into your Render environment variables as `GEMINI_API_KEY`

---

## 🗺️ Map Configuration

The app uses **Leaflet.js** with **OpenStreetMap** tiles — no API key required. The map is styled dark using CSS filters to match the platform's tactical theme.

The default map center is **Nairobi, Kenya** (`-1.286389, 36.817223`). To change this, update the `defaultCenter` in `static/js/vigilant.js`:

```javascript
const defaultCenter = options.center || [-1.286389, 36.817223];
```

---

## 🔐 Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | ✅ Yes | Django secret key — keep private, minimum 50 chars |
| `DEBUG` | ✅ Yes | `False` in production, `True` locally |
| `ALLOWED_HOSTS` | ✅ Yes | Comma-separated allowed hostnames |
| `DATABASE_URL` | ✅ Yes | PostgreSQL connection string (Render auto-sets this) |
| `GEMINI_API_KEY` | ⚡ Optional | Enables AI features — get free at aistudio.google.com |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Django 5.0 (Python) |
| **Database** | PostgreSQL (via dj-database-url) |
| **Frontend** | Django Templates + Vanilla JS |
| **Styling** | Custom CSS (dark tactical design system) |
| **Maps** | Leaflet.js + OpenStreetMap |
| **Charts** | Chart.js 4 |
| **AI** | Google Gemini 2.0 Flash API |
| **Static Files** | WhiteNoise |
| **Web Server** | Gunicorn |
| **Deployment** | Render |

---

## 🐛 Troubleshooting

**Build fails with `./build.sh: Permission denied`**
```bash
git update-index --chmod=+x build.sh
git commit -m "Make build.sh executable"
git push
```

**`ModuleNotFoundError: No module named 'decouple'`**
Ensure `python-decouple` is in `requirements.txt` and the build ran successfully.

**Static files not loading (CSS/JS broken)**
- Confirm `DEBUG=False` and `ALLOWED_HOSTS` is set correctly
- Check that `build.sh` ran `collectstatic` without errors
- WhiteNoise must be before other middleware in `settings.py`

**Database errors / `relation does not exist`**
The `build.sh` runs `migrate` automatically. If you need to re-run:
- In Render Shell: `python manage.py migrate`

**Gemini AI returns no analysis**
- Verify `GEMINI_API_KEY` is set in Render Environment tab
- Check Render logs for API errors
- The app works without AI — only AI-specific features are disabled

**500 errors on Render**
- Check the Render **Logs** tab for the Python traceback
- Temporarily set `DEBUG=True` to see detailed errors (remember to revert)

---

## 📄 License

MIT License — free to use, modify, and deploy.

---

<div align="center">
  Built with Django · Powered by Gemini AI · Deployed on Render
</div>
