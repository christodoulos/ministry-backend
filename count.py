from src.models.apografi.organization import Organization
from src.models.apografi.organizational_unit import OrganizationalUnit

orgs_count = Organization.objects.count()

distinct_organization_codes = OrganizationalUnit.objects.distinct("organizationCode")
orgs_with_units_count = len(distinct_organization_codes)

print(f"Σύνολο οργανισμών: {orgs_count}")
print(f"Σύνολο οργανισμών με μονάδες: {orgs_with_units_count}")
