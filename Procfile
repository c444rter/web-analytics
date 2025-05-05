web: cd backend && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
worker: cd backend && rq worker --with-scheduler --url ${REDIS_PUBLIC_URL} --name worker-${RAILWAY_SERVICE_ID:-local} --verbose --worker-ttl 3600 --job-timeout 3600 --burst-delay 1 --max-jobs 0
release: cd /app && PYTHONPATH=. alembic current && PYTHONPATH=. alembic upgrade head
