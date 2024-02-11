from src.apografi.sync_dictionaries import (
    sync_apografi_dictionaries,
    cache_dictionaries,
)
from src.apografi.sync_organizations import sync_organizations
from src.apografi.sync_organizational_units import sync_organizational_units

sync_apografi_dictionaries()
cache_dictionaries()

sync_organizations()

sync_organizational_units()
