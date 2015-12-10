NIO Command Line Tools
----------------------

NIO exposes a rich API for interacting with running instances. We provide a robust browser-based graphical user interface to same, but such interfaces are rarely well suited to automation of tasks and rapid context switching. For this reason, we provide the **nio** command line tool, which allows users and administrators to start, stop, view, configure, and build blocks and services from a UNIX command line.

Here's an example:

.. code-block:: bash

    $ nio ls services TestPost
    +--------------+---------+
    | TestPost     |         |
    +--------------+---------+
    | auto_start   |   True  |
    | log_level    |  DEBUG  |
    | mappings     |   NULL  |
    | sys_metadata |   NULL  |
    | type         | Service |
    +--------------+---------+

**nio** is configurable by python `.ini` file. By default, it looks in `$HOME/.config/nio-cli.ini` under the section **nio** for a hostname, port, username, and password. The path to the `.ini` file is configurable by command-line option, but make sure you put all the **nio** options under the appropriate section. Here's an example:

.. code-block:: conf

    [DEFAULT]
    host = localhost
    port = 8181
    username = User
    password = User
    
    [nio]
    username = Admin
    password = Admin
    
**nio** exposes a number of sub-commands to perform various tasks. Each, and its syntax, is represented by one of the following subsections.

new
~~~

This subcommand creates a fresh nio project from the official [project tempalte](https://github.com/nio-blocks/project_template). A new project folder will be made inside the current directory.

.. code-block:: bash

    $ nio new project_name
    $ cd project_name
    $ ls
    blocks etc extras README.md nio.conf nio.env

add
~~~

This subcommand adds new block types to and existing nio project. By defualt they are pulled from the official [nio GitHub](https://github.com/nio-blocks) account.

This must be run from the root level of the project that you want to add the blocks too. One ore morse lists can be added at a time.

.. code-block:: bash

    $ nio add logger
    $ ls blocks
    logger
    $ nio add counter simulator
    $ ls blocks
    counter logger simulator

list (ls)
~~~~~~~~~

When called without a specific block or service name, this subcommand lists all the blocks or services loaded in the instance along with a common subset of properties:

.. code-block:: bash**

	$ nio ls blocks
	+----------------+--------------+-----------+
	|      name      |     type     | log_level |
	+----------------+--------------+-----------+
	| Deb            |  Debouncer   |   ERROR   |
	| fil            |    Filter    |   ERROR   |
	| PostToMe       |  PostSignal  |   DEBUG   |
	| CountMe        |   Counter    |   ERROR   |
	| count          |   Counter    |   ERROR   |
	| FacebookPoster | FacebookPost |   ERROR   |
	| TwitterPoster  | TwitterPost  |   DEBUG   |
	| SignalLogger   | LoggerBlock  |   DEBUG   |
	+----------------+--------------+-----------+
	
When called with a block or service name, **nio** outputs a list of all the properties on that block or service:

.. code-block:: bash

    $ nio ls blocks TwitterPoster
    +------------------------+----------------------------------------------------+
    | TwitterPoster          |                                                    |
    +------------------------+----------------------------------------------------+
    | creds                  |                                                    |
    | +-> oauth_token        |                XXXXXXXXXXXXXXXXXXX                 |
    | +-> consumer_key       |                XXXXXXXXXXXXXXXXXXX                 |
    | +-> oauth_token_secret |                XXXXXXXXXXXXXXXXXXX                 |
    | +-> app_secret         |                XXXXXXXXXXXXXXXXXXX                 |
    | log_level              |                       DEBUG                        |
    | status                 |                 What the {{$foo}}?                 |
    | type                   |                    TwitterPost                     |
    +------------------------+----------------------------------------------------+
	
To list the HTTP commands (with enumerated parameters) exposed by a particular block or service, simply append the '--cmd' flag:

.. code-block:: bash

   	$ nio ls services TestPost --cmd
   	+---------+------------------+
	| command |        0         |
	+---------+------------------+
	| log     | phrase: (string) |
	+---------+------------------+
	
To view the block execution of a particular service (in tabular form), append the '--exec' flag:

.. code-block:: bash

    $ nio ls services SomeService --exec
    +--------------+--------------+
    | Output Block |      0       |
    +--------------+--------------+
    |     met      | SignalLogger |
    |   CountMe    |     Deb      |
    |     Deb      | SignalLogger |
    |   PostToMe   |   CountMe    |
    +--------------+--------------+
   	
	
command (co)
~~~~~~~~~~~~

This subcommand allows you to send commands to live instances. Because of the way blocks are referenced within NIO, you must supply the target command, the name of the service, and (if you are commanding a block) the name of the block instance.

.. code-block:: bash

	$ nio co start TestPost
	`http://localhost:8181/services/TestPost//start` was processed successfully
	
The syntax for adding parameters to commands is as follows:

.. code-block:: bash
	
	$ nio co log TestPost SignalLogger --args 'phrase=foobar'
	
Passing the `--auto` (`-a`) flag to command tells **nio** to read command arguments from the command line.
	
If the command response body is non-empty, its contents are printed to stdout; otherwise, the terminal remains silent.

config (cfg)
~~~~~~~~~~~~

This subcommand allows you to configure new and existing block and service instances while the NIO instance is live. Of course, a given service won't load a new configuration until its next startup cycle, but any changes you make here will hang around until then. Note that this is an interactive portion of the utility.

NB: If you want to automate configuration, it may be easier to make your updates directly via HTTP PUT requests. We may add a feature like this in future.

.. code-block:: bash

    $ nio cfg services TestPost
    
    log_level (select):
    Using current value: DEBUG
    
    auto_start (bool): T
    
If the block or service you're configuring holds an Object Property, each property held by that object is configured in turn:

.. code-block:: bash

    $ nio cfg blocks TwitterPoster
    
    creds (object):
    +->oauth_token (str):
    Using current value: XXXXXXXX
    +->consumer_key (str):
    Using current value: XXXXXXXX
    +->app_secret (str):
    Using current value: XXXXXXXX
    +->oauth_token_secret (str):
    Using current value: XXXXXXXX

    status (str): "It's gonna rain"

    log_level (select):
    Using current value: DEBUG
    
`nio` interprets attempts to configure nonexistent resources as creation events. That is, the following sequence results in the creation of a block called "CriticalLogger", which can subsequently be added to any service execution in the system.

.. code-block:: bash

    $ nio cfg blocks AnotherLogger
    NIOClient: NIO returned status 404
    type (str): LoggerBlock
    log_level (select): CRITICAL
    +----------------------+-------------+
    | Name: CriticalLogger |             |
    +----------------------+-------------+
    | log_level            |   CRITICAL  |
    | type                 | LoggerBlock |
    +----------------------+-------------+
    
Currently, NIO ships with only one service type (`Service`), but developers are free to add both new blocks and services as they wish.

update
~~~~~~

The `update` subcommand command is very simple but very important. It compels a running NIO instance to rediscover each of the block types in its argument list, allowing developers to perform live updates to block implementations. For example, after updating the implementation for the LoggerBlock:

.. code-block:: bash

    $ nio update LoggerBlock
    
If all the block types are valid, standard out should remain silent. 

NB: The current implementations of a running block will remain in memory until the enclosing service is restarted.


build (ln)
~~~~~~~~~

This final subcommand allows you to build NIO services from the command line by creating links between blocks that are loaded into the sytem. First, let's use `ls` to check out the execution of the `TestPost` service and view the list of blocks available in the system.

.. code-block:: bash

    $ nio ls services TestPost --exec
    +--------------+--------------+
    | Output Block |      0       |
    +--------------+--------------+
    |     met      | SignalLogger |
    |   CountMe    |     Deb      |
    |     Deb      | SignalLogger |
    |   PostToMe   |   CountMe    |
    +--------------+--------------+
    
    $ nio ls blocks
    +----------------+--------------+-----------+
    | name           |     type     | log_level |
    +----------------+--------------+-----------+
    | count          |   Counter    |   ERROR   |
    | met            |   Metrics    |   ERROR   |
    | SignalLogger   | LoggerBlock  |   DEBUG   |
    | PostToMe       |  PostSignal  |   DEBUG   |
    | Deb            |  Debouncer   |   ERROR   |
    | FacebookPoster | FacebookPost |   ERROR   |
    | CountMe        |   Counter    |   ERROR   |
    | fil            |    Filter    |   ERROR   |
    | TwitterPoster  | TwitterPost  |   DEBUG   |
    +----------------+--------------+-----------+

    
Finally, we can use `build` to connect the outputs of `CountMe` and `PostToMe` to the input of another block!

.. code-block:: bash

    
    $ nio build TestPost CountMe TwitterPoster
    +--------------+--------------+---------------+
    | Output Block |      0       |       1       |
    +--------------+--------------+---------------+
    |   CountMe    |     Deb      | TwitterPoster |
    |     met      | SignalLogger |               |
    |   PostToMe   |   CountMe    | TwitterPoster |
    |     Deb      | SignalLogger |               |
    +--------------+--------------+---------------+
    
The build subcommand behaves somewhat similarly to the UNIX `cp` command in that it takes a series of *n* block instances of which the firs *n-1* represent "source" blocks, while the *n*th block is the single sink.

Additionally, if you need to add a block `fil` to a service without connecting it to any other blocks (e.g. a block which simply serves an HTTP endpoint):

.. code-block:: bash

    $ nio build TestPost fil
    +--------------+--------------+---------------+
    | Output Block |      0       |       1       |
    +--------------+--------------+---------------+
    |   CountMe    |     Deb      | TwitterPoster |
    |     met      | SignalLogger |               |
    |   PostToMe   |   CountMe    |               |
    |     Deb      | SignalLogger | TwitterPoster |
    |     fil      |              |               |
    +--------------+--------------+---------------+
    
In this case, `fil` has no receivers, and any that you add will appear starting from column 0 of the execution table.

Finally, if you'd like to remove blocks/block connections instead of create them, just append the `-rm` option to any of the above `build` invocations.

Voila! You're now up and running with the NIO command line interface. Happy hacking!
