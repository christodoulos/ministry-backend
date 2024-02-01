from src.models.apografi import Organization


for org in Organization.objects.all():
    print(org.code)
    ext = org.to_json_enchanced()
