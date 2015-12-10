Block Development
-----------------

Module logging
~~~~~~~~~~~~~~

Sometimes your blocks will import python modules that use python logging. It is possible to configure the log level of those to match your block. The recommended place for that is in the `configure` method.

.. code-block:: python

    import requests

    class NewBlock(Block):
         
         def configure(self, context):
             super().configure(context)
             logging.getLogger('requests').setLevel(self._logger.logger.level)

Note that all imports of a python module in a service will share the same log level. So if mutliple blocks in one service set the log level to different levels, unknown behavior will occur as the log level will be chosen from whichever block configures last.
