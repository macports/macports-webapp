from datetime import datetime, timezone

from django.test import TransactionTestCase, Client
from django.urls import reverse
from rest_framework.test import APIClient

from buildhistory.models import Builder, BuildHistory, InstalledFile


def set_initial_builds_data():
    # add a builder
    builder = Builder.objects.create(
        name="10.15_x86_64",
        display_name="10.15",
        natural_name="Catalina"
    )

    # add three builds
    BuildHistory.objects.create(
        builder_name=builder,
        build_id=1,
        status="build successful",
        port_name="port-A1",
        time_start=datetime.now(timezone.utc),
        time_elapsed=None,
        watcher_id=1
    )

    BuildHistory.objects.create(
        builder_name=builder,
        build_id=2,
        status="failed install-port",
        port_name="port-A1",
        time_start=datetime.now(timezone.utc),
        time_elapsed=None,
        watcher_id=1
    )

    BuildHistory.objects.create(
        builder_name=builder,
        build_id=3,
        status="failed install-dependencies",
        port_name="port-A2",
        time_start=datetime.now(timezone.utc),
        time_elapsed=None,
        watcher_id=1
    )


class TestURLsBuilds(TransactionTestCase):
    reset_sequences = True

    def test_all_builds(self):
        response = self.client.get(reverse('all_builds'))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='buildhistory/all_builds.html')

    def test_old_url_redirect(self):
        response = self.client.get(reverse('all_build_old'))

        self.assertRedirects(response, reverse('all_builds'), status_code=302, target_status_code=200)


class TestBuildbotFetch(TransactionTestCase):
    # this is a dynamic test case and depends on being able to fetch buildhistory from buildbot
    def test_buildbot_loading(self):
        # add a builder, add latest one
        Builder.objects.create(
            name="10.15_x86_64",
            display_name="10.15",
            natural_name="Catalina"
        )

        # try to fetch some build history
        BuildHistory.populate()

        self.assertEquals(BuildHistory.objects.all().count(), 5)
        self.assertEquals(Builder.objects.all().count(), 1)

        # loop over entire the buildhistory and check for related file
        # if the status is "build successful"

        for build in BuildHistory.objects.all():
            status = build.status
            if status == "build successful":
                self.assertGreater(build.files.all().count(), 0)


class TestBuildHistoryViews(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        set_initial_builds_data()
        self.client = Client()

    def test_all_builds_view(self):
        # no kwargs, should return all builds
        response = self.client.get(reverse('all_builds'))

        all_builds = response.context['builds']
        self.assertEquals(len(all_builds), 3)

        response_only_successful = self.client.get(reverse('all_builds'), {'status-filter': 'build successful'})
        self.assertEquals(len(response_only_successful.context['builds']), 1)

        response_all_failed = self.client.get(reverse('all_builds'), {'status-filter': 'failed'})
        self.assertEquals(len(response_all_failed.context['builds']), 2)

        response_valid_builder = self.client.get(reverse('all_builds'), {'builder-filter': '10.15'})
        self.assertEquals(len(response_valid_builder.context['builds']), 3)

        response_invalid_builder = self.client.get(reverse('all_builds'), {'builder-filter': '10.14'})
        self.assertEquals(len(response_invalid_builder.context['builds']), 0)

        response_port = self.client.get(reverse('all_builds'), {'name-filter': 'port-A2'})
        self.assertEquals(len(response_port.context['builds']), 1)

    def test_unresolved(self):
        # we should get only those builds in return which do not have a successful build following
        # them for a given builder and port

        # let us resolve build 2 for port-A1
        builder = Builder.objects.get(natural_name="Catalina")

        BuildHistory.objects.create(
            builder_name=builder,
            build_id=4,
            status="build successful",
            port_name="port-A1",
            time_start=datetime.now(timezone.utc),
            time_elapsed=None,
            watcher_id=1
        )

        response = self.client.get(reverse('all_builds'), {'status-filter': 'unresolved'})
        self.assertEquals(len(response.context['builds']), 1)
        self.assertEquals(response.context['builds'][0].build_id, 3)

        # let us resolve the build for port-A2 also now
        BuildHistory.objects.create(
            builder_name=builder,
            build_id=4,
            status="build successful",
            port_name="port-A2",
            time_start=datetime.now(timezone.utc),
            time_elapsed=None,
            watcher_id=1
        )

        response = self.client.get(reverse('all_builds'), {'status-filter': 'unresolved'})
        self.assertEquals(len(response.context['builds']), 0)


class TestBuildHistoryAPIViews(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        set_initial_builds_data()
        self.client = APIClient()

    def test_builds_list_view(self):
        response = self.client.get(reverse('builds-list'), format='json')
        response = response.data

        # pagination occurs after 50 objects, but we have only 3 categories
        self.assertEquals(len(response['results']), 3)

        response_filter_builder = self.client.get(reverse('builds-list'), {'builder_name__name': '10.15_x86_64'}, format='json')
        self.assertEquals(len(response_filter_builder.data['results']), 3)

        response_filter_builder_port = self.client.get(reverse('builds-list'), {'builder_name__name': '10.15_x86_64', 'port_name': 'port-A2'}, format='json')
        self.assertEquals(len(response_filter_builder_port.data['results']), 1)

    def test_builds_detail_view(self):
        response = self.client.get(reverse('builds-detail', kwargs={'pk': 1}), format='json')
        response = response.data

        self.assertEquals(response['port_name'], 'port-A1')

    def test_files_view(self):
        build = BuildHistory.objects.get(id=1)

        InstalledFile.objects.create(build=build, file='some-file-a.txt')
        InstalledFile.objects.create(build=build, file='some-file-b.txt')
        InstalledFile.objects.create(build=build, file='some-file-c.txt')
        InstalledFile.objects.create(build=build, file='some-file-d.txt')

        response = self.client.get(reverse('files-list'), format='json')
        data = response.data['results']

        # should return 3 objects, one for each build
        self.assertEquals(len(data), 3)

        for i in data:
            build_id = i['build_id']
            files = i['files']

            if build_id == 1:
                self.assertEquals(len(files), 4)
            else:
                self.assertEquals(len(files), 0)
