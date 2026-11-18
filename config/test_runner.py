from django.apps import apps
from django.test.runner import DiscoverRunner


class ManagedModelTestRunner(DiscoverRunner):
    def setup_test_environment(self, **kwargs):
        super().setup_test_environment(**kwargs)
        self.unmanaged = [m for m in apps.get_models() if not m._meta.managed]
        for m in self.unmanaged:
            m._meta.managed = True

    def teardown_test_environment(self, **kwargs):
        for m in self.unmanaged:
            m._meta.managed = False
        super().teardown_test_environment(**kwargs)