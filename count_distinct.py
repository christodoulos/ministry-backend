from src.models.apografi import OrganizationalUnit

# Get a list of distinct organizationCodes
distinct_organization_codes = OrganizationalUnit.objects.distinct("organizationCode")

# Count the number of distinct organizationCodes
count = len(distinct_organization_codes)

print(f"There are {count} distinct documents with respect to organizationCode.")
