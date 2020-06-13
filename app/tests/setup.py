import json

from port.models import Port
from config import TEST_PORTINDEX_JSON


def setup_test_data():
    with open(TEST_PORTINDEX_JSON, 'r') as file:
        data = json.load(file)
    Port.add_or_update(data.get('ports', []))
