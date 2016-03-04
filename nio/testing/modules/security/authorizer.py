from nio.modules.security.task import SecureTask
from nio.modules.security.authorizer import Unauthorized


class Authorizer(object):

    @classmethod
    def authorize(cls, user, task):
        if not isinstance(task, SecureTask) or not task.task:
            raise Unauthorized()
