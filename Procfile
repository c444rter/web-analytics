web: cd backend && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
worker: cd backend && rq worker --with-scheduler --url ${REDIS_URL:-redis://${REDISUSER:-default}:${REDISPASSWORD}@${REDISHOST:-localhost}:${REDISPORT:-6379}} --name worker-${RAILWAY_SERVICE_ID:-local} --verbose --worker-ttl 3600 --results-ttl 3600 --max-jobs 0 default
# Migrations are completely bypassed for this deployment since the database tables already exist
# release: cd /app && PYTHONPATH=. alembic stamp head && PYTHONPATH=. alembic upgrade head
