from . import DATAPATH, USERPATH, RowerDatapackage
from bw2data.backends.peewee import ActivityDataset as AD
from bw2data import databases
from collections import defaultdict
from itertools import count
import bw2data
import os
import pyprind


DEFAULT_EXCLUSIONS = [
    "AQ",                          # Antarctica
    "AUS-AC",                      # Uninhabited
    "Bajo Nuevo",                  # Uninhabited
    "Clipperton Island",           # Uninhabited
    "Coral Sea Islands",           # Only a weather station
]


class Rower(object):
    EI_GENERIC = os.path.join(DATAPATH, "ecoinvent generic")
    EI_3_3_APOS = os.path.join(DATAPATH, "ecoinvent 3.3 apos")
    EI_3_4_APOS = os.path.join(DATAPATH, "ecoinvent 3.4 apos")
    EI_3_3_CUTOFF = os.path.join(DATAPATH, "ecoinvent 3.3 cutoff")
    EI_3_4_CUTOFF = os.path.join(DATAPATH, "ecoinvent 3.4 cutoff")
    EI_3_3_CONSEQUENTIAL = os.path.join(DATAPATH, "ecoinvent 3.3 consequential")
    EI_3_4_CONSEQUENTIAL = os.path.join(DATAPATH, "ecoinvent 3.4 consequential")

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
                if os.path.isdir(os.path.join(USERPATH,o))]

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
        assert prefix, "A prefix must be specified"
        if self.db.backend == 'sqlite':
            data = self._load_groups_sqlite()
        else:
            # data now in format {(name, product): [(location, code)]
            data = self._load_groups_other_backend()

        counter = count()
        # Group by list of excluded locations into format:
        # {tuple(sorted([location])): [RoW activity code]}
        grouped_data = self._reformat_rows(data, default_exclusions=default_exclusions)

        self.user_rows = {}
        self.labelled = {}

        if not grouped_data:
            return self.labelled, self.user_rows

        # From row_x: [locations] to (locations): row_x
        existing_reversed = {tuple(v): k for k, v in self.existing.items()}

        # For tuples of excluded locations
        for excluded in sorted(grouped_data):
            # v = list of codes for activities with this RoW definition
            list_of_codes = grouped_data[excluded]
            # If there is already a RoW id for this RoW definition
            try:
                # The list of activities for the existing RoW
                # definition is the one returned above for self.database
                self.labelled[existing_reversed[excluded]] = list_of_codes
            except KeyError:
                # Create a new RoW key.
                key = "{}_{}".format(prefix, next(counter))
                self.labelled[key] = list_of_codes
                self.user_rows[key] = excluded

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
        # AD is the ActivityDataset db table (Model in Peewee) imported from bw2data.backends.peewee
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

        if default_exclusions is True:
            exclusions = DEFAULT_EXCLUSIONS
        elif not default_exclusions:
            exclusions = []
        else:
            exclusions = list(default_exclusions)

        for lst in data.values():
            if 'RoW' not in [x[0] for x in lst]:
                continue
            result[tuple(sorted([x[0] for x in lst if x[0] != "RoW"] +
                                exclusions))
                 ].extend([x[1] for x in lst if x[0] == 'RoW'])
        return result

    def _update_locations_sqlite(self, mapping):
        count = 0

        searchable = self.db.metadata.get('searchable')
        if searchable:
            self.db.make_unsearchable()

        for act in pyprind.prog_bar(self.db):
            try:
                act['location'] = mapping[act['code']]
                act.save()
                count += 1
            except KeyError:
                continue

        if searchable:
            self.db.make_unsearchable()

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
