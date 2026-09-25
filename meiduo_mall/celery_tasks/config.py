# 配置信息 key = value
# 我们指定redis为我们的broker（中间人，经纪人，队列）
broker_url= 'redis://127.0.0.1:6379/15'

# Python 3.14's multiprocessing startup can leave Celery's prefork fast-trace
# context uninitialized in worker children. The solo pool runs tasks in the
# worker process and avoids that failure in this local development setup.
worker_pool = 'solo'
