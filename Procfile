web: cd backend && uvicorn main:app --host 0.0.0.0 --port 8000
worker: rq worker --with-scheduler --url redis://default:WmfTavIVEnHSxGgrjKDPkIWuFwGeDjwp@interchange.proxy.rlwy.net:35531 --name worker-${DYNO} --verbose --worker-ttl 3600 --job-timeout 3600 --burst-delay 1 --max-jobs 0
