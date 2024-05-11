from src.models.user import User

users = User.objects()

for user in users:
    print(user.email)
    for role in user.roles:
        print("\t", role.foreas)
        print("\t", role.monades)
        print("\t", role.role)
        print("\t", role.active)
        print("----")
