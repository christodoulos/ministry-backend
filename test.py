# from src.psped.organization_tree import foreas_tree, angular_cdk_tree


# def print_tree(node, indent=0):
#     print("\t" * indent, node.id, node.preferredLabel)
#     for subordinate in node.subordinates:
#         print_tree(subordinate, indent + 1)


# code = "24672"
# tree = foreas_tree(code)


# for root in tree:
#     print_tree(root)


# print(angular_cdk_tree(code))
from src.models.psped import Foreas

foreas = Foreas.objects(code="24672").first()
foreas.build_tree()
