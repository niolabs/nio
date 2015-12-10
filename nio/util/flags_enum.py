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
        # an error_1 occurred
        status.add(Status.error_1)
        # Note that started is still set
        ....
        # system recovered
        status.remove(Status.error_1)
        # Note: started still remains, back to normal

    """

    def __init__(self, enum, default_flag=None,
                 status_change_callback=None):
        """ Initializes a FlagsEnum instance

        Args:
            enum (Enum): the enum from which flags are accepted

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
        """ Validates if a flag is allowed

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
        if not self._flags[flag.name]:
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
        if self._flags[flag.name]:
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
            status.set(Status.created)
        """
        self._validate_flag(flag)

        old_status = copy.deepcopy(self)
        change_occurred = False
        # set all flags but intended to False
        for key in self._flags.keys():
            if self._flags[key] and key is not flag.name:
                self._flags[key] = False
                change_occurred = True

        # set intended flag
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
            None

        Example:
            status = FlagsEnum(Status)
            status.is_set(Status.created)
        """
        self._validate_flag(flag)
        return self._flags[flag.name]

    def clear(self):
        for value in self._enum:
            self._flags[value.name] = False

    @property
    def flags(self):
        return self._flags

    @flags.setter
    def flags(self, flags):

        old_status = copy.deepcopy(self)
        change_occurred = False
        for key in flags.keys():
            if key in self.flags and self.flags[key] != flags[key]:
                change_occurred = True
                break

        self._flags = flags
        if change_occurred and self._status_change_callback:
            self._status_change_callback(old_status, self)

    @property
    def name(self):
        """ Provides a string with all flags currently set

        Args:
            None

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
        """ Allows control over pickling, removes callback field
        which is not pickable.

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
