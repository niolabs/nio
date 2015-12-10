Building Your First NIO Application
-----------------------------------

Before we get started, let's go over some key concepts that are central to the NIO platform. In this document, we'll discuss **Blocks**, **Signals**, **Services**, the **NIO Core**, and steps you'll need to take in order to build your first NIO app.

Terminology
~~~~~~~~~~~
* **Instance** - A running, well, instance of the NIO executable.
    - Probably comprises multiple **Services**.
* **Service** - The main organizational component in NIO.
    - Each service maintains a **Block execution** that defines connections between some number of blocks.
    - Maintains its own, unique, configuration.
* **Block** - The fundamental unit of computation in NIO.
    - Written in NIO-flavored Python, blocks either operate on **Signals**, interact with the outside world, or both.
* **Signal** - The fundamental unit of data transfer in NIO.
* **Modules** - Uniform API's designed to provide functionality common to many NIO applications without tying developers to any particular library of implementation.
* **Property** - A configurable field on a block or service.
* **Core** - Everything that NIO does that you don't have to worry about.
    - Manages block communication via signals, inter-process communication, block discovery, and much more.


Blocks
~~~~~~
Here's an example of the most basic possible block, one that accepts incoming signals and passes them along, untouched:

.. code-block:: python

    from nio.common.blocks.base import Block
    from nio.common.discovery import Discoverable, DiscoverableType
    
    @Discoverable(DiscoverableType.block)
    class IDBlock(Block):
    
        def process_signals(self, signals):
    		self.notify_signals(signals)
    		
With no modification, this block will be discovered by a correctly configured NIO service and could run as part of its execution. The core delivers signals notified by other blocks to `IDBlock.process_signals`, where any necessary processing is performed and, optionally, the signals are notified again.

For examples of more complex blocks making use of various modules and higher-order functionality, visit nio_blocks_

.. _nio_blocks: http://github.com/nio-blocks/

Block methods
~~~~~~~~~~~~~

The following methods perform essential block functions and can be reimplemented in custom blocks. If overridden, it is almost always necessary to call the overriden method in the first line of the custom method.

* **Blocks.configure** - This method is called before the block is started. Note that unhandled exceptions here will cause the enclosing service to abort.

* **Blocks.start** - This method is called when the service enclosing is started by nio's core. This is the place to schedule jobs, connect to external services, etc. Note that unhandled exceptions here will not effect the running status of the enclosing service.

* **Blocks.stop** - This method is called when the enclosing service is stopped by nio's core. Any persistent data, running threads, etc. should be cleaned up here.

* **Blocks.notify_signals** - Call this method from your block to forward an arbitrary list of Python objects to any receivers of your custom block. This is the primary output mechanism for blocks.

* **Blocks.process_signals** - This method is called when your block is configured as the receiver of another block in the enclosing service. This is the primary input mechanism for blocks.

Services
~~~~~~~~

Currently, we provide a single service class that has served our purposes quite nicely until now. However, we have left open the possiblility for developers to provide custom service classes for use in their nio projects. Here's an example:

.. code-block:: python

    from nio.common.service.base import Service
    from nio.common.discovery import Discoverable, DiscoverableType
    
    @Discoverable(DiscoverableType)
    class BasicService(Block):
        def start(self):
        	# custom start logic here
        	
So far, the default service has been sufficient for all our internal use cases; by design, much of the logic in your nio project will reside at the block level.
