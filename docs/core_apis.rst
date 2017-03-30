Core APIs
=========

Nio has a few crucial api endpoints: ``/nio`` and ``/shutdown``.

Nio API
-------

The ``/nio`` endpoint is where you will find information about your running nio instances:

.. code-block:: bash

    curl -XGET 'localhost:8181/nio'

The following json body is returned:

.. code-block:: bash

    {
      "start_time": "2016-05-04 18:26:46.093569",
      "nio": {
        "binary": "nio_full",
        "build": "20160426",
        "version": "2.0.0b4"
      },
      "modules": {},
      "components": {
        "ProjectManager": {},
        "ManagementPublisher": {},
        "BlockManager": {},
        "LogManager": {},
        "ServiceExecutor": {},
        "ConfigMonitor": {},
        "RESTManager": {},
        "ServiceMonitor": {},
        "ServiceManager": {}
      }
    }

- ``start_time`` - Datetime string at which nio was started.
- ``nio``

   - ``binary`` - Name of executable binary that was run against the project.
   - ``build`` - Build version of binary.
   - ``version`` - Version of nio framework, not to be confused with ``build`` which is the version of the ``binary``.


Shutdown API
------------

The ``/shutdown`` endpoint is used to shutdown a running Nio instance.

.. code-block:: bash

    curl -XGET 'localhost:8181/nio'

The following html is returned on a successful shutdown:

.. code-block:: bash

    Shutdown complete
