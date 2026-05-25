import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

try:
    from celery import Celery
    
    app = Celery('core')
    app.config_from_object('django.conf:settings', namespace='CELERY')
    app.autodiscover_tasks()
except ImportError:
    # Celery not installed - create a mock app for development
    class MockCeleryApp:
        def task(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
        
        def autodiscover_tasks(self):
            pass
    
    app = MockCeleryApp()