class SecureTask(object):

    def __init__(self, task, **kwargs):
        super().__init__(**kwargs)
        self.task = task
