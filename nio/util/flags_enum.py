import copy


class InvalidFlag(Exception):
    pass


class FlagsEnum(object):

    """Adds flag like functionality to an enum type

    For example:
        class Status(Enum):
            started = 1
            stopped = 2
            error_1 = 3
            error_2 = 4

        status = FlagsEnum(Status)
        status.add(Status.started)
        ....
        # an 'error_1' occurred
        status.add(Status.error_1)
        # Note that 'started' is still set
        ....
        # system recovered
        status.remove(Status.error_1)
        # Note: 'started' still remains, back to normal

    """

    def __init__(self, enum, default_flag=None,
                 status_change_callback=None):
        """ Create a new FlagsEnum instance.

        Args:
            enum (Enum): the enum from which flags are accepted
            default_flag (Enum): optional initial flag
            status_change_callback (callable): Method to call when
                detected a change in the flags value.

        Returns:
            None
        """
        super().__init__()

        self._enum = enum
        self._status_change_callback = status_change_callback
        self._flags = {}

        self.clear()
        if default_flag:
            self.add(default_flag)

    def _validate_flag(self, flag):
        """ Validates if given flag is within the range of the enum values

        Args:
            flag (value within the enum): the flag to check against

        Returns:
            None

        Raises:
            InvalidFlag
        """
        if flag not in self._enum:
            raise InvalidFlag('set, Invalid flag')

    def add(self, flag):
        """ Adds a flag value to the current set of flags

        Args:
            flag (value within the enum): the flag to add

        Returns:
            None

        Example:
            status = FlagsEnum(Status)
            status.add(Status.created)
        """
        self._validate_flag(flag)

        # make sure flag is not already set
        if not self._flags[flag.name]:

            # save old status to send along with changed status
            old_status = copy.deepcopy(self)
            self._flags[flag.name] = True
            if self._status_change_callback:
                self._status_change_callback(old_status, self)

    def remove(self, flag):
        """ Removes a flag value from the current set of flags

        Args:
            flag (value within the enum): the flag to remove

        Returns:
            None

        Example:
            status = FlagsEnum(Status)
            status.remove(Status.created)
        """
        self._validate_flag(flag)

        # make sure flag is set
        if self._flags[flag.name]:

            # save old status to send along with changed status
            old_status = copy.deepcopy(self)
            self._flags[flag.name] = False
            if self._status_change_callback:
                self._status_change_callback(old_status, self)

    def set(self, flag):
        """ Sets a flag, override any flags previously added

        Args:
            flag (value within the enum): the flag to set

        Returns:
            None

        Example:
            status = FlagsEnum(Status)
            # set status to be 'created'
            status.set(Status.created)
            # set status to be 'created, error'
            status.add(Status.error)
            # override previous status, set it to 'configured'
            status.set(Status.configured)
        """
        self._validate_flag(flag)

        # save old status to send along with changed status
        old_status = copy.deepcopy(self)
        change_occurred = False
        # set all flags but intended flag to False
        for key in self._flags.keys():
            if self._flags[key] and key is not flag.name:
                self._flags[key] = False
                change_occurred = True

        # set intended flag if not already set
        if not self._flags[flag.name]:
            self._flags[flag.name] = True
            change_occurred = True

        if change_occurred and self._status_change_callback:
            self._status_change_callback(old_status, self)

    def is_set(self, flag):
        """ Checks if a flag is set

        Args:
            flag (value within the enum): the flag to check against

        Returns:
            True if flag is set, False otherwise

        """
        self._validate_flag(flag)
        return self._flags[flag.name]

    def clear(self):
        """ Resets all possible flag values

        Returns:
            None

        """
        for value in self._enum:
            self._flags[value.name] = False

    @property
    def flags(self):
        """ Provides flag values

        Returns:
            Flag values

        """
        return self._flags

    @flags.setter
    def flags(self, flags):
        """ Allows to set more than one flag at the same time

        Args:
            flags: flags to set

        Returns:
            None

        """

        # save old status to send along with changed status
        old_status = copy.deepcopy(self)
        change_occurred = False
        for key in flags.keys():
            if key in self.flags and self.flags[key] != flags[key]:
                change_occurred = True
                break

        self._flags = copy.deepcopy(flags)
        if change_occurred and self._status_change_callback:
            self._status_change_callback(old_status, self)

    @property
    def name(self):
        """ Provides a string with all flags currently set

        Returns:
            strings with all flag names currently set

        Example:
            status = FlagsEnum(Status)
            print(status.name)
        """
        statuses = ""
        for key in self._flags:
            if self._flags[key]:
                statuses += "{0}, ".format(key)
        return statuses[:-2]

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __eq__(self, rhs):
        """ Check if current settings matches the flag

        Args:
            rhs (flag or instance): right hand side part of equality
                setting to match to

        Returns:
            True or False

        """
        if isinstance(rhs, FlagsEnum):
            for key in self._flags:
                if key not in rhs.flags or rhs.flags[key] != self.flags[key]:
                    return False
        else:
            flag = rhs
            self._validate_flag(flag)
            if not self.is_set(flag):
                return False
            # make sure that all others are turned off
            for key in self._flags.keys():
                if key != flag.name and self._flags[key]:
                    return False

        return True

    def __getstate__(self):
        """ Make sure the object is able to be pickled.

        This method allows control over pickling, removes callback field
        which is not picklable.

        Returns:
            Fields to serialize

        """
        # make sure callback like attribute is present, since once it is
        # cloned once it will not be present any longer.
        if "_status_change_callback" in self.__dict__:
            # copy the dict since it will be changed
            odict = self.__dict__.copy()
            # remove callback entry
            del odict['_status_change_callback']
            return odict
        else:
            return self.__dict__
