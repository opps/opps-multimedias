
opps-multimedias
================
[![Build
Status](https://travis-ci.org/opps/opps-multimedias.png?branch=master)](https://travis-ci.org/opps/opps-multimedias)


Multimedia Application for Opps


Requirements
-------------

Linux: FFVideo

Python: Opps, ffvideo



Installation
-------------

Install FFVideo dependencies:
```
sudo apt-get install python-dev cython libavcodec-dev libavformat-dev libswscale-dev
```

Install Celery dependencies:
```
sudo apt-get install rabbitmq-server
```

Install UOL Mais lib:
```
pip install -e git+git@github.com:YACOWS/Multimedia-UOLMais.git#egg=uolmais-api
```

Install the opps-multimedias lib:
```
python setup.py install
```

or
```
pip install opps-multimedias
```


Configuration
-------------

Include opps.multimedias and djcelery on your django settings
```python
INSTALLED_APPS += (
    'opps.multimedias',
    'djcelery',
)
```

Add celery configuration
```python
import djcelery
djcelery.setup_loader()
BROKER_URL = 'amqp://guest@localhost:5672'
```

Add TemporaryFileUploadHandler as the default upload file handler
```python
FILE_UPLOAD_HANDLERS = (
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
)
```

Add Youtube and UOL Mais credentials:
```python

YOUTUBE_AUTH_EMAIL = 'sergio@tracy.com.br'
YOUTUBE_AUTH_PASSWORD = 'this is my password'
YOUTUBE_DEVELOPER_KEY = 'AI39si4JXaQthEfdVoTjpgJ5hWhK5JFgz-lkaTquXGYl8P-QLKUiwEEFasdiouIKJHDhsjk823KJKsohvBPaYPQ'

UOLMAIS_USERNAME = 'sergio@tracy.com.br'
UOLMAIS_PASSWORD = 'this is my password'

```


Create DB tables:
```
python manage.py syncdb
```


Final Notes
=============

This Django App fully relies on Django Celery tasks. To get all it's features 
working properly make sure celery is running with events and beat activated. 

To start it use the following command:
```
python src/manage.py celery worker --loglevel=error --events --beat
```

To get tasks information on Django Admin UI you will also need to activate celerycam. 
```
python src/manage.py celerycam
```

To avoid memory leaks ensure that settings.DEBUG is set to False.


License
=======

Copyright 2013 `YACOWS <http://yacows.com.br/>`_. and other contributors
