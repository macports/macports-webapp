from django.test import SimpleTestCase

from ports.utilities import sort_by_version


class TestVersions(SimpleTestCase):
    reset_sequences = True

    def test_numeric_dict(self):
        versions = [
            {"version": "10.10.1_1"},
            {"version": "10.10.1_0"},
            {"version": "10.10"},
            {"version": "10.10.1"},
            {"version": "10.10.11"},
            {"version": "10.9"},
            {"version": "10.1"},
            {"version": "10.1.11"},
            {"version": "10.1.10"},
            {"version": "10.1.9"},
            {"version": "9.9.9.9"},
            {"version": "9.9.9"},
            {"version": "9.9"},
            {"version": "9"},
            {"version": "9.1.0.0"},
            {"version": "9.1.0.A"},
            {"version": "9.1.0.a"},
            {"version": "9.100.1"},
        ]
        versions = sort_by_version.sort_list_of_dicts_by_version(versions, "version")

        expected = [
            {"version": "10.10.11"},
            {"version": "10.10.1_1"},
            {"version": "10.10.1_0"},
            {"version": "10.10.1"},
            {"version": "10.10"},
            {"version": "10.9"},
            {"version": "10.1.11"},
            {"version": "10.1.10"},
            {"version": "10.1.9"},
            {"version": "10.1"},
            {"version": "9.100.1"},
            {"version": "9.9.9.9"},
            {"version": "9.9.9"},
            {"version": "9.9"},
            {"version": "9.1.0.0"},
            {"version": "9.1.0.a"},
            {"version": "9.1.0.A"},
            {"version": "9"},
        ]

        self.assertEquals(versions, expected)

    def test_alphanumeric_dict(self):
        versions = [
            {"version": "10.10.a"},
            {"version": "10.10.a1"},
            {"version": "10.10.a2"},
            {"version": "10.10.a12"},
            {"version": "10.a.1"},
            {"version": "10.aa.1"},
            {"version": "10.ab.1"},
            {"version": "10.b.1"},
            {"version": "10.a"},
            {"version": "10.b"},
            {"version": "10.1.a"},
            {"version": "10.1-a_0"},
            {"version": "10.1-c_0"},
            {"version": "10.+-=!ABC_0"},
            {"version": "AAAAAA"},
            {"version": "AAA.AAA"},
            {"version": "AAA-A-A"},
            {"version": "AAA-A+B"},
        ]
        versions = sort_by_version.sort_list_of_dicts_by_version(versions, "version")

        expected = [
            {"version": "10.10.a2"},
            {"version": "10.10.a12"},
            {"version": "10.10.a1"},
            {"version": "10.10.a"},
            {"version": "10.1-c_0"},
            {"version": "10.1-a_0"},
            {"version": "10.1.a"},
            {"version": "10.b.1"},
            {"version": "10.b"},
            {"version": "10.ab.1"},
            {"version": "10.aa.1"},
            {"version": "10.a.1"},
            {"version": "10.a"},
            {"version": "10.+-=!ABC_0"},
            {"version": "AAAAAA"},
            {"version": "AAA.AAA"},
            {"version": "AAA-A+B"},
            {"version": "AAA-A-A"},
        ]
        self.assertEquals(versions, expected)

    def test_version_list(self):
        versions = [
            "10.10.a",
            "10.1_0.a",
            "10.10.a1",
            "10.10.a2",
            "10.10.a12",
            "10.a.a",
            "10.aa.1",
            "10.ab.1",
            "10.b.1",
            "10.a",
            "10.b",
            "10.1_0.a",
            "10.1.a",
            "10.1-a_0",
            "10.1-c_0",
            "10.+-=!ABC_0",
            "AAAAAA",
            "AAA.AAA",
            "AAA-A-A",
            "AAA-A+B"
        ]
        versions = sort_by_version.sort_list_by_version(versions)

        expected = [
            "10.10.a2",
            "10.10.a12",
            "10.10.a1",
            "10.10.a",
            "10.1_0.a",
            "10.1_0.a",
            "10.1-c_0",
            "10.1-a_0",
            "10.1.a",
            "10.b.1",
            "10.b",
            "10.ab.1",
            "10.aa.1",
            "10.a.a",
            "10.a",
            "10.+-=!ABC_0",
            "AAAAAA",
            "AAA.AAA",
            "AAA-A+B",
            "AAA-A-A",
        ]

        self.assertEquals(versions, expected)
