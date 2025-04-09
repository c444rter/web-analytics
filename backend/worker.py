# backend/worker.py

import os
from rq import Worker, Queue, Connection
from core.redis_client import redis_client

listen = ['default']

if __name__ == '__main__':
    with Connection(redis_client):
        worker = Worker(list(map(Queue, listen)))
        worker.work()
