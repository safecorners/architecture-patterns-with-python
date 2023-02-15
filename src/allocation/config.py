import os


def get_postgres_uri():
    host = os.environ.get("DB_HOST", "localhost")
    user = os.environ.get("DB_USER", "allocation")
    password = os.environ.get("DB_PASSSWORD", "allocation")
    port = os.environ.get("DB_PORT", 5432)
    db_name = os.environ.get("DB_NAME", "allocation")
    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"


def get_api_url():
    host = os.environ.get("API_HOST", "localhost")
    port = 5005 if host == "localhost" else 80
    return f"http://{host}:{port}"
