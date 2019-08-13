from django.test import TransactionTestCase
from django.urls import reverse

from ports.models import Dependency, Port, BuildHistory, Builder
from MacPorts.config import TEST_PORTINDEX_JSON, BUILDS_FETCHED_COUNT


class TestDependencies(TransactionTestCase):
    reset_sequences = True

    def test_loading_builders(self):
        BuildHistory.populate_builders()

        loaded = False
        if Builder.objects.count() >= 11:
            loaded = True
        self.assertEquals(loaded, True)

    def test_fetch_and_filter_buildhistory(self):
        Builder.objects.create(name='10.14_x86_64')
        BuildHistory.populate()
        buildhistory_object = BuildHistory.objects.get(id=1)
        port_name = buildhistory_object.port_name

        response1 = self.client.get(reverse('all_builds'))
        response2 = self.client.get(reverse('all_builds_filter'), data={
            'port_name': port_name
        })

        self.assertEquals(BuildHistory.objects.count(), BUILDS_FETCHED_COUNT)

        self.assertEquals(len(response1.context['builders']), 1)

        filter_works = False
        for i in response2.context['builds']:
            if i.port_name == port_name:
                filter_works = True
            else:
                filter_works = False

        self.assertEquals(filter_works, True)
