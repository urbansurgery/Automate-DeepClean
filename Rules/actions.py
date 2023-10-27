from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Dict, List, Optional, Union, Any
from speckle_automate import AutomationContext
from specklepy.objects import Base

from Rules.rules import ParameterRules


# Our main goal is to define actions that can be taken on parameters.
# We'll start by creating a base class that all specific actions will inherit from.


class ParameterAction(ABC):
    """
    Base class for actions on parameters.

    This class provides a general structure for actions that can be applied to
    parameters. Each action derived from this class will have to implement its
    specific logic in the `apply` method and then provide feedback through the
    `report` method.
    """

    def __init__(self) -> None:
        # A dictionary to keep track of parameters affected by the action.
        # The key is the parent object's ID, and the value is a list of
        # parameter names that were affected.
        self.affected_parameters: Dict[str, List[str]] = defaultdict(list)

    @abstractmethod
    def apply(self, parameter: Dict[str, str], parent_object: Dict[str, str]) -> None:
        """Method to apply the specific action logic on the parameter."""
        pass

    @abstractmethod
    def report(self, automate_context: AutomationContext) -> None:
        """Method to provide feedback based on the action's results."""
        pass


# Now, let's create a specific action. In this example, we're removing parameters
# that start with a specific prefix.


class PrefixRemovalAction(ParameterAction):
    """
    Action to remove parameters with a specific prefix.
    """

    def __init__(self, forbidden_prefix: str) -> None:
        super().__init__()
        # The prefix we want to remove
        self.forbidden_prefix: str = forbidden_prefix

    def apply(
        self, parameter: Union[Base, Dict[str, Any]], parent_object: Base
    ) -> None:
        """
        Remove the parameter if its name starts with the forbidden prefix.
        This function demonstrates the complexities of navigating and modifying
        the structure of Revit parameters in Speckle's data model.

        In Revit, custom parameters are stored with a GUID as the key, which means
        we cannot predict the exact key ahead of time. Instead, we have to traverse
        through the parameters and match them by another attribute, in this case,
        the `applicationInternalName`.
        """

        # Extract the parameter name. If the parameter doesn't have a name or if the
        # name doesn't start with the forbidden prefix, exit the function early.
        param_name = parameter["name"]
        if not param_name or not param_name.startswith(self.forbidden_prefix):
            return

        # The parameters in parent_object are stored in a dictionary-like structure
        # where the key is a GUID (applicationInternalName). We need to safely
        # access this key without causing a KeyError.

        # If the parameter's parent object is a Base type, we can use the `__dict__` method
        # to access its underlying dictionary representation.
        if isinstance(parent_object["parameters"], Base):
            try:
                # Retrieve the unique GUID which corresponds to the parameter's key in the parent object.
                application_name = parameter.__getitem__("applicationInternalName")

                # Check if the GUID exists as a key in the parent object's parameters.
                # If it does, remove that parameter from the dictionary.
                if application_name in parent_object["parameters"].__dict__:
                    parent_object["parameters"].__dict__.pop(application_name)
                    self.affected_parameters[parent_object["id"]].append(param_name)

            except KeyError:
                pass
                # This block will execute if the `applicationInternalName` key is not found in parameter.
                # In this example, we're simply passing over this exception, but more specific error
                # handling can be implemented if needed.
                # Record this removal in our affected_parameters dictionary

    def report(self, automate_context: AutomationContext) -> None:
        """
        Generate a summary of removed parameters.

        After all parameters have been checked, this method will be called to
        provide feedback on the results of the action.
        """
        if not self.affected_parameters:
            return

        # Summarize the names of all removed parameters
        removed_params = set(
            param for params in self.affected_parameters.values() for param in params
        )

        message = f"The following parameters were removed: {', '.join(removed_params)}"

        # Attach this summary to the relevant objects in the AutomationContext
        automate_context.attach_info_to_objects(
            category="Removed_Parameters",
            object_ids=list(self.affected_parameters.keys()),
            message=message,
        )


# This example Automate function is for prefixed parameter removal. Additional example actions below follow the same
# pattern, but with different logic. In some instances there is a strong coupling between the action and the checking
# logic, and in others there is a looser coupling. Which is why I have defined the actions separately from the
# checking logic.


class MissingValueReportAction(ParameterAction):
    """
    This action class is designed to handle parameters that lack values.
    It checks each parameter for a value, and if one isn't found, it records the
    parameter's name. Later, a report can be generated that summarizes which parameters
    are missing values.
    """

    def apply(self, parameter: Dict[str, str], parent_object: Dict[str, str]) -> None:
        # Check if the parameter has a missing value using our predefined rule
        if ParameterRules.has_missing_value(parameter):
            # If missing, add the parameter's name to our affected_parameters dictionary
            # The key is the parent object's ID for easy lookup later
            self.affected_parameters[parent_object["id"]].append(parameter["name"])

    def report(self, automate_context: AutomationContext) -> None:
        # Construct a set of unique parameter names that have missing values
        missing_value_params = set(
            param for params in self.affected_parameters.values() for param in params
        )

        # Formulate a message summarizing the missing parameters
        message = f"The following parameters have missing values: {', '.join(missing_value_params)}"

        # Use the automation context to attach this message to the relevant objects
        automate_context.attach_info_to_objects(
            category="Missing_Values",
            object_ids=list(self.affected_parameters.keys()),
            message=message,
        )


class DefaultValueMutationAction(ParameterAction):
    """
    This action class is focused on parameters that have default values.
    The goal is to detect these default values and replace them with a new specified value.
    The parameters that were mutated will be recorded, allowing for a report to be generated
    that summarizes the changes.
    """

    def __init__(self, new_value: Optional[str] = None) -> None:
        super().__init__()
        # The new value to replace defaults with; if none is given, use "Updated Value"
        self.new_value: str = new_value or "Updated Value"

    def apply(self, parameter: Dict[str, str], parent_object: Dict[str, str]) -> None:
        # Check if the parameter has a default value
        if ParameterRules.has_default_value(parameter):
            # If it does, update its value with the new specified value
            parameter["value"] = self.new_value  # Mutate the parameter value

            # Record the parameter's name in our affected_parameters dictionary
            self.affected_parameters[parent_object["id"]].append(parameter["name"])

    def report(self, automate_context: AutomationContext) -> None:
        # Construct a set of unique parameter names that were mutated
        mutated_params = set(
            param for params in self.affected_parameters.values() for param in params
        )

        # Formulate a message summarizing the mutated parameters
        message = f"The following parameters were updated from default values: {', '.join(mutated_params)}"

        # Use the automation context to attach this message to the relevant objects
        automate_context.attach_info_to_objects(
            category="Updated_Defaults",
            object_ids=list(self.affected_parameters.keys()),
            message=message,
        )
