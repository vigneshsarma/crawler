CELERY_RESULT_BACKEND = "amqp"
BROKER_URL = "amqp://guest:guest@localhost:5672//"
CELERY_IMPORTS = ("crawler", )
