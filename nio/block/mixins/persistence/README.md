Persistence (Mixin)
===========

A mixin to take care of some common persistence tasks in blocks.

This mixin allows a block developer to define some class-level variables to 
be persisted through service restarts. Specificially, the mixin performs (or
allows the block to be configured to perform) these tasks:
 
 * Loading values into instance variables upon block configuration
 * Saving values on block stop
 * Periodic backing up of values in case of service crash

Properties
--------------

-   **Backup Interval**: (hidden attribute) How often to periodically backup the saved values
-   **Load from Persistence?**: Whether or not to load from persistence when the block is configured. Often times, a block may be configured to perform a different action and it is not desirable to load previously persisted values. Unchecking this option will prevent the block from loading when it is configured.

Dependencies
------------
None

Commands
--------
None

Input
-----
None

Output
------
None

Example Usage
-------------

In the block, override the method `persisted_values` to return a dict with all attributes that should be peristed. Dict keys are the names to save as and the values are the attribute names.

```python
class MyBlock(Persistence, Block):

    def __init__(self):
        self._persisted_attr = None

    def persisted_values(self):
        return { "attr": "_persisted_attr" }
```

For unit tests, setup the persistence module to use the default in-memory persistence. Mock Persistence during configure to assert calls to `store` and `save`. Optionally, set return values for `load` and `has_key` to load values from persistence.

```python
class TestMyBlock(NIOBlockTestCase):

    def get_test_modules(self):
        return super().get_test_modules() + ['persistence']

    def get_module_config_persistence(self):
        """ Make sure we use in-memory persistence """
        return {'persistence': 'default'}

    def test_persistence(self):
        """ Test that the block uses persistence """
        blk = MyBlock()
        with patch('nio.common.block.base.Persistence') as persist:
            persist.return_value.load.return_value = "I was persisted!"
            persist.return_value.has_key.side_effect = \
                lambda key: key in ["attr"]
            self.configure_block(blk, {})
        # Confirm that the attr was loaded from persistence
        self.assertEqual(blk._persisted_attr, "I was persisted!")
        # Check that stats are persisted at the end
        blk.start()
        blk.stop()
        blk.persistence.store.assert_called_once_with(
            "attr", blk._persisted_attr
        )
        blk.persistence.save.assert_called_once_with()
```
