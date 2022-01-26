

class Chat:
    def __init__(self, id1, id2):
        self.pending = {id1: [], id2: []}

    def __contains__(self, id_):
        return id_ in self.pending.keys()

    def __getitem__(self, item):
        return self.pending[item]

    def remove_pended(self, id_, msg):
        if id_ in self:
            self.pending[id_].remove(msg)

    def add_pending(self, id_, msg):
        if id_ in self:
            self.pending[id_].append(msg)


class DatabaseConnection:
    def __init__(self, **kwargs):
        self.chats = {}
        self.users = {}

