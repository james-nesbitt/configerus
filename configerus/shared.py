"""

Common shared functions.

The important methods here are the functions used for navigating trees of Dict
data using the dot notation syntax and the merging of those trees.

"""
import logging
from typing import Dict, Any, List

logger = logging.getLogger("configerus.shared")

# @see https://stackoverflow.com/
#       @questions/20656135/python-deep-merge-dictionary-data


def tree_merge(source: Any, destination: Any):
    """Deep merge source into destination.

    >>> a = { 'first' : { 'all_rows' : { 'pass' : 'dog', 'number' : '1' } } }
    >>> b = { 'first' : { 'all_rows' : { 'fail' : 'cat', 'number' : '5' } } }
    >>> merge(b, a) ==
         { 'first' : { 'all_rows' :
           { 'pass' : 'dog', 'fail' : 'cat', 'number' : '5' } } }
    True
    """
    if not (isinstance(source, dict) and isinstance(destination, dict)):
        return source

    for key, value in source.items():
        if isinstance(value, dict) and key in destination:
            value = tree_merge(value, destination[key])
        destination[key] = value

    return destination


def tree_get(
    node: Dict, keys: List[str], glue: str = ".", ignore: List[str] = None
) -> Any:
    """Find a path down a tree using the keys as a step by step path."""
    if not node:
        raise ValueError(
            "There was no data in the config so no key match could be made"
        )

    flat_steps = tree_reduce(tree=keys, glue=glue, ignore=ignore)
    if len(flat_steps) == 0:
        return node

    for step in flat_steps:
        try:
            if node is None:
                raise KeyError("Path tried to descend into None")
            if isinstance(node, str):
                raise KeyError(
                    "Path tried to descend into a string: {}".format(node)
                )
            if isinstance(node, list) and step.isnumeric():
                node = node[int(step)]
            else:
                # hopefully the target is subscriptable?
                node = node[step]

        except KeyError as err:
            raise KeyError(
                f"Key {keys} not found in loaded config data. '{step}' "
                "was not found"
            ) from err
        except IndexError as err:
            raise IndexError(
                f"Array index '{step}' was not found in list : {node}"
            ) from err
        except TypeError as err:
            raise ValueError(
                f"Invalid key '{step}' in the keys list: '{node}'"
            ) from err

    return node


def tree_reduce(
    tree: Any, glue: str = ".", ignore: List[Any] = None
) -> List[str]:
    """Merge a nested tree of strings down to a flat list of strings.

    Also split any strings that contain a glue character into a list of strings
    and flatten them down as well.

    Also ignore certain passed in strings from the list.

    Parameters:
    -----------
    tree (str | List[str] | List[List[str]] ...) : Any list tree of strings
        that need to be flattened to a single depth

    glue (str) : if a string is found that has a glue, then it is split along
        that glue and converted to a List

    ignore (List[str]) : a list of strings that should be considered invalid
        values that should not be included in the flattenned list

    Returns:
    --------
    List[str] tree reduced to a flat (single) depth, potentially empty
    """
    # don't use the iterator solution with strings
    if isinstance(tree, str):
        if glue == "":
            tree = [tree]
        else:
            tree = tree.split(glue)
    elif isinstance(tree, int):
        tree = [tree]

    else:
        flatter = []
        for node in tree:
            flat_node = tree_reduce(node, glue, ignore)
            flatter += flat_node
        tree = flatter

    if ignore is None:
        ignore = []
    return [node for node in tree if node and node not in ignore]
