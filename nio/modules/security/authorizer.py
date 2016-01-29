from nio.modules.proxy import ModuleProxy


class Unauthorized(Exception):

    """ Unauthorized security Exception

    Exception triggered when a user is not authorized to perform a task
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
    def authorize_multiple(cls, user, *tasks, meet_all=True):
        """ Authorize a user against multiple tasks.

        This method is provided as a helper to authorize a user against
        multiple tasks. It will call Authorizer.authorize. You may override
        this in your implementation if it is needed for some reason, but it
        is recommended to leave it.

        Example:
            This example ensures that the user can perform t1 OR t2.
            >>> Authorizer.authorize_multiple(
                    User('test'), SecureTask('t1'), SecureTask('t2'),
                    meet_all=False)

        Args:
            user (User): A user object to check permissions against
            *tasks (list of SecureTasks): In a *args strucutre, pass in any
                number of SecureTask objects to check that the user can perform
            meet_all (bool): Whether or not the user must be able to perform
                all of the tasks or just one. The method will short-circuit
                as expected for either value of this bool.

        Returns:
            None: Same as the Authorizer.authorize method

        Raises:
            Unauthorized: Just like Authorizer.authorize, this will raise
                an exception if the user cannot perform the tasks.
        """
        for task in tasks:
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
