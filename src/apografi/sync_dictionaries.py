from src.models.apografi.dictionary import Dictionary
from src.models.utils import Log
from src.apografi.constants import APOGRAFI_DICTIONARIES, APOGRAFI_DICTIONARIES_URL
from src.apografi.utils import apografi_get
from deepdiff import DeepDiff
from alive_progress import alive_bar
import redis

r = redis.Redis()


def sync_apografi_dictionaries():
    print("Συγχρονισμός λεξικών από την Απογραφή...")

    with alive_bar(len(APOGRAFI_DICTIONARIES)) as bar:
        for dictionary in APOGRAFI_DICTIONARIES.keys():
            response = apografi_get(f"{APOGRAFI_DICTIONARIES_URL}{dictionary}")
            for item in response.json()["data"]:
                doc = {
                    "code": dictionary,
                    "code_el": APOGRAFI_DICTIONARIES[dictionary],
                    "apografi_id": item["id"],
                    "description": item["description"],
                }
                if "parentId" in item:
                    doc["parentId"] = item["parentId"]
                doc_id = f"{dictionary}:{item['id']}:{item['description']}"

                existing = Dictionary.objects(
                    code=dictionary,
                    apografi_id=item["id"],
                    description=item["description"],
                ).first()

                if existing:
                    existing_dict = existing.to_mongo().to_dict()
                    existing_dict.pop("_id")
                    diff = DeepDiff(
                        existing_dict,
                        doc,
                    )
                    if diff:
                        for key, value in doc.items():
                            setattr(existing, key, value)
                        existing.save()
                        Log(
                            entity="dictionary",
                            action="update",
                            doc_id=doc_id,
                            value=diff,
                        ).save()
                else:
                    Dictionary(**doc).save()
                    Log(
                        entity="dictionary", action="insert", doc_id=doc_id, value=doc
                    ).save()
            bar()

    print("Τέλος συγχρονισμού λεξικών από την Απογραφή.")


def cache_dictionaries():
    r = redis.Redis()
    print("Καταχώρηση λεξικών στην cache...")
    for dictionary in APOGRAFI_DICTIONARIES.keys():
        r.delete(dictionary)
        docs = Dictionary.objects(code=dictionary)
        ids = set([doc["apografi_id"] for doc in docs])
        r.sadd(dictionary, *ids)
    print("Τέλος καταχώρησης λεξικών στην cache.")
