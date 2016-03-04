from nio.properties import TimeDeltaProperty, BoolProperty
from nio.modules.persistence import Persistence as PersistenceModule
from nio.modules.scheduler import Job


class Persistence(object):

    """ A block mixin that provides persistence for some variables.

    To use, override the persisted_values function and define which variables
    on your class you wish to have persisted. The values should be strings
    that correspond to the variable names to be saved.

    """

    backup_interval = TimeDeltaProperty(
        visible=False, title='Backup Interval', default={"seconds": 60 * 60})
    load_from_persistence = BoolProperty(
        title='Load from Persistence?', default=True)

    def __init__(self):
        super().__init__()
        self._persistence = None
        self._backup_job = None

    def persisted_values(self):
        """ Return a list containing the values to be persisted.

        This function should be overriden in a Block that wishes to use
        persistence. Return a list of the names of the instance level variables
        to save.

        For example, if your block class has an instance level attribute called
        `_values` and you wish to save it, you would return this list:
            ["_values"]
        """
        return []

    def _load(self):
        """ Load the values from persistence """
        self.logger.debug("Loading from persistence")
        for persisted_var in self.persisted_values():
            if self._persistence.has_key(persisted_var):
                loaded = self._persistence.load(persisted_var)
                self.logger.debug("Loaded value {} for attribute {}".format(
                    loaded, persisted_var))
                # Set the loaded value to the attribute on this class
                setattr(self, persisted_var, loaded)

    def _save(self):
        """ Save the values to persistence """
        self.logger.debug("Saving to persistence")
        for persisted_var in self.persisted_values():
            self._persistence.store(
                persisted_var, getattr(self, persisted_var))
        self._persistence.save()

    def configure(self, context):
        super().configure(context)
        # Create a persistence object using the block's name
        self._persistence = PersistenceModule(self.name())
        if self.load_from_persistence():
            self._load()

    def start(self):
        super().start()

        # If we have configured a backup interval, set up the job to
        # periodically save to persistence
        if self.backup_interval().total_seconds() > 0:
            self._backup_job = Job(self._save, self.backup_interval(), True)

    def stop(self):
        if self._backup_job:
            self._backup_job.cancel()

        # Do one last save before stopping
        self._save()
        super().stop()
