Setup
=====

Setup
-----

This section provides information on how to install nio, configure it to your liking and get it running.

Nio binaries
~~~~~~~~~~~~

Nio has many varieties in the form of installable and runable binaries. While each binary uses the same Nio Framework and blocks, the functionality and features of a binary can vary greatly. For example, one binary may have minimal features for the sake of running on lower power devices, while another may incorporate a plethora of security enhancements for running in an enterprise environment.

When you install the binary, the required Nio Framework and other Python dependences will be installed as well.

Supported platforms
~~~~~~~~~~~~~~~~~~~

Nio can run on any computer with Python 3.4 (or greater), the ability to pip install additional (but minimal Python libraries) and a file system.

Installation
~~~~~~~~~~~~

After downloading a Nio binary, use pip to install it:

.. code-block:: bash

    pip3 install <nio-binary.whl>

You will also want to install the Nio CLI to assist in the creation and running of a Nio project:

.. code-block:: bash

    pip3 install nio-cli

Creating and running a project
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a project with the Nio CLI and the run nio from the root of that project:

.. code-block:: bash

    nio new first_project
    cd first_project
    nio server

Running as a daemon
~~~~~~~~~~~~~~~~~~~

To run Nio in the background, use the `-d` flag:

.. code-block:: bash

    nio server -d

Configuration
-------------

Nio configuration settings generally exist at the root of your project directory.

Nio settings
~~~~~~~~~~~~

Most configuration exists in the file ``nio.conf`` at the root of your project. The configuration format is INI.

communication
`````````````

When running a network of Nio devices, keep one as the master broker and configure the others to talk to it:

.. code-block:: ini

    [communication]
    master=false
    broker_ip_address=192.168.100.41

service
```````

If you have services that auto-start when Nio boots up and it is running on a slow device (like a Raspberry Pi), you may want those services to start in series to help with the CPU hit:

.. code-block:: ini

    [service]
    async_start=false

rest
````

If you want the Nio REST API to run on a different port, perhaps because you have multiple Nio instances on one computer:

.. code-block:: ini

    [rest]
    port=8182

Nio environment variables
~~~~~~~~~~~~~~~~~~~~~~~~~

You can specify project specific environement variabls to be used in configuration files. These variables can used in ``nio.conf``, logging config and block and service property configurations. The values of these variables are not accessible through the Nio REST API so they are a good place for things that need to be kept private. It is common to use these environment variables so that you can run the same project in different environments and change the behavior simply by referencing a different variable file.

The default environment variable file is ``nio.env`` and is located at the project root.

When starting Nio, specify a non-default environment variable file with the ``-e`` flag.

Popular variables and their meaning:

``COMHOST`` - The publically accessible IP address of the master broker.

``PROJECT_ROOT`` - Automatically populated by Nio and used to reference files and directories relative to the project root.

Logging
~~~~~~~

Nio uses Python logging so the same documentation applies. By defauly, the logging file ``logging.json`` is in the ``etc`` directory of your project.

Running as a Service on Linux
-----------------------------

Running as a Service on Windows
-------------------------------

TODO

Project Directory Layout
------------------------

Component Configuration
-----------------------

Module Configuration
--------------------
