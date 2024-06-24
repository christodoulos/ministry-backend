from src.config import MONGO_PSPED_DB
from src.models.apografi.organization import Organization
from src.models.apografi.organizational_unit import OrganizationalUnit
import mongoengine as me


class UserRole(me.EmbeddedDocument):
    role = me.StringField(required=True, choices=["EDITOR", "READER", "ADMIN", "ROOT", "HELPDESK"], default="READER")
    active = me.BooleanField(required=True, default=True)
    foreas = me.ListField(me.StringField(), default=[])
    monades = me.ListField(me.StringField(), default=[])


class User(me.Document):
    email = me.EmailField(required=True, unique=True)
    firstName = me.StringField(required=True)
    lastName = me.StringField(required=True)
    name = me.StringField(required=True)
    googleId = me.StringField(required=True)
    photoUrl = me.StringField(required=True)
    provider = me.StringField(required=True, choices=["GOOGLE"], default="GOOGLE")
    roles = me.EmbeddedDocumentListField(UserRole, default=[UserRole(role="READER")])

    meta = {"collection": "users", "db_alias": MONGO_PSPED_DB}

    def to_mongo_dict(self):
        mongo_dict = self.to_mongo().to_dict()
        mongo_dict.pop("_id")
        return mongo_dict

    @staticmethod
    def get_user_by_google_id(googleId: str) -> "User":
        return User.objects(googleId=googleId).first()

    @staticmethod
    def get_user_by_email(email: str) -> "User":
        return User.objects(email=email).first()
