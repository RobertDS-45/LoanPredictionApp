# LoanPredictionApp

A Django app for loan prediction with a responsive Bootstrap frontend.

## Project structure

- `LQS/` — Django project settings and WSGI configuration
- `User/` — app for user views, models, forms, templates, and static files
- `static/` — global CSS and assets
- `db.sqlite3` — local SQLite database used for development
- `requirements.txt` — Python dependencies

## Local setup

1. Clone the repository:
   ```bash
   git clone https://github.com/RobertDS-45/LoanPredictionApp.git
   cd LoanPredictionApp
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/Scripts/activate   # Windows PowerShell
   # or source venv/bin/activate  # Linux / macOS
   ```

3. Install dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Run database migrations:
   ```bash
   python manage.py migrate
   ```

5. Collect static files:
   ```bash
   python manage.py collectstatic
   ```

6. Start the development server:
   ```bash
   python manage.py runserver
   ```

7. Open the app in your browser:
   - `http://127.0.0.1:8000/`

## Render deployment

This project is configured for Render with:
- `Procfile`
- `runtime.txt`
- `gunicorn`
- `whitenoise`

### Render setup

1. Push your code to GitHub.
2. Create a new Render Web Service.
3. Connect to the `LoanPredictionApp` GitHub repository.
4. Set `Build Command` to:
   ```bash
   pip install -r requirements.txt && python manage.py collectstatic --no-input
   ```
5. Set `Start Command` to:
   ```bash
   gunicorn LQS.wsgi --log-file -
   ```
6. If you want, add these optional environment variables in Render:
   - `DJANGO_SECRET_KEY`
   - `DJANGO_ALLOWED_HOSTS=your-app-name.onrender.com`

### Notes for Render

- `ALLOWED_HOSTS` is preconfigured in `LQS/settings.py` for `loanpredictionapp-eaef.onrender.com`.
- SQLite is acceptable for a simple demo, but it is not ideal for production.
- If you need persistent production data later, use a managed PostgreSQL or other external database provider.

## Production preparation

Before production deployment:

- Set `DEBUG = False` in `LQS/settings.py`
- Set a strong `DJANGO_SECRET_KEY`
- Add your Render domain to `ALLOWED_HOSTS`
- Use `collectstatic` for static assets

## Useful commands

- Run checks:
  ```bash
  python manage.py check
  ```
- Create a superuser:
  ```bash
  python manage.py createsuperuser
  ```
- Open the Django shell:
  ```bash
  python manage.py shell
  ```
