class CommunitySearcher:

    def __init__(self, communities):
        self.communities = communities


    def find_community(
        self,
        entity
    ):

        return self.communities.get(entity)


    def get_members(
        self,
        community_id
    ):

        return [
            node
            for node, cid in self.communities.items()
            if cid == community_id
        ]


    def search(
        self,
        entity
    ):

        community_id = self.find_community(entity)

        if community_id is None:
            return {
                "community_id": None,
                "members": []
            }


        return {
            "community_id": community_id,
            "members": self.get_members(
                community_id
            )
        }