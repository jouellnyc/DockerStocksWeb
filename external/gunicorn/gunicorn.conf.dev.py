workers = 4
bind = "0.0.0.0:8000"
access_log_format = '%({X-Forwarded-For}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
loglevel = 'debug'
capture_output = True
errorlog  = '/tmp/stocks.error.log'
accesslog = '/tmp/stocks.access.log'

