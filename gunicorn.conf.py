import multiprocessing
import os

# Railway sets PORT dynamically; fall back to 8000 for local dev
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
workers = min(multiprocessing.cpu_count() * 2 + 1, 4)  # Cap at 4 for Railway memory limits
worker_class = "uvicorn.workers.UvicornWorker"
max_requests = 1000
max_requests_jitter = 50
timeout = 120
keepalive = 5
accesslog = "-"
errorlog = "-"
loglevel = "info"
forwarded_allow_ips = "*"
