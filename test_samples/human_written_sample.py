# quick auth system for the app
import hashlib
from datetime import datetime

class Auth:
    def __init__(self):
        self.users = {}
        self.sess = {}
    
    def reg(self, usr, pwd, email):
        # TODO: add email validation
        if usr in self.users:
            return False
        
        h = hashlib.sha256(pwd.encode()).hexdigest()
        self.users[usr] = {'pwd': h, 'email': email, 'created': datetime.now()}
        return True
    
    def login(self, usr, pwd):
        if usr not in self.users:
            return None
        
        h = hashlib.sha256(pwd.encode()).hexdigest()
        if self.users[usr]['pwd'] == h:
            # FIXME: use proper token generation
            tok = str(hash(usr + str(datetime.now())))
            self.sess[tok] = usr
            return tok
        return None
    
    def check(self, tok):
        return tok in self.sess
    
    def logout(self, tok):
        if tok in self.sess:
            del self.sess[tok]
