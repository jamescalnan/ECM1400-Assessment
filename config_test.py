import json
import os.path


def test_config_file_exists():
    assert os.path.exists('config.json')


def test_config_contents():
    data = json.loads(open("config.json", encoding="utf8").read())
    assert isinstance(data['location'], str)
    assert isinstance(data['location_type'], str)
    assert isinstance(data['news_terms'], str)
    assert isinstance(data['nation'], str)
