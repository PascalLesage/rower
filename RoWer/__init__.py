from bw2data.backends.peewee import ActivityDataset as AD
from collections import defaultdict
from itertools import count
import bw2data
import datetime
import json
import os
import sys


DATAPATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "data")


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
            self._save_json(definitions, os.path.join(self.path, "definitions.json"))
        if activity_mapping:
            self._save_json(activity_mapping, os.path.join(self.path, "activity_mapping.json"))
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
            self.metadata = str(int(self.metadata["version"]) + 1)
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

        """
        assert database in bw2data.databases, "Database {} not registered".format(database)
        self.db = bw2data.Database(database)
        self.existing = {}

    def define_RoWs(self, prefix="RoW_user"):
        """Generate and return "RoW definition" dict and "activities to new RoW" dict.

        "RoW definition" identifies the geographies that are to be **excluded** from the RoW.
        It has the structure {'RoW_0': ['geo1', 'geo2', ..., ], 'RoW_1': ['geo3', 'geo4', ..., ]}.

        The "activities to new RoW" dict identifies which activities have which each RoW.
        It has the structure {'RoW_0': ['code of activity', 'code of another activity']}

        """
        if self.db.backend == 'sqlite':
            data = self._load_groups_sqlite()
        else:
            data = self._load_groups_other_backend()

        counter = count()
        data = self._reformat_rows(data)

        self.user_rows = {}
        self.labelled = {}
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
        """Update the ``location`` labels in the given database with the generated RoWs.

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

    def _reformat_rows(self, data):
        """Transform ``data`` from ``{(name, product): [(location, code)]`` to ``{tuple(sorted([location])): [RoW activity code]}``.

        ``RoW`` must be one of the locations (and is deleted)."""
        return {tuple(sorted([x[0] for x in lst if x[0] != "RoW"])):
                [x[1] for x in lst if x[0] == 'RoW']
                for lst in data.values()
                if 'RoW' in [x[0] for x in lst]}

    def _update_locations_sqlite(self, mapping):
        count = 0
        for k, v in mapping.items():
            count += AD.update({AD.location: v}).where(
                AD.code == k, AD.database == self.db.name
            ).execute()
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
        return count
