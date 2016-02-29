from nio.properties import TimeDeltaProperty, BoolProperty
from nio.modules.scheduler import Job


class Persistence(object):

    """ A block mixin that provides persistence for some variables.

    To use, override the persisted_values function and define which variables
    on your class you wish to have persisted. The values should be strings
    that correspond to the variable names to be saved.

    """

    backup_interval = TimeDeltaProperty(
        visible=False, title='Backup Interval', default={"seconds": 60 * 60})
    use_persistence = BoolProperty(
        title='Load from Persistence?', default=True)

    def __init__(self):
        super().__init__()
        self._backup_job = None

    def persisted_values(self):
        """ Return a dictionary containing the values to be persisted.

        This function should be overriden in a Block that wishes to use
        persistence. Return a dictionary with the key being the key you wish
        to save it under (useful for making changes to the block) and the value
        being the name of the instance attribute to save and load into.

        For example, if your block class has an instance level attribute called
        `_values` and you wish to save it, you could return this dictionary:

            {
               "values": "_values"
            }

        """
        return {}

    def _load(self):
        """ Load the values from persistence """
        self._logger.debug("Loading from persistence")
        for persist_key, persist_target in self.persisted_values().items():
            if self.persistence.has_key(persist_key):
                loaded = self.persistence.load(persist_key)
                self._logger.debug("Loaded value {} for attribute {}".format(
                    loaded, persist_target))
                # Set the loaded value to the attribute on this class
                setattr(self, persist_target, loaded)

    def _save(self):
        """ Save the values to persistence """
        self._logger.debug("Saving to persistence")
        for persist_key, persist_target in self.persisted_values().items():
            self.persistence.store(persist_key, getattr(self, persist_target))
        self.persistence.save()

    def configure(self, context):
        super().configure(context)
        if self.use_persistence():
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
