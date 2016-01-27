from nio.modules.proxy import ModuleProxy


class Unauthorized(Exception):

    """ Unauthorized security Exception

    Exception triggered when the user using the system is not authorized
    """
    pass


class Authorizer(ModuleProxy):

    @classmethod
    def authorize(cls, user, task):
        """ Ensure a user can perform a task.

        Args:
            user (User): A user object, likely returned by the Authenticator
            task (SecureTask): A task this user can or cannot perform

        Returns:
            None: The method will pass successfully if the user is authorized

        Raises:
            Unauthorized: if the user cannot perform the specified task
        """
        raise NotImplementedError()

    @classmethod
    def authorize_multiple(cls, user, *args, meet_all=True):
        """ Authorize a user against multiple tasks """
        for task in args:
            if meet_all:
                # Since they all need to pass, just try them, if one fails
                # it will raise the exception here
                cls.authorize(user, task)
            else:
                try:
                    cls.authorize(user, task)
                    # We need any of them to pass and this one has, let's
                    # break out and call it done
                    break
                except Unauthorized:
                    # This one didn't work, maybe the next one will, gotta
                    # keep trying
                    pass
        else:
            # Exhausting all of the options is good if we want to meet all.
            # However, if we want to meet any (meet_all = False), then that
            # means that the loop never broke out and we should raise our
            # exception
            if not meet_all:
                raise Unauthorized()
