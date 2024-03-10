import json
import mongoengine as me
from src.models.apografi.organization import Organization
from src.models.apografi.organizational_unit import OrganizationalUnit
from src.models.utils import JSONEncoder


class TreeNode(me.EmbeddedDocument):
    expandable = me.BooleanField()
    monada = me.ReferenceField(OrganizationalUnit)
    level = me.IntField()


def print_tree(node, indent=0):
    print("\t" * indent, node.id, node.preferredLabel)
    for subordinate in node.subordinates:
        print_tree(subordinate, indent + 1)


def build_subtree(super_monada, monades):
    subordinates = [u for u in monades if u.supervisorUnitCode == super_monada.code]

    for sub in subordinates:
        sub.subordinates = build_subtree(sub, monades)

    return subordinates


def build_tree(monades):
    roots = [u for u in monades if not u.supervisorUnitCode]

    for root in roots:
        root.subordinates = build_subtree(root, monades)
        # print_tree(root)

    return roots


def convert_tree_to_flat_nodes(node, level=0):
    flat_nodes = []
    flat_node = TreeNode(expandable=bool(node.subordinates), monada=node, level=level)
    flat_nodes.append(flat_node)
    for subordinate in node.subordinates:
        flat_nodes.extend(convert_tree_to_flat_nodes(subordinate, level + 1))
    return flat_nodes


class Apografi(me.EmbeddedDocument):
    foreas = me.ReferenceField(Organization)
    monades = me.ListField(me.ReferenceField(OrganizationalUnit))


class Foreas(me.Document):
    meta = {"collection": "foreis", "db_alias": "psped"}

    code = me.StringField(required=True, unique=True)
    level = me.StringField(
        choices=["ΚΕΝΤΡΙΚΟ", "ΑΠΟΚΕΝΤΡΩΜΕΝΟ", "ΠΕΡΙΦΕΡΕΙΑΚΟ", "ΤΟΠΙΚΟ", "ΜΗ ΟΡΙΣΜΕΝΟ"],
        default="MH ΟΡΙΣΜΕΝΟ",
    )
    apografi = me.EmbeddedDocumentField(Apografi, required=True)
    tree = me.EmbeddedDocumentListField(TreeNode)

    def to_json(self):
        organization = Organization.objects.get(code=self.code).to_json_enchanced()
        data = {k: v for k, v in organization.items()}
        data["level"] = self.level
        return json.dumps(data, cls=JSONEncoder)

    def to_json_enchanced(self):
        organization_id = self.apografi.foreas.id
        organizational_units_ids = [monada.id for monada in self.apografi.monades]
        organization = Organization.objects.with_id(organization_id).to_json_enchanced()
        organizational_units = [OrganizationalUnit.objects.with_id(ou_id) for ou_id in organizational_units_ids]

        data = {
            **json.loads(organization),
            "level": self.level,
            "monades": [{**json.loads(unit.to_json_enchanced())} for unit in organizational_units],
        }

        return json.dumps(data)

    def build_tree(self):
        monades = self.apografi.monades
        tree = build_tree(monades)

        flat_nodes = []
        for root in tree:
            flat_nodes.extend(convert_tree_to_flat_nodes(root))
        Foreas.objects(code=self.code).update_one(set__tree=flat_nodes)

    def tree_to_json(self):
        self.build_tree()
        tree = []
        for node in self.tree:
            tree.append(
                {
                    "expandable": node.expandable,
                    "monada": {
                        "preferredLabel": node.monada.preferredLabel,
                        "code": node.monada.code,
                    },
                    "level": node.level,
                }
            )
        return tree
