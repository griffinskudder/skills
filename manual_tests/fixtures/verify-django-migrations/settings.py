SECRET_KEY = "local-order-migration-fixture"
INSTALLED_APPS = ["orders"]
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
USE_I18N = False
