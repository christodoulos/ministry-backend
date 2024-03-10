from src.models.psped import Foreas


def build_tree(unit, monades):
    subordinates = [u for u in monades if u.supervisorUnitCode == unit.code]

    for sub in subordinates:
        sub.subordinates = build_tree(sub, monades)

    return subordinates


def foreas_tree(code: str):
    foreas = Foreas.objects(code=str(code)).first()
    monades = foreas.apografi.monades

    trees = []

    roots = [u for u in monades if not u.supervisorUnitCode]

    for root in roots:
        root.subordinates = build_tree(root, monades)
        trees.append(root)

    return trees


def convert_tree_to_flat_nodes(node, level=0):
    flat_nodes = []
    flat_node = {
        "expandable": bool(node.subordinates),
        "name": node.id,
        "level": level,
        "isExpanded": False,
    }
    flat_nodes.append(flat_node)

    for subordinate in node.subordinates:
        flat_nodes.extend(convert_tree_to_flat_nodes(subordinate, level + 1))

    return flat_nodes


def angular_cdk_tree(code: str):
    tree = foreas_tree(code)

    flat_nodes = []
    for root in tree:
        flat_nodes.extend(convert_tree_to_flat_nodes(root))

    return flat_nodes
