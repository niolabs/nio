class DefaultMatching(object):
    @classmethod
    def matches(cls, sub_topics, pub_topics):
        """ For it to match, for every key/topic the subscriber cares about
        the publisher must have a matching value and no more
        """
        for key, sub_values in sub_topics.items():
            if key not in pub_topics:
                return False

            # if subscriber list is empty, it means subscribes to
            # everything being published by key
            if not len(sub_values):
                continue

            # publisher values are a subset of what subscriber is looking for
            for value in pub_topics[key]:
                if value not in sub_values:
                    return False

        return True
