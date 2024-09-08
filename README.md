# How to start:

1. Clone the repository
2. Start postgresql server and configure .env file (DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
2. Run `pip install -r requirements.txt`
3. Run `alembic revision --autogenerate -m "Initial commit"`
4. Run `alembic upgrade head`
5. Run `python run.py`