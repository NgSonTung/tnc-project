# import multiprocessing

# bind = "0.0.0.0:5000"

# workers = 1

# Maximum number of simultaneous clients supported by each worker
worker_connections = 1000

# Enable graceful restarts and reloading of workers
preload_app = True
max_requests = 1000
max_requests_jitter = 50

# Set the timeout for handling requests (adjust based on your application's needs)
timeout = 300


# Set the maximum request header size (adjust if needed)
limit_request_line = 4094

# Enable support for the X-Forwarded-For header when running behind a reverse proxy
forwarded_allow_ips = "*"

raw_env = ["FLASK_ENV=production"]

threads = 2
