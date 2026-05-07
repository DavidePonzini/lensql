from server.db.admin import User

if __name__ == '__main__':
    for user in User.list_all():
        print(user.username)