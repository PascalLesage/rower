Rower - a library for creating and using "Rest-of-World" locations
==================================================================

In life cycle assessment, it is common to use a locations called "Rest-of-World", which is defined by the regions in the world not otherwise given. For example, if you defined the production of sugarcane in Brazil in a specific process, then the "Rest-of-World" process would give the production conditions for all sugarcane production outside of Brazil. We can spatially define this, or any other "Rest-of-World", using the `constructive_geometries <https://github.com/cmutel/constructive_geometries>`__ library. This library allows you to consistently define, label, and manage "Rest-of-World" locations for processes in `Brightway <https://brightwaylca.org/>`__ databases. To make our lives a bit easier, we will abbreviate "Rest-of-World" as RoW in this documentation.

Using built-in activity maps
----------------------------

Using built-in RoW definitions
------------------------------

``rower`` comes with built-in definitions for all system models of ecoinvent, versions 3.3 and 3.4. Here is how to use these definitions on an existing database "example":

.. code-block:: python

    from rower import Rower
    instance = Rower("example")

Defining your own RoWs
----------------------

Potential gotchas
-----------------

* You can have more than one RoW activity per combination of name and reference product - they will both get relabeled to the same new RoW.
* The same RoW label will be used for each unique RoW definition, so one RoW label can be applied to many activities.
* RoW will be defined and relabeled, even if no regions are excluded.
* Data package folder names are chosen be users, so may not match the database, even if they say they do.
* ``Rower.save_data_package`` will delete an existing data package completely; it will not do a partial update.
