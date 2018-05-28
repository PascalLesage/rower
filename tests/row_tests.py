from rower import Rower, RowerDatapackage
import rower
from bw2data import Database, projects, get_activity
from bw2data.tests import bw2test
import os
import pytest
import json


@pytest.fixture
def redirect_userdata(monkeypatch, tmpdir):
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


def test_existing_ecoinvent_present(basic):
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


# def test_RoW_dict(animals_db):
#     RoW_dict, RoW_act_mapping = make_RoWs('animals', modify_db_in_place=True)
#     mutt_act = get_activity(('animals', 'mutt'))
#     mutt_pup_act = get_activity(('animals', 'mutt pup'))
#     moggy_act = get_activity(('animals', 'moggy'))
#     mutt_location = mutt_act['location']
#     mutt_pup_location = mutt_pup_act['location']
#     moggy_location = moggy_act['location']

#     # Locations of RoW activities begin with "RoW"
#     assert mutt_location[0:3] == 'RoW'
#     assert mutt_pup_location[0:3] == 'RoW'
#     assert moggy_location[0:3] == 'RoW'
#     # Locations of RoW activities are of length 5
#     assert len(mutt_location) == 5
#     assert len(mutt_pup_location) == 5
#     assert len(moggy_location) == 5
#     # Locations of RoW acts are in the RoW dict
#     assert mutt_location in RoW_dict.keys()
#     assert mutt_pup_location in RoW_dict.keys()
#     assert moggy_location in RoW_dict.keys()
#     # The RoW dict only has those three
#     print(RoW_dict, RoW_act_mapping)
#     assert len(RoW_dict) == 3
#     # Check the contents of the RoW_dict
#     assert sorted(RoW_dict[mutt_location]) == ['CN', 'DE']
#     assert sorted(RoW_dict[mutt_pup_location]) == ['CN', 'DE']
#     assert RoW_dict[moggy_location] == ['IR']
#     # Check that the values of the RoW_act_mapping are the keys of the RoW_dict
#     assert sorted(list(RoW_dict.keys())) == sorted(list(RoW_act_mapping.values()))
#     # Specifically:
#     assert RoW_act_mapping[mutt_act.key] == mutt_location
#     assert RoW_act_mapping[mutt_pup_act.key] == mutt_pup_location
#     assert RoW_act_mapping[moggy_act.key] == moggy_location

# def test_written_info_no_new_name(animals_db, tmpdir_factory):
#     RoW_dict, RoW_act_mapping = make_RoWs('animals', modify_db_in_place=False)
#     temp_dir = tmpdir_factory.mktemp('temp')
#     write_RoW_info(RoW_dict, RoW_act_mapping, root_dirpath=temp_dir, overwrite=False, new_name=None)
#     dir = os.path.join(temp_dir, 'animals')
#     package = json.load(open(os.path.join(dir, 'datapackage.json')))
#     row_def_resource = [resource for resource in package['resources']
#                         if list(resource.keys())[0]=='RoW definitions'][0]
#     loaded_RoW_defs = json.load(open(row_def_resource['RoW definitions']['path'], 'r'))
#     for k in loaded_RoW_defs.keys():
#         assert RoW_dict[k] == loaded_RoW_defs[k]
#     mapping_resource = [resource for resource in package['resources']
#                         if list(resource.keys())[0]=='Mapping'][0]
#     loaded_mapping_resources = json.load(open(mapping_resource['Mapping']['path'], 'r'))
#     for k in loaded_mapping_resources.keys():
#         assert loaded_mapping_resources[k] == RoW_act_mapping[('animals', k)]
#     # Check that error is thrown if attempt to overwrite files
#     with pytest.raises(ValueError):
#         write_RoW_info(RoW_dict, RoW_act_mapping, root_dirpath=temp_dir, overwrite=False)

# def test_written_info_new_name(animals_db, tmpdir_factory):
#     RoW_dict, RoW_act_mapping = make_RoWs('animals', modify_db_in_place=False)
#     temp_dir = tmpdir_factory.mktemp('temp')
#     write_RoW_info(RoW_dict, RoW_act_mapping, root_dirpath=temp_dir, overwrite=False, new_name="furry things")
#     dir = os.path.join(temp_dir, 'furry things')
#     package = json.load(open(os.path.join(dir, 'datapackage.json')))
#     row_def_resource = [resource for resource in package['resources']
#                         if list(resource.keys())[0]=='RoW definitions'][0]
#     loaded_RoW_defs = json.load(open(row_def_resource['RoW definitions']['path'], 'r'))
#     for k in loaded_RoW_defs.keys():
#         assert RoW_dict[k] == loaded_RoW_defs[k]
#     mapping_resource = [resource for resource in package['resources']
#                         if list(resource.keys())[0]=='Mapping'][0]
#     loaded_mapping_resources = json.load(open(mapping_resource['Mapping']['path'], 'r'))
#     for k in loaded_mapping_resources.keys():
#         assert loaded_mapping_resources[k] == RoW_act_mapping[('animals', k)]
#     # Check that error is thrown if attempt to overwrite files
#     with pytest.raises(ValueError):
#         write_RoW_info(RoW_dict, RoW_act_mapping, root_dirpath=temp_dir, overwrite=False, new_name="furry things")
