from src.models.apografi.organization import Organization
from src.models.apografi.organizational_unit import OrganizationalUnit


def check_extended_reprs():
    for org in Organization.objects.all():
        _ = org.to_json_enchanced()

    for unit in OrganizationalUnit.objects.all():
        _ = unit.to_json_enchanced()


if __name__ == "__main__":
    check_extended_reprs()
