HOST = None
PORT = None
DBNAME = None

USERNAME = None
PASSWORD = None

def are_credentials_set():
    for cred in (HOST, PORT, DBNAME, USERNAME, PASSWORD):
        if cred is None:
            return False
    return True