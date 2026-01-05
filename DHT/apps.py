from django.apps import AppConfig

class DhtConfig(AppConfig):
    name = 'DHT'

    def ready(self):
        import DHT.signals
