Block Router
------------

The block router is what manages the passing of signals from block to block. nio comes packaged with a variety of block routers and each is configurable to control behavior.

Configuration
~~~~~~~~~~~~~

Configuration of block routers is set in the block_router.cfg file in the project's etc/ directory.

*   clone_signals: False
   *   If clone_signals is True, then the block router will perform a deepcopy on the signals whenever they are split and passed to more than one block.
*   max_workers: 50
   *   When using ThreadedPoolExecutorRouter, this is the max number of workers.

Block Router Types
~~~~~~~~~~~~~~~~~~

Each nio project can specify a default block router in nio.conf by setting block_router.

In addition to specifying the block router for the project, each service can use its own block router by setting block_router on the service configuration.

**BaseBlockRouter**

Default block router.

nio.common.block.router.base.BaseBlockRouter


**ThreadedBaseBlockRouter**

Threaded block router.

nio.common.block.router.threaded.ThreadedBaseBlockRouter


**ThreadedPoolExecutorRouter**

Threaded block router that makes used of thread pools (https://docs.python.org/3/library/concurrent.futures.html).

nio.common.block.router.thread_pool_executor.ThreadedPoolExecutorRouter
