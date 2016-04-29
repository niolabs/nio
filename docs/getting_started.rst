Getting Started
===============

Nio is a highly scalable open-source stream processing engine. It allows you to asynchronously process streaming data signals and act on them in real-time. It is generally used as the 'brains' of a real-time application, particularly systems that require distributed processing.

Here are a few sample use-cases that nio could be used for:

* You want to know what people are saying about you on Twitter. Instantaneously get tweets that mention your business, automate responses, identify trends and alert your support team when the number of "help me" tweets passes your acceptable threshold.
* You run a factory or farm and want to optimize workers and the end product. Nio can read from any sensor and act on that data in real-time.

In this getting started tutorial you will learn how to get nio up and running, create a project and build a simple service.

Basic Concepts
--------------

Before you install nio, it's important to understand a few core concepts.

Project
  A nio project is a directory on your computer that contains all the configuration that defines your nio implementation. Projects can run stand-alone or they can be a part of a larger nio network where many nio instances communicate with one another.
Block
  A block is a configurable piece of code that processes data signals. Blocks can generate signals and/or consume signals.
Service
  A service is a runnable piece of nio that defines your application logic. Services define how blocks are connected together.
Signal
  A signal is a unit of data that is passed from block to block within a service. Think of it is a little box of data, containing anything from a temperature reading to a tweet.
Nio Framework
  The nio library is the versioned portion of the nio code. You will install the nio library and then execute that with the appropriate nio binary. Install the framework with pip: ``pip install nio``.
Nio Binary
  Depending on your circumstances, you will run one of many nio binaries. Binaries range in complexity and are often tuned for hardware. If you're tinkering around on a Raspberry Pi, you don't need to run the same binary as a network of a dozen super computers built to analyze hundreds of thousands signals per second.

Installation
------------

Nio requires at least Python 3.4. You will also need pip to install nio and its dependencies. Finally, nio projects are best managed using git and in this tutorial you'll be pulling down a project template from GitHub. Before you install nio, make sure you have all these things:

.. code-block:: bash

    python3 --version
    pip3 --version
    git --version

Once you have these basic prerequisites, you can download and install nio. The binaries are not necesarilly publicly available, so if you don't have a wheel to install, you better make friends with someone who does! You may need to ``sudo`` install if the following doesn't work for you:

.. code-block:: bash

    pip3 install <nio-binary.whl>

Note: Depending on how ``pip`` was installed, the command may be slightly different. You can verify the command to call pip by trying ``pip``, ``pip3``, or ``pip3.4`` with the ``--version`` option. Also, if you have access to the web hosted nio wheels, you can use ``pip3.4 install http://<URL-of-nio-wheels>``. 

Now we're going to install the Nio CLI. While not required to run Nio, it is helpful for setting up a project and running it:

.. code-block:: bash

    pip3 install nio-cli

Creating and Running a Project
------------------------------

Alright, now it's time for things to get interesting. Create a Nio project in your current directory and run it with:

.. code-block:: bash

    nio new first_project
    cd first_project
    nio server

If all goes well, you should see something like the following logs:

TODO: update logs for 2.x

.. code-block:: bash

    [2016-03-04 23:49:41.035] NIO [INFO] [main.WebServer] Server configured on 0.0.0.0:8181
    [2016-03-04 23:49:41.042] NIO [INFO] [main.ServiceManager] Component: ServiceManager status changed from:  to: created
    [2016-03-04 23:49:41.055] NIO [INFO] [main.ServiceManager] Component: ServiceManager status changed from: created to: configuring
    [2016-03-04 23:49:41.109] NIO [INFO] [main.ServiceManager] Component: ServiceManager status changed from: configuring to: configured
    [2016-03-04 23:49:41.123] NIO [INFO] [main.WebServer] Starting server on 0.0.0.0:8181
    [2016-03-04 23:49:41.226] NIO [INFO] [main.WebServer] Server 0.0.0.0:8181 started on 0.0.0.0:8181
    [2016-03-04 23:49:41.226] NIO [INFO] [main.ServiceManager] Component: ServiceManager status changed from: configured to: starting
    [2016-03-04 23:49:41.227] NIO [INFO] [main.ServiceManager] Component: ServiceManager status changed from: starting to: started

You can see that we now have a web server running on port 8181. This is how you will communicate with Nio. Open up a new terminal window and verify that you can access the api by hitting the /nio endpoint:

.. code-block:: bash

    curl localhost:8181/nio

Adding Blocks to a Project
~~~~~~~~~~~~~~~~~~~~~~~~~~

Before we move on, you're going to want to add some blocks to your project. Press ctrl-c to ext nio. We'll add four popular blocks to get you started:

.. code-block:: bash

    nio add logger simulator filter dynamic_fields

Explore Nio
-----------

If you don't have Nio running already, do that now:

.. code-block:: bash

    nio server

Builder
~~~~~~~

While we could continue using the REST API directly, we don't need to do that in this tutorial. Instead, we'll use this handy web app:

.. code-block:: bash

    open http://builder.n.io


It's looking pretty empty in there but you should at least see a list of blocks on the left. While it won't get too exciting quite yet, we'll start by building a very basic service to simulate and log signals. By default, the projects logs go to standard out as well as to files in the ``logs`` directory of your project folder.

Start by clicking the "Add Service" button and name your service "SimulateAndLog".

Now that we have a service, we'll add a CounterIntervalSimulator block and a Logger block. On the left, click on Logger and drag it onto the service canvas. Go ahead give it the name "Log". Do the same with CounterIntervalSimulator and name it "Simulate". Now connect these blocks by clicking and dragging on the output terminal of Simulate and release it on the input terminal of "Log".

Once you are satisfied with your service, click "Save Service".

Running Services
~~~~~~~~~~~~~~~~

By now I'm sure you're more than ready to see something happen. Click "Start Service" and you should see some logs appear in the terminal where you ran nio from.

TODO: update logs for 2.x

.. code-block:: bash

    [2016-03-05 00:32:05.189] NIO [INFO] [SimulateAndLog.Log] Block: Log (type: LoggerBlock) status is configured
    [2016-03-05 00:32:05.191] NIO [INFO] [SimulateAndLog.service] Service: SimulateAndLog status changed from: configuring to: configured
    [2016-03-05 00:32:05.193] NIO [INFO] [SimulateAndLog.service] Service: SimulateAndLog status changed from: configured to: starting
    [2016-03-05 00:32:05.199] NIO [INFO] [SimulateAndLog.Log] Block: Log (type: LoggerBlock) status is starting
    [2016-03-05 00:32:05.199] NIO [INFO] [SimulateAndLog.Log] Block: Log (type: LoggerBlock) status is started
    [2016-03-05 00:32:05.200] NIO [INFO] [SimulateAndLog.service] Service: SimulateAndLog status changed from: starting to: started
    [2016-03-05 00:32:05.200] NIO [INFO] [SimulateAndLog.Log] {'sim': 0}
    [2016-03-05 00:32:05.201] NIO [INFO] [main.ServiceManager] Service: SimulateAndLog with process identifier(pid): 65638 has started
    [2016-03-05 00:32:06.203] NIO [INFO] [SimulateAndLog.Log] {'sim': 1}
    [2016-03-05 00:32:07.204] NIO [INFO] [SimulateAndLog.Log] {'sim': 0}
    [2016-03-05 00:32:08.204] NIO [INFO] [SimulateAndLog.Log] {'sim': 1}
    [2016-03-05 00:32:09.203] NIO [INFO] [SimulateAndLog.Log] {'sim': 0}
    [2016-03-05 00:32:10.204] NIO [INFO] [SimulateAndLog.Log] {'sim': 1}

Click "Stop Service" when you're ready to move on.

Configuring Blocks
~~~~~~~~~~~~~~~~~~

So far we're only using the default behavior of these blocks. Why don't you try changing things up by configuring the Simulate block. Click on the block and take a look at it's properties on the right side of the builder. You'll notice that Interval is configured to 1 second. Change that to 2 and then click "Save Block". Now when you start the service, you'll only see signals logged every other second.

Commanding Blocks and Services
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Commands are a way to execute code in a block or service. Techincally, you've already commanded services with "start" and "stop".

Running blocks can also be commanded. With the SimulateAndLog service running, select the Log block and then click the "Command Block" button. Select "log", type in a phrase and then "Execute Command". You'll see your phrase logged alongside the simulated signals.

Conclusion
----------

At this point you should feel comfortable installing nio, creating a project with blocks and configuring and running services. You can find block `documentation on GitHub <https://github.com/nio-blocks>`_.
