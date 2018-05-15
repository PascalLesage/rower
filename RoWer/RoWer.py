import bw2data
import sys
from time import time
import json
import os
import shutil

def make_RoWs(database, modify_db_in_place=True, verbose=True):
    """ Return "RoW definition" dict and "activities to new RoW" dict

    The "RoW definition" dict identifies the geographies that are to be **excluded** from the RoW
    The "RoW definition" dict has the structure {'RoW_0': ['geo1', 'geo2', ..., ], 'RoW_1': ['geo3', 'geo4', ..., ]}

    The "activities to new RoW" dict identifies which activities have which new RoW.
    The "activities to new RoW" dict structure is {act0: 'RoW_0', act1: 'RoW_1', ...}

    With modify_db_in_place=True, replace all instances of unspecified "RoW" in
    database with specific RoW from "RoW definition" dict.
    """
    assert database in bw2data.databases, "Database {} not registered".format(database)
    t0 = time()
    loaded_db = bw2data.Database(database).load()
    acts_with_RoWs = [act for act, data in loaded_db.items() if data['location']=='RoW']
    if len(acts_with_RoWs) == 0:
        print("No datasets with RoW location found. Exiting.")
        sys.exit()
    if verbose:
        print("{} activities with RoW location found in {:4} seconds, generating dictionaries".format(
            len(acts_with_RoWs),
            time()-t0
        )
        )
    t1 = time()

    RoW_dict = {}  # RoW definition dict
    RoW_act_mapping = {} # activities to new RoW dict

    for i, act in enumerate(acts_with_RoWs):
        RoW_dict['RoW_' + str(i)] = [data['location'] for data in loaded_db.values()
                                     if data['name'] == loaded_db[act]['name']
                                     and data['reference product'] == loaded_db[act]['reference product']
                                     and data['location'] != 'RoW'
                                     ]
        RoW_act_mapping[act] = 'RoW_' + str(i)
    if verbose:
        print("Generated {} RoW definitions in {:4} seconds".format(
            len(RoW_dict),
            time()-t1
        )
        )
    if modify_db_in_place:
        print("Modifying database {} in place".format(database))
        modify_database_from_loaded_database(database, loaded_db, RoW_act_mapping)
    return RoW_dict, RoW_act_mapping


def modify_database_from_stored_database(database_name, RoW_act_mapping):
    """ Specify RoW locations in a database on disk and save database"""
    assert database_name in bw2data.databases, "Database {} not registered".format(database)
    modify_database_from_loaded_database(
        database_name,
        Database(database_name).load(),
        RoW_act_mapping
    )
    return None

def modify_database_from_loaded_database(database_name, loaded_database, RoW_act_mapping):
    """ Specify RoW locations in a loaded database and save database to disk"""
    for act, new_row in RoW_act_mapping.items():
        loaded_database[act]['location'] = new_row
    bw2data.Database(database_name).write(loaded_database)

def write_RoW_info(RoW_dict, RoW_act_mapping, root_dirpath, overwrite=False, new_name=None):
    """ Function to store RoW data to disk.

    Will create a directory following the json Data Package schema.
    By default, the name of the Data Package is the name of the database, i.e.
    the first string in the key of the activities.
    It is possible to override this default name with `new_name`, but you should probably
    not do this.
    The data package will have two resources:
        RoW definition dict
        activities to new RoW dict
    """
    # Check that there is actually some data to save
    assert len(RoW_dict)>0, "No data to save"
    # Validate dicts:
    assert len(RoW_dict)==len(RoW_act_mapping), "The two dicts must have the same length"
    implicit_db_names = [key[0] for key in RoW_act_mapping.keys()]
    assert len(set(implicit_db_names))==1, "The dicts should be for a single database"
    implicit_db_name = implicit_db_names[0]
    name = new_name or implicit_db_name

    if os.path.exists(root_dirpath):
        assert os.path.isdir(root_dirpath), "`root_dirpath` must be a directory"
        assert os.access(root_dirpath, os.W_OK), "`dirpath` must be a writable directory"
    else:
        os.makedirs(root_dirpath)

    dirpath = os.path.join(root_dirpath, name)

    if os.path.isdir(dirpath):
        if not overwrite:
            raise ValueError("The directory {} already exists".format(dirpath))
        else:
            shutil.rmtree(dirpath)
    os.makedirs(dirpath)

    # Inform datapackage metadata
    datapackage = {
        "name": str(name),
        "description": "Dictionaries containing details about RoWs for database {}".format(implicit_db_name),
        "profile": "data-package",
        "resources": [
            {"RoW definitions":
                {
                    "name": "RoW definition dict",
                    "path": os.path.join(dirpath, 'RoW_definition.json'),
                    "description": "Dictionary with specific RoWs as keys and list of excluded geographies as value.",
                    "format": "json",
                }
            },
            {"Mapping":
                 {
                    "name": "Activity to RoW mapping dict",
                    "path": os.path.join(dirpath, 'activity_to_RoW_mapping.json'),
                    "description": "Dictionary mapping activity codes to specific RoWs.",
                    "format": "json",
                },
            }
        ]
    }

    RoW_act_mapping_as_codes = {k[1]:v for k, v in RoW_act_mapping.items()}

    with open(os.path.join(dirpath, "datapackage.json"), "w", encoding='utf-8') as f:
        json.dump(datapackage, f, indent=2, ensure_ascii=False)
    with open(os.path.join(dirpath, "RoW_definition.json"), "w", encoding='utf-8') as f:
        json.dump(RoW_dict, f, indent=2, ensure_ascii=False)
    with open(os.path.join(dirpath, "activity_to_RoW_mapping.json"), "w", encoding='utf-8') as f:
        json.dump(RoW_act_mapping_as_codes, f, indent=2, ensure_ascii=False)