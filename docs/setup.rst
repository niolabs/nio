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

Most configuration exists in the file `nio.conf` at the root of your project. The configuration format is INI.

communication
`````````````

When running a network of Nio devices, keep one as the master broker and configure the others to talk to it:

.. code-block:: ini

    [communication]
    master=false
    broker_ip_address=192.168.100.41

service
```````

If you have services that auto-start when Nio boots up and it is running on a slow device (like a Raspberry Pi), you may wan those services to start in series to help with the CPU hit:

.. code-block:: ini

    [service]
    async_start=false

rest
````

If you want the Nio REST API to run a different port, maybe because you have multiple Nio instances is one computer:

.. code-block:: ini

    [rest]
    port=8182

Nio environment variables
~~~~~~~~~~~~~~~~~~~~~~~~~

Logging
~~~~~~~

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
