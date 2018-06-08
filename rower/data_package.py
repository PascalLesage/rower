import bw2data
import datetime
import json
import os


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
            if not resource["format"] == "json":
                continue
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
