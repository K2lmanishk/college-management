# College Management System (Django)

Roles: **admin**, **faculty**, **student** — users, subjects, attendance, marks, fees,
notices, online admission form, Twilio SMS helper.

## Setup

```bash
python -m venv venv
# Windows: venv\Scripts\activate      Mac/Linux: source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env        # (Windows: copy .env.example .env) then edit values

python manage.py migrate    # migrations are already included
python manage.py createsuperuser   # superusers automatically get the "admin" role
python manage.py runserver
```

Open http://127.0.0.1:8000/login/

## First steps after logging in as admin
1. Django Admin (`/django-admin/`) -> add **Programs**.
2. Use **Users** page to add faculty and students.
3. Use **Subjects** page to add subjects, then Django Admin -> **Faculty assignments** to link faculty to subjects.
4. Faculty can now mark attendance / enter marks. Fee records are added via Django Admin -> **Fees**.

## Notes
- Twilio credentials go in `.env` only. `communication/sms.py` exposes `send_sms(to, message)`.
- For production: set `DEBUG=False`, a real `SECRET_KEY`, `ALLOWED_HOSTS`, run `python manage.py collectstatic`, and serve with gunicorn.
