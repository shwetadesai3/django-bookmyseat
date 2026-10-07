
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bookmyseat.settings")

import django
django.setup()

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
app = application
