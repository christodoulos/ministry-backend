APOGRAFI_API_URL = "https://hr.apografi.gov.gr/api"

# https://hr.apografi.gov.gr/api.html#genikes-plhrofories-le3ika

APOGRAFI_DICTIONARIES_URL = f"{APOGRAFI_API_URL}/public/metadata/dictionary/"

APOGRAFI_DICTIONARIES = {
    "OrganizationTypes": "Τύποι Φορέων",
    "OrganizationCategories": "Κατηγορίες Φορέων",
    "EmploymentTypes": "Εργασιακές Σχέσεις",
    "EmployeeCategories": "Κατηγορίες Προσωπικού",
    "SupervisorPositions": "Τύποι Θέσεων Ευθύνης",
    "UnitTypes": "Τύποι Μονάδων",
    "Functions": "Λειτουργίες",
    "FunctionalAreas": "Τομείς Πολιτικής",
    "ProfessionCategories": "Κλάδοι",
    "Specialities": "Ειδικότητες",
    "EducationTypes": "Κατηγορίες Εκπαίδευσης",
    "Countries": "Χώρες",
    "Cities": "Δήμοι",
}

APOGRAFI_DICTIONARIES_SINGULAR = {
    "OrganizationTypes": "OrganizationType",
    "OrganizationCategories": "OrganizationCategory",
    "EmploymentTypes": "EmploymentType",
    "EmployeeCategories": "EmployeeCategory",
    "SupervisorPositions": "SupervisorPosition",
    "UnitTypes": "UnitType",
    "Functions": "Function",
    "FunctionalAreas": "FunctionalArea",
    "ProfessionCategories": "ProfessionCategory",
    "Specialities": "Speciality",
    "EducationTypes": "EducationType",
    "Countries": "Country",
    "Cities": "City",
}

# https://hr.apografi.gov.gr/api.html#genikes-plhrofories-foreis

APOGRAFI_ORGANIZATIONS_URL = f"{APOGRAFI_API_URL}/public/organizations"

# https://hr.apografi.gov.gr/api.html#genikes-plhrofories-monades-lista-monadwn

APOGRAFI_ORGANIZATIONAL_UNITS_URL = (
    f"{APOGRAFI_API_URL}/public/organizational-units?organizationCode="
)

# https://hr.apografi.gov.gr/api.html#genikes-plhrofories-monades-ierarxia-monadwn

APOGRAFI_ORGANIZATION_TREE_URL = (
    f"{APOGRAFI_API_URL}/public/organization-tree?organizationCode="
)
