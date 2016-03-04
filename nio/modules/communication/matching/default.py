class DefaultMatching(object):

    @classmethod
    def matches(cls, sub_topics, pub_topics):
        """ Finds out if there is a match between sub and pub topics

        Args:
            sub_topics: subscriber topics
            pub_topics: publisher topics

        For it to match, every key/value the subscriber specifies
        must have a matching in the publisher and no more

        If publisher provides more than what the subscriber is looking for
        there is no match.
        """
        for key, sub_values in sub_topics.items():
            # no match, if a subscriber key does not exist in the publisher
            if key not in pub_topics:
                return False

            # if subscriber does not specified values for given key,
            # assume that it is interested in everything published by key
            if not len(sub_values):
                continue

            # when values for a given key are specified by the subscriber,
            # then all the values provided by publisher need to be present
            # in the subscriber topics, in other words, publisher values for a
            # given key are a subset of subscriber values for same key
            for value in pub_topics[key]:
                if value not in sub_values:
                    return False

        return True
