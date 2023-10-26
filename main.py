"""This module contains the business logic of the function.

use the automation_context module to wrap your function in an Automate context helper
"""
from typing import Callable, cast

from pydantic import Field
from speckle_automate import (
    AutomateBase,
    AutomationContext,
    execute_automate_function,
)
from specklepy.objects import Base
from specklepy.objects.graph_traversal.traversal import TraversalRule, GraphTraversal


class FunctionInputs(AutomateBase):
    """These are function author defined values.

    Automate will make sure to supply them matching the types specified here.
    Please use the pydantic model schema to define your inputs:
    https://docs.pydantic.dev/latest/usage/models/
    """

    forbidden_parameter_prefix: str = Field(
        title="Parameter Prefix to Cleanse",
        description=(
            "If a object has a parameter with the following prefix it will be removed from the object."
        ),
    )


def automate_function(
        automate_context: AutomationContext,
        function_inputs: FunctionInputs,
) -> None:
    """This is an example Speckle Automate function.

    Args:
        automate_context: A context helper object, that carries relevant information
            about the runtime context of this function.
            It gives access to the Speckle project data, that triggered this run.
            It also has convenience methods attach result data to the Speckle model.
        function_inputs: An instance object matching the defined schema.
    """
    # the context provides a convenient way, to receive the triggering version
    if (
            not function_inputs.forbidden_parameter_prefix
            or function_inputs.forbidden_parameter_prefix == ""
    ):
        automate_context.mark_run_failed("No prefix has been set.")
        return

    version_root_object = automate_context.receive_version()

    func = get_default_traversal_func()

    traversal_collection_contexts = func.traverse(version_root_object)

    for context in traversal_collection_contexts:
        current = context.current
        if hasattr(current, "parameters"):
            parameters = cast(Base, current.parameters)
            parameter_names = parameters.get_dynamic_member_names()

            for parameter_name in parameter_names:
                if parameter_name.startswith(
                        function_inputs.forbidden_parameter_prefix
                ):
                    # Base objects doesn't support the delitem method
                    parameters.__dict__.pop(parameter_name)

    automate_context.create_new_version_in_project(
        version_root_object,
        "cleansed",
        "This version has been cleansed of parameters with the prefix '"
    )


# traverse the root object and if a revit parameter has the prefix, remove it
# this is a recursive function


def get_default_traversal_func() -> GraphTraversal:
    """
    Traversal func for traversing a speckle commit object
    """

    DISPLAY_VALUE_PROPERTY_ALIASES = {"displayValue", "@displayValue"}
    ELEMENTS_PROPERTY_ALIASES = {"elements", "@elements"}

    display_value_rule = TraversalRule(
        [
            lambda o: any(
                getattr(o, alias, None) for alias in DISPLAY_VALUE_PROPERTY_ALIASES
            ),
            lambda o: "Geometry" in o.speckle_type,
        ],
        lambda o: ELEMENTS_PROPERTY_ALIASES,
    )

    default_rule = TraversalRule(
        [lambda _: True],
        lambda o: o.get_member_names(),  # TODO: avoid deprecated members
    )

    return GraphTraversal([display_value_rule, default_rule])


# make sure to call the function with the executor
if __name__ == "__main__":
    # NOTE: always pass in the automate function by its reference, do not invoke it!

    # pass in the function reference with the inputs schema to the executor
    execute_automate_function(automate_function, FunctionInputs)

    # if the function has no arguments, the executor can handle it like so
    # execute_automate_function(automate_function_without_inputs)
