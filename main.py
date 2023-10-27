"""This module contains the business logic of the function.

use the automation_context module to wrap your function in an Automate context helper
"""
from typing import cast, List, Dict

from pydantic import Field
from speckle_automate import (
    AutomateBase,
    AutomationContext,
    execute_automate_function,
)
from specklepy.objects import Base

from Rules.actions import PrefixRemovalAction
from Rules.rules import ParameterRules
from Rules.traversal import get_data_traversal_rules


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
    """
    Main function for the Speckle Automation.

    This function receives the Speckle data, applies a series of checks
    and actions on it, and then reports the results.

    Args:
        automate_context: Context with helper methods for Speckle Automate.
        function_inputs: User-defined inputs for the automation.
    """
    if not function_inputs.forbidden_parameter_prefix:
        automate_context.mark_run_failed("No prefix has been set.")
        return

    version_root_object = automate_context.receive_version()

    # Traverse the received Speckle data.
    speckle_data = get_data_traversal_rules()
    traversal_contexts_collection = speckle_data.traverse(version_root_object)

    # Checking rules
    is_revit_parameter = ParameterRules.speckle_type_rule(
        "Objects.BuiltElements.Revit.Parameter"
    )
    has_forbidden_prefix = ParameterRules.forbidden_prefix_rule(
        function_inputs.forbidden_parameter_prefix
    )

    # Actions
    removal_action = PrefixRemovalAction(function_inputs.forbidden_parameter_prefix)

    cleansed_objects = set()

    # Iterate over each context in the traversal contexts collection.
    # Each context represents an object (or a nested part of an object) within
    # the data structure that was traversed.
    # The goal of this loop is to identify and act upon parameters of the objects
    # that meet certain criteria (e.g., being a Revit parameter with a forbidden prefix).
    for context in traversal_contexts_collection:
        current_object = context.current
        if hasattr(current_object, "parameters"):
            parameters = cast(Base, current_object.parameters)

            if parameters is None:
                continue

            for parameter_key in parameters.get_dynamic_member_names():
                parameter = cast(Base, parameters.__getitem__(f"{parameter_key}"))

                if is_revit_parameter(parameter) and has_forbidden_prefix(parameter):
                    removal_action.apply(parameter, current_object)
                    if current_object.id not in cleansed_objects:
                        cleansed_objects.add(current_object.id)

    # check the affected objects of all actions and count them
    affected_objects = set()
    for action in [removal_action]:
        affected_objects.update(action.affected_parameters)

    if not affected_objects or len(affected_objects) == 0:
        automate_context.mark_run_success("No parameters were removed.")
        return

    # Generate reports for all actions.
    for action in [removal_action]:
        action.report(automate_context)

    new_version_id = automate_context.create_new_version_in_project(
        version_root_object, "cleansed", "Cleansed Parameters"
    )

    if not new_version_id:
        automate_context.mark_run_failed("Failed to create a new version.")
        return

    # Final summary.
    automate_context.mark_run_success("Actions applied and reports generated.")


# make sure to call the function with the executor
if __name__ == "__main__":
    # NOTE: always pass in the automate function by its reference, do not invoke it!

    # pass in the function reference with the inputs schema to the executor
    execute_automate_function(automate_function, FunctionInputs)

    # if the function has no arguments, the executor can handle it like so
    # execute_automate_function(automate_function_without_inputs)
