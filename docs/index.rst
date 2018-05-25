Rower - a library for creating and using "Rest-of-World" locations
==================================================================

In life cycle assessment, it is common to use a locations called "Rest-of-World", which is defined by the regions in the world not otherwise given. For example, if you defined the production of sugarcane in Brazil in a specific process, then the "Rest-of-World" process would give the production conditions for all sugarcane production outside of Brazil. We can spatially define this, or any other "Rest-of-World", using the `constructive_geometries <https://github.com/cmutel/constructive_geometries>`__ library. This library allows you to consistently define, label, and manage "Rest-of-World" locations for processes in `Brightway <https://brightwaylca.org/>`__ databases. To make our lives a bit easier, we will abbreviate "Rest-of-World" as RoW in this documentation.

Using built-in RoW definitions
------------------------------

``rower`` comes with built-in definitions for all system models of ecoinvent, versions 3.3 and 3.4.

Defining your own RoWs
----------------------


