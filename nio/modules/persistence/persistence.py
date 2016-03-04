from nio.modules.proxy import ModuleProxy


class Persistence(ModuleProxy):

    """ Persistence Module

    This class encapsulates the user-facing interface to NIO's
    persistence layer. Block writers use this module to save dynamic
    data at runtime, allowing it to persist in the block instance
    after a service/instance restart.

    Args:
        name (str): The name of the block whose data will be persisted.

    Example:
        self.persistence.store('foo', 'bar')
        self.persistence.save() # saves the stored k/v store to disk
        val = self.persistence.load('foo') # now val == 'bar'

    """

    # Note: We don't proxy a constructor, the ModuleProxy __init__ will handle
    # the mapping to the proper class for us, so just call super

    def __init__(self, name):
        """ Create a Persistence object for a given name """
        super().__init__(name)

    def store(self, key, value):
        """ Store a key/value datum in memory.

        Args:
            key: The key to store into
            value: The value associated with that key
        """
        raise NotImplementedError()

    def load(self, key, default=None):
        """ Load a value from the k/v store *currently in memory*.

        Args:
            key: The key to lookup in the store.
            default:  The value to return if the key is not present

        Returns:
            value: The value associated with that key

        """
        raise NotImplementedError()

    def has_key(self, key):
        """ Check whether a particular key exists in the persistence store

        Args:
            key: The key in question.

        Returns:
            exists (bool)

        """
        raise NotImplementedError()

    def clear(self, key):
        """ Remove the given key and associated value from the store

        As above, this will not be reflected permanently until
        Persistence.save is called.

        Args:
            key: The key pointing to the data to clear.
        """
        raise NotImplementedError()

    def save(self):
        """ Save the in-memory store to persistence.

        This allows the data therein to persist between instance/service
        restarts.
        """
        raise NotImplementedError()

    @classmethod
    def setup(cls, configuration):
        """ Class method to initialize the Persistence class with a config.

        This method will be called after the ModuleProxy is initialized.

        Args:
            configuration (dict): The dictionary that
                module_init was called with

        Returns:
            None
        """
        raise NotImplementedError()

    @classmethod
    def configure(cls, service_name):
        """ Class method to configure the Persistence class with a service

        This allows us to have a service-by-service namespace for
        persisted block data.

        Args:
            service_name (str): The name of the service constituting this
                                process.

        Returns:
            None

        """
        pass
