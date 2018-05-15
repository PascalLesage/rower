from RoWer import make_RoWs, write_RoW_info
from brightway2 import Database, projects, get_activity
import os
import pytest
import json

@pytest.fixture(scope='function') # Tear down database after every test
def animals_db(tmpdir):
    #Setup
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
    dirpath = str(tmpdir)
    os.environ["BRIGHTWAY2_DIR"] = dirpath

    projects.set_current('test')
    db = Database('animals')
    db.write(animal_data)

    yield

    #teardown
    #db.delete()
    #db.deregister()
    #projects.delete_project(delete_dir=True)
    del os.environ["BRIGHTWAY2_DIR"]
    return None

def test_RoW_db_has_same_structure(animals_db):
    db = Database('animals')
    original_length = len(db)
    original_loaded_db = db.load()

    _, _ = make_RoWs('animals', modify_db_in_place=True)

    # Modification of database hasn't changed its size
    assert len(db) == original_length

    loaded_db = db.load()
    # The keys of the datasets have not changed
    assert set([*original_loaded_db]) == set([*loaded_db])

def test_locations_changed_as_expected(animals_db):
    original_db = Database('animals').load()
    _, _ = make_RoWs('animals', modify_db_in_place=True)
    new_db = Database('animals').load()

    for act in original_db.keys():
            # Check all the locations that were initially RoWs
        if original_db[act]['location'] == 'RoW':
            assert new_db[act]['location'][0:3] == 'RoW'
            assert new_db[act]['location'][3] == '_'
            int(new_db[act]['location'][4:]) # Will fail if not integer
        else:
            assert new_db[act]['location'] == original_db[act]['location']

def test_RoW_dict(animals_db):
    RoW_dict, RoW_act_mapping = make_RoWs('animals', modify_db_in_place=True)
    mutt_act = get_activity(('animals', 'mutt'))
    mutt_pup_act = get_activity(('animals', 'mutt pup'))
    moggy_act = get_activity(('animals', 'moggy'))
    mutt_location = mutt_act['location']
    mutt_pup_location = mutt_pup_act['location']
    moggy_location = moggy_act['location']

    # Locations of RoW activities begin with "RoW"
    assert mutt_location[0:3] == 'RoW'
    assert mutt_pup_location[0:3] == 'RoW'
    assert moggy_location[0:3] == 'RoW'
    # Locations of RoW activities are of length 5
    assert len(mutt_location) == 5
    assert len(mutt_pup_location) == 5
    assert len(moggy_location) == 5
    # Locations of RoW acts are in the RoW dict
    assert mutt_location in RoW_dict.keys()
    assert mutt_pup_location in RoW_dict.keys()
    assert moggy_location in RoW_dict.keys()
    # The RoW dict only has those three
    print(RoW_dict, RoW_act_mapping)
    assert len(RoW_dict) == 3
    # Check the contents of the RoW_dict
    assert sorted(RoW_dict[mutt_location]) == ['CN', 'DE']
    assert sorted(RoW_dict[mutt_pup_location]) == ['CN', 'DE']
    assert RoW_dict[moggy_location] == ['IR']
    # Check that the values of the RoW_act_mapping are the keys of the RoW_dict
    assert sorted(list(RoW_dict.keys())) == sorted(list(RoW_act_mapping.values()))
    # Specifically:
    assert RoW_act_mapping[mutt_act.key] == mutt_location
    assert RoW_act_mapping[mutt_pup_act.key] == mutt_pup_location
    assert RoW_act_mapping[moggy_act.key] == moggy_location

def test_written_info_no_new_name(animals_db, tmpdir_factory):
    RoW_dict, RoW_act_mapping = make_RoWs('animals', modify_db_in_place=False)
    temp_dir = tmpdir_factory.mktemp('temp')
    write_RoW_info(RoW_dict, RoW_act_mapping, root_dirpath=temp_dir, overwrite=False, new_name=None)
    dir = os.path.join(temp_dir, 'animals')
    package = json.load(open(os.path.join(dir, 'datapackage.json')))
    row_def_resource = [resource for resource in package['resources']
                        if list(resource.keys())[0]=='RoW definitions'][0]
    loaded_RoW_defs = json.load(open(row_def_resource['RoW definitions']['path'], 'r'))
    for k in loaded_RoW_defs.keys():
        assert RoW_dict[k] == loaded_RoW_defs[k]
    mapping_resource = [resource for resource in package['resources']
                        if list(resource.keys())[0]=='Mapping'][0]
    loaded_mapping_resources = json.load(open(mapping_resource['Mapping']['path'], 'r'))
    for k in loaded_mapping_resources.keys():
        assert loaded_mapping_resources[k] == RoW_act_mapping[('animals', k)]
    # Check that error is thrown if attempt to overwrite files
    with pytest.raises(ValueError):
        write_RoW_info(RoW_dict, RoW_act_mapping, root_dirpath=temp_dir, overwrite=False)

def test_written_info_new_name(animals_db, tmpdir_factory):
    RoW_dict, RoW_act_mapping = make_RoWs('animals', modify_db_in_place=False)
    temp_dir = tmpdir_factory.mktemp('temp')
    write_RoW_info(RoW_dict, RoW_act_mapping, root_dirpath=temp_dir, overwrite=False, new_name="furry things")
    dir = os.path.join(temp_dir, 'furry things')
    package = json.load(open(os.path.join(dir, 'datapackage.json')))
    row_def_resource = [resource for resource in package['resources']
                        if list(resource.keys())[0]=='RoW definitions'][0]
    loaded_RoW_defs = json.load(open(row_def_resource['RoW definitions']['path'], 'r'))
    for k in loaded_RoW_defs.keys():
        assert RoW_dict[k] == loaded_RoW_defs[k]
    mapping_resource = [resource for resource in package['resources']
                        if list(resource.keys())[0]=='Mapping'][0]
    loaded_mapping_resources = json.load(open(mapping_resource['Mapping']['path'], 'r'))
    for k in loaded_mapping_resources.keys():
        assert loaded_mapping_resources[k] == RoW_act_mapping[('animals', k)]
    # Check that error is thrown if attempt to overwrite files
    with pytest.raises(ValueError):
        write_RoW_info(RoW_dict, RoW_act_mapping, root_dirpath=temp_dir, overwrite=False, new_name="furry things")