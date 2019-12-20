import os


class Config(object):
    username = os.environ['NPTU_USER']
    password = os.environ['NPTU_PASS']
    attempts = 5
    def configure_credentials(self, new_username, new_password):
        self.username = new_username
        self.password = new_password