Blocks Types API
================

Nio blocks are the functional pieces of code that generate signals and/or do work with them. Earlier we saw examples of blocks such as CounterIntervalSimulator and Logger. Information and interaction with the blocks of a running Nio instance is available through the blocks types API.

Get API
-------

The get API return a json body with information about a block type based on its name. The following example gets the information for the Logger block:

.. code-block:: bash

    curl -XGET 'http://localhost:8181/blocks_types/Logger' --user 'Admin:Admin'

The result of the previous request is:

.. code-block:: bash

    {
        "name": "Logger",
        "version": "0.0.0",
        "namespace": "blocks.logger.logger_block.Logger",
        "properties": {
            "log_level": {
                "enum": "LogLevel",
                "allow_none": false,
                "options": {
                    "CRITICAL": 50,
                    "INFO": 20,
                    "NOTSET": 0,
                    "ERROR": 40,
                    "WARNING": 30,
                    "DEBUG": 10
                },
                "type": "SelectType",
                "default": "INFO",
                "visible": true,
                "title": "Log Level"
            },
            "name": {
                "allow_none": false,
                "default": null,
                "visible": false,
                "title": "Name",
                "type": "StringType"
            },
            "log_at": {
                "enum": "LogLevel",
                "allow_none": false,
                "options": {
                    "CRITICAL": 50,
                    "INFO": 20,
                    "NOTSET": 0,
                    "ERROR": 40,
                    "WARNING": 30,
                    "DEBUG": 10
                },
                "type": "SelectType",
                "default": "INFO",
                "visible": true,
                "title": "Log At"
            },
            "type": {
                "allow_none": false,
                "type": "StringType",
                "default": null,
                "readonly": true,
                "visible": false,
                "title": "Type"
            },
            "version": {
                "allow_none": false,
                "default": "0.0.0",
                "visible": true,
                "title": "Version",
                "type": "StringType"
            }
        },
        "commands": {
            "properties": {
                "params": {},
                "title": "properties"
            },
            "log": {
                "params": {
                    "phrase": {
                        "default": "Default phrase",
                        "allow_none": false,
                        "title": "phrase"
                    }
                },
                "title": "log"
            }
        },
        "attributes": {
            "output": [
                {
                    "label": "default",
                    "visible": true,
                    "id": "__default_terminal_value",
                    "type": "output",
                    "default": true,
                    "order": 0,
                    "description": ""
                }
            ],
            "input": [
                {
                    "label": "default",
                    "visible": true,
                    "id": "__default_terminal_value",
                    "type": "input",
                    "default": true,
                    "order": 0,
                    "description": ""
                }
            ]
        }
    }

name
    The name of the block type.
version
    The version of the block type that is being used by the running n.io instance.
namespace
    Where the block type is imported from.
properties
    Each of the configurable block attributes and all information about them (i.e. property ``type``, ``name``, ``default`` value, display ``title``, if it can ``allow_none``, etc...).
commands
    Executable commands on running blocks and all information about them (i.e. command ``title`` and ``params``).
attributes
    Any additional block attributes, including Signal ``input`` and ``output`` points.

Get All API
-----------

In addition to getting the details of one block type, specified by name, you can get the details of all blocks in one request:

.. code-block:: bash

    curl -XGET 'http://localhost:8181/blocks_types' --user 'Admin:Admin'


Add API
-------

When n.io starts up, it discovers and adds all the block types in the project. If you want to add a new block to an already runnning n.io instance, you can do that with the Add API. Once the block code is added to the project directory, use the following request to load it into the running n.io instance:

.. code-block:: bash

    curl -XPUT 'http://localhost:8181/blocks_types/Logger' --user 'Admin:Admin'

Update API
----------

When n.io starts up, it discovers and adds all the block types in the project. When block code is changed in a project (likely as a result of upgrading to a newer version of the block) to an already runnning n.io instance, the running n.io instance needs to be told to use that new updated code. You can do that with the Update API. Once the new block code is updated in the project directory, use the following request to load it into the running n.io instance:

.. code-block:: bash

    curl -XPUT 'http://localhost:8181/blocks_types/Logger' --user 'Admin:Admin'
