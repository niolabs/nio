from unittest.mock import MagicMock
from nio.block.mixins.persistence.persistence import Persistence
from nio.block.base import Block
from nio.util.support.block_test_case import NIOBlockTestCase
from time import sleep


class DummyBlock(Persistence, Block):

    def __init__(self):
        super().__init__()
        self._to_be_saved = 'value'
        self._not_to_be_saved = 'value'
        self._to_be_saved_again = 'another value'

    def persisted_values(self):
        """ Overridden to define what is persisted """
        return {
            "saved_1": "_to_be_saved",
            "saved_2": "_to_be_saved_again"
        }


class TestPersistence(NIOBlockTestCase):

    def get_test_modules(self):
        return super().get_test_modules() | {'persistence'}

    def test_saves_properly(self):
        """ Tests that the mixin saves the right values """
        block = DummyBlock()
        self.configure_block(block, {})
        block.persistence.save = MagicMock()
        block.start()
        # Stop the block to initiate the save
        block.stop()

        # Make sure we called the save function
        block.persistence.save.assert_called_once_with()
        # Make sure the right data was saved
        self.assertTrue(block.persistence.has_key('saved_1'))
        self.assertTrue(block.persistence.has_key('saved_2'))
        self.assertEqual(len(block.persistence._values), 2)
        self.assertEqual(block.persistence.load('saved_1'), 'value')
        self.assertEqual(block.persistence.load('saved_2'), 'another value')

    def test_loads_properly(self):
        """ Tests that the mixin loads into the right values """
        block = DummyBlock()
        self.configure_block(block, {
            'use_persistence': True
        })
        block.persistence._values = {
            "saved_1": "saved value 1",
            "saved_2": "saved value 2"
        }
        # Force the load now - it happened in configure too, but we hadn't
        # mocked the saved values yet
        block._load()

        # Make sure the right data was loaded into the right variables
        self.assertEqual(block._to_be_saved, 'saved value 1')
        self.assertEqual(block._to_be_saved_again, 'saved value 2')

    def test_no_load(self):
        """ Tests that the mixin doesn't load if it's told not to """
        block = DummyBlock()
        block._load = MagicMock()
        self.configure_block(block, {
            'use_persistence': False
        })
        # Make sure load wasn't called
        self.assertFalse(block._load.called)
        # We should have the original values too
        self.assertEqual(block._to_be_saved, 'value')
        self.assertEqual(block._to_be_saved_again, 'another value')

    def test_backup_job(self):
        """ Tests that periodic backups occur """
        block = DummyBlock()
        self.configure_block(block, {
            'backup_interval': {
                'seconds': 1
            }
        })
        block.persistence.save = MagicMock()
        block.start()
        # Give the block time to perform two saves
        sleep(2.5)
        # Stop the block to initiate one more save
        block.stop()

        # We should have had 3 saves, one every second and one on the stop
        self.assertEqual(block.persistence.save.call_count, 3)

        # Make sure the right data was saved
        self.assertTrue(block.persistence.has_key('saved_1'))
        self.assertTrue(block.persistence.has_key('saved_2'))
        self.assertEqual(len(block.persistence._values), 2)
        self.assertEqual(block.persistence.load('saved_1'), 'value')
        self.assertEqual(block.persistence.load('saved_2'), 'another value')

    def test_no_backup(self):
        """ Backup interval of 0 means no backing up """
        block = DummyBlock()
        self.configure_block(block, {
            'backup_interval': {
                'seconds': 0
            }
        })
        self.assertIsNone(block._backup_job)
