from . import DATAPATH, RowerDatapackage, Rower
from bw2data import Database
import os


def update_ecoinvent_definitions(new_ei):
    """Update definitions to include new ecoinvent versions.

    ``new_ei`` is a list of imported database names."""

    # Load existing data as a dictionary: "RoW_label": [list of locations]
    existing = RowerDatapackage(Rower.EI_GENERIC).read_data()["Rest-of-World definitions"]

    for name in new_ei:
        print("Processing {}".format(name))
        assert len(Database(name))
        rower = Rower(name)

        # new_data is a dictionary with (tuple of locations): [list of codes]
        new_data = rower._reformat_rows(rower._load_groups_sqlite())

        missing = []

        for tpl in new_data:
            if not any(1 for o in existing.values() if tuple(o) == tpl):
                missing.append(tpl)

        if missing:
            top = max([int(x.split("_")[-1]) for x in existing])
            missing.sort()
            print("Adding {} new RoWs".format(len(missing)))

            missing = {"RoW_{}".format(i + 1 + top): list(o)
                       for i, o in enumerate(missing)}

            existing.update(missing)

        r = Rower(name)
        r.existing = existing
        labelled, user_rows = r.define_RoWs()
        assert not user_rows
        rows_used = {i: j for i, j in existing.items() if i in labelled}
        dp = RowerDatapackage(os.path.join(DATAPATH, "ecoinvent " + name))
        dp.write_data("ecoinvent " + name, rows_used, labelled)

    dp = RowerDatapackage(os.path.join(DATAPATH, "ecoinvent generic"))
    dp.write_data("ecoinvent generic", existing)
