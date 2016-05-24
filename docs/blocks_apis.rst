Blocks API
==========

Configured instances of a n.io block type are simply referred to as blocks. Earlier we saw an example of a Logger block instance created with the name ``Log``. Information and interaction with the block configurations of a running Nio instance is available through the blocks API.

Get API
-------

The get API returns a json body with information about a block based on its name. The following example gets the information for the configured Logger block ``Log``:

.. code-block:: bash

    curl -XGET 'http://localhost:8181/blocks/Log' --user 'Admin:Admin'

The result of the previous request is:

.. code-block:: bash

    {
        "type": "Logger",
        "name": "Log"
        "version": "0.0.0",
        "log_level": "INFO",
        "log_at": "INFO",
    }

type
    The block type of the block configuration.
version
    The version of the block type when the block configuration was created.
name
    The name of the block configuration. This must be unique among all blocks, regardless of type.
log_level
    Level at which the block logs messages. Messages are logged for the specified ``log_level`` and all higher level.
log_at
    ``log_at`` is specific to the ``Logger`` block. It is the level at which Signal enter the block will be logged at. ``log_level`` needs to be at least ``log_at`` or lower for the Signals ot be logged.

Each block type has its own unique properties that will be viewable here.

Get All API
-----------

In addition to getting the details of one block configuration, specified by name, you can get the details of all block configurations in one request:

.. code-block:: bash

    curl -XGET 'http://localhost:8181/blocks' --user 'Admin:Admin'

Create API
----------

Update API
----------

Delete API
----------
