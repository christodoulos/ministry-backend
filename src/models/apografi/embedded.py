import mongoengine as me

# Embeddable documents for the Organization model


class Spatial(me.EmbeddedDocument):
    countryId = me.IntField()
    cityId = me.IntField()


class ContactPoint(me.EmbeddedDocument):
    email = me.EmailField()
    telephone = me.StringField()


class FoundationFek(me.EmbeddedDocument):
    year = me.IntField()
    number = me.StringField()
    issue = me.StringField()


class Address(me.EmbeddedDocument):
    fullAddress = me.StringField()
    postCode = me.StringField()
    adminUnitLevel1 = me.IntField()
    adminUnitLevel2 = me.IntField()
