[![build and deploy Speckle functions](https://github.com/urbansurgery/Automate-DeepClean/actions/workflows/main.yml/badge.svg)](https://github.com/urbansurgery/Automate-DeepClean/actions/workflows/main.yml)

# Speckle Automate Function: Data Validation in AEC

This repository provides a Speckle Automate function crafted specifically for the AEC industry, demonstrating the power
of data validation using the `specklepy` SDK.

Our function showcases both loose and tight coupling methodologies between check rules (conditions we validate) and
actions (responses based on conditions). This balance ensures adaptability and reliability in our validation framework.

## Getting Started

1. **Use this Template**: Click on "Use this template" to create a new repository with this structure.

2. **Register the Function**: [Describe how to register the function with Speckle.]

3. **Add Dependencies**: Use `$ poetry add [package_name]` to add new Python package dependencies.

4. **Edit Launch Variables**: [Briefly describe how the `launch.json` should be edited for custom configurations.]

5. **Local Development**: For a local dev setup, [provide steps].

6. **GitHub Codespaces**: Quickly set up a dev environment using GitHub Codespaces.

## How the Validation Works

In the AEC domain, data validation isn't merely about ensuring data integrity. It's about comprehending the intricate
relationships between data points, especially when diving into BIM (Building Information Modelling). This function
demonstrates the traversal through and manipulation of this complex web of relationships while preserving the integrity
of the overall data structure.

### Check Rules and Actions: The Core Framework

Our system's core is the dynamic relationship between check rules (conditions we validate against) and actions (
operations we conduct based on these conditions). This relationship can be:

- **Loosely Coupled**: In this method, checks and actions remain modular and distinct. This flexibility allows checks to
  be paired with diverse actions depending on specific needs.

- **Tightly Coupled**: Here, specific checks are intrinsically linked to distinct actions. This ensures a predictable
  validation trajectory.

Our function manifests both methods. While the `ParameterRules` class provides modular checks, the subclasses
of `ParameterAction`, such as `PrefixRemovalAction`, embrace the tight coupling principle, offering specific responses
to set conditions.

### Traversal Rule Pattern: Navigating Complex Data Structures

The traversal methodology found in both the speckle-sharp and specklepy SDKs, which we refer to as the `TraversalRule`
pattern, is integral to our validation process. Its utility is manifold:

1. **Preserve Hierarchical Relationships**: BIM data is all about hierarchy - a door hosted by a wall, situated in a
   room, and so on. Using the traversal methodology, while elements can be changed, their relationships with other
   elements stay intact.

2. **In-place Data Mutation**: Rather than spawning entirely new data structures, the traversal method champions
   in-place data mutation. This approach is not only efficient but also minimizes data loss risks.

3. **Maintain Original Constructs**: This becomes pivotal when examining elements like family instances in Revit. A
   single alteration can ripple through the data. The traversal methodology ensures that while data undergoes validation
   or changes, original structural relationships are upheld.

### Zooming Out: The Broader Perspective

In the AEC landscape, data validation transcends data integrity; it's about safeguarding relationships and data
hierarchies. With a robust blend of check rules, actions, and the traversal methodology, our function stands as a
testament to handling intricate AEC data with finesse, balancing both data accuracy and structural authenticity.

## Using this Speckle Function

1. **Create a New Speckle Automation**: Navigate to the Speckle dashboard.

2. **Select the Speckle Project & Model**: Choose the relevant project and model.

3. **Select the Function**: Opt for the function named "Data Validation in AEC."

4. **Configure & Create**: Adjust settings as needed and click "Create Automation."

## Develop Your Own Speckle Function

1. **Fork & Clone**: Fork this repository and clone it or use GitHub CodeSpaces.

2. **Function Registration**: After registration, save the Function Publish Token and ID as GitHub Action Secrets.

3. **Edit**: Make modifications in `main.py`.

4. **Automatic Versioning**: Every commit to the main branch auto-creates a new version.

## Developer Setup

- **Requirements**: Install Python 3 and Poetry. Run `poetry shell && poetry install` for required packages.

- **Building & Testing**: Test locally using `poetry run pytest`. Also, package the code as a Docker Container Image for
  Speckle Automate.

## Resources

- **SpecklePy**: Dive deeper into `SpecklePy` and harness the power of Speckle from Python.
