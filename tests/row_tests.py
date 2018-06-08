from rower import Rower, RowerDatapackage
import rower
from bw2data import Database, projects, get_activity
from bw2data.tests import bw2test
import os
import pytest
import json


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
    assert len(Rower("animals").list_existing()) == 7

def test_locations_changed_as_expected(basic):
    rower = Rower("animals")
    rower.define_RoWs()
    rower.label_RoWs()
    assert get_activity(('animals', 'mutt pup'))['location'] == 'RoW_user_0'
    assert get_activity(('animals', 'mutt'))['location'] == 'RoW_user_0'
    assert get_activity(('animals', 'moggy'))['location'] == 'RoW_user_1'

def test_userdata_redirect(basic, redirect_userdata):
    rower = Rower("animals")
    rower.define_RoWs()
    rower.label_RoWs()
    dp = rower.save_data_package("foo", "bar")
    print(dp)
    assert "rower" not in dp
    assert "pytest" in dp

def test_writing_new_datapackage(basic, redirect_userdata):
    rower = Rower("animals")
    rower.define_RoWs()
    rower.label_RoWs()
    dp = rower.save_data_package("foo", "bar")
    assert len(Rower("animals").list_existing()) == 8
    assert "foo" in Rower("animals").list_existing()[-1]

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
        assert os.path.isdir(getattr(Rower, label))
    assert len({getattr(Rower, label) for label in labels}) == len(labels)

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

    r = Rower('animals')
    r.load_existing(r.EI_GENERIC)
    r.label_RoWs()
    assert get_activity(('animals', 'mutt')) == "RoW_88"

def test_with_ecoinvent_specific():
    pass

def test_with_user_existing():
    pass

def test_with_nondefault_backend():
    pass

def test_with_default_exclusions():
    pass

def test_without_default_exclusions():
    pass
