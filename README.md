opps-videos
===========

Video Application for Opps


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

Install the opps-videos lib:
```
python setup.py install
```

or
```
pip install opps-videos
```


Configuration
-------------

Include opps.videos on your django settings

```python
INSTALLED_APPS += (
    'opps.videos'
)
```

Add TemporaryFileUploadHandler as the default upload file handler
```python
FILE_UPLOAD_HANDLERS = (
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
)
```

Create DB tables:
```
python manage.py syndb
```

License
=======

Copyright 2013 `YACOWS <http://yacows.com.br/>`_. and other contributors
