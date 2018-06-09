from bw2data import Database, projects, get_activity
from bw2data.tests import bw2test
import json
import os
import pytest
import rower


@pytest.fixture
def redirect_userdata(monkeypatch, tmpdir):
    monkeypatch.setattr(rower.base, 'USERPATH', tmpdir)
    monkeypatch.setattr(rower, 'USERPATH', tmpdir)


@pytest.fixture
@bw2test
def basic():
    assert not len(Database('animals'))
    animal_data = {
        ('animals', 'food'): {
            'name': 'food',
            'exchanges': [
                {
                    'amount': 1.0,
                    'input': ('animals', 'food'),
                    'type': 'production'
                }
            ],
            'unit': 'kilogram',
            'location': 'GLO',
            'reference product': 'food',
        },
        ('animals', 'german_shepherd'): {
            'name': 'dogs',
            'reference product': 'dog',
            'exchanges': [
                {
                    'amount': 1.0,
                    'input': ('animals', 'food'),
                    'type': 'technosphere'
                },
                {
                    'amount': 1.0,
                    'input': ('animals', 'german_shepherd'),
                    'type': 'production'
                },
            ],
            'unit': 'kilogram',
            'location': 'DE',
        },
        ('animals', 'pug'): {
            'name': 'dogs',
            'reference product': 'dog',
            'exchanges': [
                {
                    'amount': 1.0,
                    'input': ('animals', 'food'),
                    'type': 'technosphere'
                },
                {
                    'amount': 1.0,
                    'input': ('animals', 'pug'),
                    'type': 'production'
                },
            ],
            'unit': 'kilogram',
            'location': 'CN',
        },
        ('animals', 'mutt'): {
            'name': 'dogs',
            'reference product': 'dog',
            'exchanges': [
                {
                    'amount': 1.0,
                    'input': ('animals', 'food'),
                    'type': 'technosphere'
                },
                {
                    'amount': 1.0,
                    'input': ('animals', 'mutt'),
                    'type': 'production'
                },
            ],
            'unit': 'kilogram',
            'location': 'RoW',
        },

        ('animals', 'german_shepherd pup'): {
            'name': 'dogs',
            'reference product': 'puppy',
            'exchanges': [
                {
                    'amount': 1.0,
                    'input': ('animals', 'food'),
                    'type': 'technosphere'
                },
                {
                    'amount': 1.0,
                    'input': ('animals', 'german_shepherd pup'),
                    'type': 'production'
                },
            ],
            'unit': 'kilogram',
            'location': 'DE',
        },
        ('animals', 'pug pup'): {
            'name': 'dogs',
            'reference product': 'puppy',
            'exchanges': [
                {
                    'amount': 1.0,
                    'input': ('animals', 'food'),
                    'type': 'technosphere'
                },
                {
                    'amount': 1.0,
                    'input': ('animals', 'pug pup'),
                    'type': 'production'
                },
            ],
            'unit': 'kilogram',
            'location': 'CN',
        },
        ('animals', 'mutt pup'): {
            'name': 'dogs',
            'reference product': 'puppy',
            'exchanges': [
                {
                    'amount': 1.0,
                    'input': ('animals', 'food'),
                    'type': 'technosphere'
                },
                {
                    'amount': 1.0,
                    'input': ('animals', 'mutt pup'),
                    'type': 'production'
                },
            ],
            'unit': 'kilogram',
            'location': 'RoW',
        },
        ('animals', 'persian'): {
            'name': 'cats',
            'reference product': 'cat',
            'exchanges': [
                {
                    'amount': 1.0,
                    'input': ('animals', 'food'),
                    'type': 'technosphere'
                },
                {
                    'amount': 1.0,
                    'input': ('animals', 'persian'),
                    'type': 'production'
                },
            ],
            'unit': 'kilogram',
            'location': 'IR',
        },
        ('animals', 'moggy'): {
            'name': 'cats',
            'reference product': 'cat',
            'exchanges': [
                {
                    'amount': 1.0,
                    'input': ('animals', 'food'),
                    'type': 'technosphere'
                },
                {
                    'amount': 1.0,
                    'input': ('animals', 'moggy'),
                    'type': 'production'
                },
            ],
            'unit': 'kilogram',
            'location': 'RoW',
        },
        ('animals', 'hamster'): {
            'name': 'hamster',
            'reference product': 'hamster',
            'exchanges': [
                {
                    'amount': 1.0,
                    'input': ('animals', 'food'),
                    'type': 'technosphere'
                },
                {
                    'amount': 1.0,
                    'input': ('animals', 'hamster'),
                    'type': 'production'
                },
            ],
            'unit': 'kilogram',
            'location': 'GLO',
        },
    }
    db = Database('animals')
    db.write(animal_data)
    return db


def test_existing_ecoinvent_present(basic, redirect_userdata):
    assert len(rower.Rower("animals").list_existing()) == 7

def test_locations_changed_as_expected(basic):
    rwr = rower.Rower("animals")
    rwr.define_RoWs()
    rwr.label_RoWs()
    assert get_activity(('animals', 'mutt pup'))['location'] == 'RoW_user_0'
    assert get_activity(('animals', 'mutt'))['location'] == 'RoW_user_0'
    assert get_activity(('animals', 'moggy'))['location'] == 'RoW_user_1'

def test_userdata_redirect(basic, redirect_userdata):
    rwr = rower.Rower("animals")
    rwr.define_RoWs()
    rwr.label_RoWs()
    dp = rwr.save_data_package("foo", "bar")
    assert "rower" not in dp
    assert "pytest" in dp

def test_writing_new_datapackage(basic, redirect_userdata):
    rwr = rower.Rower("animals")
    rwr.define_RoWs()
    rwr.label_RoWs()
    dp = rwr.save_data_package("foo", "bar")
    assert len(rower.Rower("animals").list_existing()) == 8
    assert "foo" in rower.Rower("animals").list_existing()[-1]

def test_builtin_paths():
    labels = [
        "EI_GENERIC",
        "EI_3_3_APOS",
        "EI_3_4_APOS",
        "EI_3_3_CUTOFF",
        "EI_3_4_CUTOFF",
        "EI_3_3_CONSEQUENTIAL",
        "EI_3_4_CONSEQUENTIAL",
    ]
    assert len(set(labels)) == len(labels)
    for label in labels:
        assert os.path.isdir(getattr(rower.Rower, label))
    assert len({getattr(rower.Rower, label) for label in labels}) == len(labels)

@bw2test
def test_with_ecoinvent_generic():
    assert not len(Database('animals'))
    animal_data = {
        ('animals', 'dogo'): {
            'name': 'dogs',
            'reference product': 'dog',
            'exchanges': [],
            'unit': 'kilogram',
            'location': 'BR',
        },
        ('animals', 'st bernhard'): {
            'name': 'dogs',
            'reference product': 'dog',
            'exchanges': [],
            'unit': 'kilogram',
            'location': 'CH',
        },
        ('animals', 'mutt'): {
            'name': 'dogs',
            'reference product': 'dog',
            'exchanges': [],
            'unit': 'kilogram',
            'location': 'RoW',
        },
    }
    db = Database('animals')
    db.write(animal_data)

    rwr = rower.Rower('animals')
    rwr.load_existing(rwr.EI_GENERIC)
    rwr.define_RoWs()
    rwr.label_RoWs()
    assert get_activity(('animals', 'mutt'))['location'] == "RoW_88"

@bw2test
def test_with_ecoinvent_specific_full():
    assert not len(Database('animals'))
    animal_data = {
        ('animals', "6ccf7e69afcf1b74de5b52ae28bbc1c2"): {
            'name': 'dogs',
            'reference product': 'dog',
            'exchanges': [],
            'unit': 'kilogram',
            'location': 'RoW',
        },
    }
    db = Database('animals')
    db.write(animal_data)

    rwr = rower.Rower('animals')
    rwr.load_existing(rwr.EI_3_4_CONSEQUENTIAL)
    rwr.label_RoWs()
    assert get_activity(('animals', "6ccf7e69afcf1b74de5b52ae28bbc1c2"))['location'] == "RoW_64"

@bw2test
def test_with_ecoinvent_specific_shortcut():
    assert not len(Database('animals'))
    animal_data = {
        ('animals', "6ccf7e69afcf1b74de5b52ae28bbc1c2"): {
            'name': 'dogs',
            'reference product': 'dog',
            'exchanges': [],
            'unit': 'kilogram',
            'location': 'RoW',
        },
    }
    db = Database('animals')
    db.write(animal_data)

    rwr = rower.Rower('animals')
    rwr.apply_existing_activity_map(rwr.EI_3_4_CONSEQUENTIAL)
    assert get_activity(('animals', "6ccf7e69afcf1b74de5b52ae28bbc1c2"))['location'] == "RoW_64"

def test_with_user_existing():
    pass

def test_with_nondefault_backend():
    pass

def test_with_default_exclusions(basic, redirect_userdata):
    rwr = rower.Rower("animals")
    rwr.define_RoWs()
    expected = {
        'RoW_user_0': ('AQ', 'AUS-AC', 'Bajo Nuevo', 'CN',
                       'Clipperton Island', 'Coral Sea Islands', 'DE'),
        'RoW_user_1': ('AQ', 'AUS-AC', 'Bajo Nuevo', 'Clipperton Island',
                        'Coral Sea Islands', 'IR'),
    }
    assert rwr.user_rows == expected

def test_without_default_exclusions(basic, redirect_userdata):
    rwr = rower.Rower("animals")
    rwr.define_RoWs(default_exclusions=False)
    expected = {
        'RoW_user_0': ('CN', 'DE'),
        'RoW_user_1': ('IR',),
    }
    assert rwr.user_rows == expected

def test_custom_exclusions(basic, redirect_userdata):
    rwr = rower.Rower("animals")
    rwr.define_RoWs(default_exclusions=('foo', 'bar'))
    expected = {
        'RoW_user_0': ('CN', 'DE', 'bar', 'foo'),
        'RoW_user_1': ('IR', 'bar', 'foo'),
    }
    assert rwr.user_rows == expected
