class LooseMatching(object):

    @classmethod
    def matches(cls, sub_topics, pub_topics):
        """ Finds out if there is a match between sub and pub topics

        Args:
            sub_topics: subscriber topics
            pub_topics: publisher topics

        For it to match, there should be a key where the publisher
        publishes something the subscriber cares about
        """

        # empty lists, publish everything, subscribe everything
        if not len(sub_topics) and not len(pub_topics):
            return True

        matching_keys = [key for key in sub_topics.keys()
                         if key in pub_topics.keys()]
        if not matching_keys:
            return False

        for key, sub_values in sub_topics.items():
            if key not in pub_topics:
                continue

            # if publishing everything from key, subscriber is interested
            if not len(pub_topics[key]):
                return True

            # if subscriber list is empty, it means subscribes to
            # everything being published by key
            if not len(sub_values):
                return True

            match_for_key = False
            for value in pub_topics[key]:
                # publishing something subscriber cares about is enough
                # for a match
                if value in sub_values:
                    match_for_key = True
                    break

            # a common key existed, but not a single match
            if not match_for_key:
                return False

        return True
