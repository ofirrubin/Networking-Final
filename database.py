

class Database:
    def __init__(self, master_key):
        self.master = master_key

    def add_user(self, username, password):
        #  Save user by user name and password encrypted with master key
        return True

    def remove_user(self, username, password):
        # Remove user if username and password is correct
        return True

    def get_file(self, file):
        return b"Ofir Rubin"

    def remove_file(self, file):
        return True
    
