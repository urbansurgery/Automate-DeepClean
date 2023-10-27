from specklepy.objects.graph_traversal.traversal import GraphTraversal, TraversalRule


def get_data_traversal_rules() -> GraphTraversal:
    """
    Generates traversal rules for navigating Speckle data structures.

    This function defines and returns traversal rules tailored for Speckle data.
    These rules are used to navigate and extract specific data properties
    within complex Speckle data hierarchies.

    It defines two main rules:

    1. `display_value_rule`:
        - Targets objects that have properties named either "displayValue" or
          "@displayValue".
        - Specifically focuses on objects with a 'speckle_type' containing
          "Geometry".
        - For such objects, the function looks to traverse their 'elements'
          or '@elements' properties.

    2. `default_rule`:
        - A more general rule that applies to all objects.
        - It aims to traverse all member names of an object while avoiding
          deprecated members (a potential enhancement for the future).

    Returns:
        GraphTraversal: A GraphTraversal instance initialized with the
        defined rules.
    """
    display_value_property_aliases = {"displayValue", "@displayValue"}
    elements_property_aliases = {"elements", "@elements"}

    display_value_rule = TraversalRule(
        [
            lambda o: any(
                getattr(o, alias, None) for alias in display_value_property_aliases
            ),
            lambda o: "Geometry" in o.speckle_type,
        ],
        lambda o: elements_property_aliases,
    )

    default_rule = TraversalRule(
        [lambda _: True],
        lambda o: o.get_member_names(),
    )

    return GraphTraversal([display_value_rule, default_rule])
