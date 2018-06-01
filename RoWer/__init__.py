from bw2data.backends.peewee import ActivityDataset as AD
from bw2data import databases
from collections import defaultdict
from itertools import count
import appdirs
import bw2data
import datetime
import json
import os
import pyprind
import sys


DATAPATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "data")
USERPATH = os.path.abspath(appdirs.user_data_dir("rower", "pylca"))
DEFAULT_EXCLUSIONS = [
    "AQ",                          # Antarctica
    "AUS-AC",                      # Uninhabited
    "Bajo Nuevo",                  # Uninhabited
    "Clipperton Island",           # Uninhabited
    "Coral Sea Islands",           # Only a weather station
]


if not os.path.isdir(USERPATH):
    os.makedirs(USERPATH)


class RowerDatapackage(object):
    def __init__(self, dirpath):
        if not os.path.exists(dirpath):
            os.mkdir(dirpath)
        elif not os.path.isdir(dirpath) or not os.access(dirpath, os.W_OK):
            raise ValueError("``dirpath`` must be a writable directory")
        self.path = dirpath
        if "datapackage.json" in os.listdir(self.path):
            self.metadata = self._read_json(os.path.join(self.path, "datapackage.json"))
        else:
            self.metadata = None

    @property
    def empty(self):
        return not any(x.endswith(".json") for x in os.listdir(self.path))

    def write_data(self, name, definitions=None, activity_mapping=None):
        assert definitions or activity_mapping, \
            "Must provide either ``definitions`` or ``activity_mapping``"
        if not self.empty:
            for root, dirs, files in os.walk(self.path):
                for filename in files:
                    os.unlink(os.path.join(self.path, filename))
        if definitions:
            self._save_json(definitions, "definitions.json")
        if activity_mapping:
            self._save_json(activity_mapping, "activity_mapping.json")
        self._write_datapackage(name)

    def read_data(self):
        data = {}
        for resource in self.metadata["resources"]:
            assert (bw2data.filesystem.md5(
                os.path.join(self.path, resource["path"])
            ) == resource["hash"]), "Data integrity failure"
            data[resource["name"]] = self._read_json(
                os.path.join(self.path, resource["path"])
            )
        return data

    def _save_json(self, data, filename):
        with open(os.path.join(self.path, filename), "w", encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _read_json(self, filename):
        return json.load(open(os.path.join(self.path, filename)))

    def _create_metadata(self, name):
        return  {
            "profile": "data-package",
            "name": name,
            "description": "Rest-of-World definitions and/or activity mappings for all or a given database",
            "version": "1",
            "licenses": [{
                "name": "ODC-PDDL-1.0",
                "path": "https://opendefinition.org/licenses/odc-pddl/",
                "title": "Open Data Commons Public Domain Dedication and Licence 1.0"
            }],
            "created": datetime.datetime.utcnow().isoformat(),
            "resources": []
        }

    def _write_datapackage(self, name):
        if not self.metadata:
            self.metadata = self._create_metadata(name)
        else:
            self.metadata["version"] = str(int(self.metadata["version"]) + 1)
            self.metadata["created"] = datetime.datetime.utcnow().isoformat()
        self._update_metadata_resources()
        self._save_json(self.metadata, os.path.join(self.path, "datapackage.json"))

    def _update_metadata_resources(self):
        self.metadata["resources"] = []
        if "definitions.json" in os.listdir(self.path):
            self.metadata["resources"].append({
                "name": "Rest-of-World definitions",
                "path": "definitions.json",
                "description": "Dictionary mapping specific Rest-of-Worlds labels to list of excluded locations",
                "format": "json",
                "hash": bw2data.filesystem.md5(
                    os.path.join(self.path, "definitions.json")
                )
            })
        if "activity_mapping.json" in os.listdir(self.path):
            self.metadata["resources"].append({
                "name": "Activity mapping",
                "path": "activity_mapping.json",
                "description": "Mapping from activity code to Rest-of-World label",
                "format": "json",
                "hash": bw2data.filesystem.md5(
                    os.path.join(self.path, "activity_mapping.json")
                )
            })


class Rower(object):
    def __init__(self, database):
        """Initiate ``Rower`` object to consistently label 'Rest-of-World' locations in LCI databases.

        ``database`` must be a registered database.

        This class provides the following functionality:

        * Define RoWs in a given database (``define_RoWs``). This will use the RoW labels in the master data, or create new user RoWs.
        * Load saved RoW definitions (``read_datapackage``).
        * Relabel activity locations in a given database using the generated RoW labels (``label_RoWs``).
        * Save user RoW definitions for reuse in a standard format (``write_datapackage``).
        * Import a ``geocollection`` and ``topocollection`` into bw2regional (bw2regional must be installed) (Not implemented).

        This class uses the following internal parameters:

        * ``self.db``: ``bw2data.Database`` instance
        * ``self.existing``: ``{"RoW label": ["list of excluded locations"]}``
        * ``self.user_rows``: ``{"RoW label": ["list of excluded locations"]}``
        * ``self.labelled``: ``{"RoW label": ["list of activity codes"]}``

        ``self.existing`` should be loaded (using ``self.load_existing``) from a previous saved result, while ``self.user_rows`` are new RoWs not found in ``self.existing``. When saving to a data package, only ``self.user_rows`` and ``self.labelled`` are saved.

        """
        assert database in bw2data.databases, "Database {} not registered".format(database)
        self.db = bw2data.Database(database)
        self.existing = {}
        self.user_rows = {}
        self.labelled = {}

    def list_existing(self):
        """List existing RoW definition data packages"""
        return [os.path.join(DATAPATH, o) for o in os.listdir(DATAPATH)
                if os.path.isdir(os.path.join(DATAPATH,o))] + \
               [os.path.join(USERPATH, o) for o in os.listdir(USERPATH)
                if os.path.isdir(os.path.join(DATAPATH,o))]

    def load_existing(self, dirname):
        """Load a data package and populate ``self.existing`` and/or ``self.labelled``.

        Returns *all* the data package resources."""
        data = RowerDatapackage(dirname).read_data()
        if "Activity mapping" in data:
            self.labelled = data["Activity mapping"]
        if "Rest-of-World definitions" in data:
            self.existing = data["Rest-of-World definitions"]
        return data

    def apply_existing_activity_map(self, dirname):
        self.load_existing(dirname)
        assert self.labelled, "No activity mapping found"
        self.label_RoWs()

        dct = self._get_saved(dirname)
        if 'Activity mapping' not in dct:
            raise ValueError("No activity mapping found")
        self.labelled = dct['Activity mapping']

    def save_data_package(self, dirname, name, overwrite=False):
        """Save definitions and activity mapping to a data package. Returns path of created directory.

        ``name`` is the data package name (stored in metadata).

        ``overwrite`` controls whether existing packages will be replaced."""
        dirpath = os.path.abspath(os.path.join(USERPATH, dirname))
        if os.path.exists(dirpath) and not overwrite:
            raise OSError("Directory already exists")
        dp = RowerDatapackage(dirpath)
        dp.write_data(name, self.user_rows, self.labelled)
        return dirpath

    def define_RoWs(self, prefix="RoW_user", default_exclusions=True):
        """Generate and return "RoW definition" dict and "activities to new RoW" dict.

        "RoW definition" identifies the geographies that are to be **excluded** from the RoW.
        It has the structure {'RoW_0': ['geo1', 'geo2', ..., ], 'RoW_1': ['geo3', 'geo4', ..., ]}.

        The "activities to new RoW" dict identifies which activities have which each RoW.
        It has the structure {'RoW_0': ['code of activity', 'code of another activity']}

        Resets ``self.user_rows`` and ``self.labelled``.

        """
        if self.db.backend == 'sqlite':
            data = self._load_groups_sqlite()
        else:
            data = self._load_groups_other_backend()

        counter = count()
        data = self._reformat_rows(data, default_exclusions=default_exclusions)
        self.user_rows = {}
        self.labelled = {}

        if not data:
            return self.labelled, self.user_rows

        for k in sorted(data):
            v = data[k]
            if k in self.existing:
                self.labelled[self.existing[k]] = v
            else:
                key = "{}_{}".format(prefix, next(counter))
                self.labelled[key] = v
                self.user_rows[key] = k

        return self.labelled, self.user_rows

    def label_RoWs(self):
        """Update the ``location`` labels in the given database with the generated RoWs stored in ``self.labelled``.

        Returns the number of locations changed."""
        assert hasattr(self, "labelled") and hasattr(self, "user_rows"), "Must run ``define_RoWs`` first"
        mapping = {code: row for row, lst in self.labelled.items() for code in lst}

        if self.db.backend == 'sqlite':
            return self._update_locations_sqlite(mapping)
        else:
            return self._update_locations_other(mapping)

    def _load_groups_other_backend(self):
        """Return dictionary of ``{(name, product): [(location, code)]`` from non-SQLite3 database"""
        data = defaultdict(list)
        for obj in bw2data.Database(database):
            data[(obj['name'], obj['product'])].append((obj['location'], obj['code']))
        return data

    def _load_groups_sqlite(self):
        """Return dictionary of ``{(name, product): [(location, code)]`` from SQLite3 database"""
        data = defaultdict(list)
        qs = list(AD.select(AD.name, AD.product, AD.location, AD.code).where(
            AD.database == self.db.name).dicts())
        for obj in qs:
            data[(obj['name'], obj['product'])].append((obj['location'], obj['code']))
        return data

    def _reformat_rows(self, data, default_exclusions=True):
        """Transform ``data`` from ``{(name, product): [(location, code)]}`` to ``{tuple(sorted([location])): [RoW activity code]}``.

        ``RoW`` must be one of the locations (and is deleted).

        Adds default exclusions if ``default_exclusions``."""
        result = defaultdict(list)
        for lst in data.values():
            if 'RoW' not in [x[0] for x in lst]:
                continue
            result[tuple(sorted([x[0] for x in lst if x[0] != "RoW"] +
                                DEFAULT_EXCLUSIONS if default_exclusions else []))
                 ].extend([x[1] for x in lst if x[0] == 'RoW'])
        return result

    def _update_locations_sqlite(self, mapping):
        count = 0
        for k, v in pyprind.prog_bar(mapping.items()):
            activity = bw2data.get_activity((self.db.name, k))
            activity['location'] = v
            activity.save()
            count += 1
        self.db.metadata['rowed'] = True
        databases.flush()
        return count

    def _update_locations_other(self, mapping):
        count = 0
        data = self.db.load()
        for k, v in data.items():
            if k[1] in mapping:
                v['location'] = mapping[k[1]]
                count += 1
        if count:
            self.db.write(data)
        self.db.metadata['rowed'] = True
        databases.flush()
        return count

    def _get_saved(self, dirname):
        if os.path.isdir(os.path.join(DATAPATH, dirname)):
            return RowerDatapackage(os.path.join(DATAPATH, dirname)).read_data()
        elif os.path.isdir(os.path.join(USERPATH, dirname)):
            return RowerDatapackage(os.path.join(USERPATH, dirname)).read_data()
        raise OSError("Can't find specified directory")
