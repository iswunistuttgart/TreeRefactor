# Extending TreeRefactor with a new refactoring tool

A *refactoring tool* is something the LLM can call to execute a refactoring. TreeRefactor turns that call into new code, then evaluates, tests and commits it like any other candidate (see [HOW_IT_WORKS.md](HOW_IT_WORKS.md)). This guide adds an example tool, `remove_unused_import`, in four steps.

## The interfaces

| Interface | File | What you provide |
|---|---|---|
| `Refactoring` | [refactoring/refactoring.py](refactoring/refactoring.py) | The result of one refactoring. Pass `old_code` and `new_code` to `super().__init__` and override `tool_name()`. Diff, commit message and validity are inherited. |
| `RopeRefactoring` | [refactoring/rope_refactoring.py](refactoring/rope_refactoring.py) | Optional base class if you use [Rope](https://github.com/python-rope/rope). It handles the temporary project, you implement `execute_rope_refactoring`. See [extract_method_refactoring.py](refactoring/extract_method_refactoring.py). |
| `RefactoringTool` | [refactoring/refactoring_tool.py](refactoring/refactoring_tool.py) | Two static methods: `get_description()` returns the JSON schema of the tool call for the LLM, `call(code, arguments)` builds the `Refactoring` from the LLM's arguments. |
| `RefactoringCategory` | [tree_of_thoughts/refactoring_category.py](tree_of_thoughts/refactoring_category.py) | The categories offer tools to the LLM through their `tools` list. A tool is only offered for the categories you add it to. |
| `RefactoringGenerator` | [tree_of_thoughts/refactoring_generator.py](tree_of_thoughts/refactoring_generator.py) | `__handle_tool_call_response` maps the tool name of an LLM call to the matching `Tool.call`. |

Rules for `call`: the `arguments` come from the LLM and can be wrong. Validate them, raise inside the `Refactoring` constructor, and have `call` catch the error, report it with `CLI.print_error` and return `None`. The generator then skips that candidate. The generic `apply_edits` tool and `no_refactoring` are always offered in addition to the tools of the category.

## Example: `remove_unused_import`

### 1. Implement the refactoring and the tool

Create `refactoring/remove_unused_import_refactoring.py`:

```python
""" This file contains the implementation of the Remove Unused Import refactoring and a corresponding tool for an LLM to call. """
from refactoring.refactoring import Refactoring
from refactoring.refactoring_tool import RefactoringTool
from utility.cli import CLI


class RemoveUnusedImportRefactoring(Refactoring):
    def __init__(self, code: str, name: str):
        """Remove a name from the top-level imports of the code.

        Args:
            code (str): The code being refactored.
            name (str): The imported name (or alias) to remove.

        Raises:
            ValueError: If the name is not imported at the top level, or is still used in the code.
        """
        # Validate the arguments (raise ValueError if invalid) and compute the new code.
        new_code = ...
        super().__init__(code, new_code)

    def tool_name(self) -> str:
        return "Remove Unused Import"


class RemoveUnusedImportTool(RefactoringTool):
    @staticmethod
    def get_description() -> dict:
        """ Returns the description of the Remove Unused Import tool for the LLM. """
        return {
            "type": "function",
            "function": {
                "name": "remove_unused_import",
                "description": "Remove an import that is never used in the code. Pass the name as it is used in the code (the alias, if there is one).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The imported name to remove, e.g. 'os' for 'import os' or 'np' for 'import numpy as np'."
                        }
                    },
                    "required": ["name"],
                    "additionalProperties": False,
                },
            },
        }

    @staticmethod
    def call(code: str, arguments: dict) -> RemoveUnusedImportRefactoring | None:
        """ Calls the Remove Unused Import refactoring with the given arguments from the LLM. Returns None if it fails. """
        try:
            return RemoveUnusedImportRefactoring(code, arguments["name"])
        except Exception as e:
            CLI.print_error(f"Failed to create RemoveUnusedImportRefactoring. Error: {e}")
            return None
```

### 2. Offer the tool to the LLM

In [tree_of_thoughts/refactoring_category.py](tree_of_thoughts/refactoring_category.py) add the description to the `tools` of the fitting category, here `CODE_QUALITY`:

```python
from refactoring.remove_unused_import_refactoring import RemoveUnusedImportTool

CODE_QUALITY = RefactoringCategory(
    ...
    tools=[MultiRenameTool.get_description(), RemoveUnusedImportTool.get_description()],
    ...
)
```

### 3. Dispatch the tool call

In `__handle_tool_call_response` of [tree_of_thoughts/refactoring_generator.py](tree_of_thoughts/refactoring_generator.py) add the import and a branch next to the existing ones:

```python
from refactoring.remove_unused_import_refactoring import RemoveUnusedImportTool

...
            if tool_call.name == "remove_unused_import":
                return RemoveUnusedImportTool.call(code=code, arguments=arguments)
```

The name must equal the `name` in your `get_description()`. Without this branch the generator reports an unknown tool and drops the candidate.

### 4. (Optional) Mention it in the prompt

The prompt of a category lists example refactorings (`RefactoringSuggestion` in [tree_of_thoughts/refactoring_suggestion.py](tree_of_thoughts/refactoring_suggestion.py)). If the LLM should know when to use your tool, add a suggestion with a before/after example to the category, or extend the `description` of the tool.

## How the tests were written

Test are helpful to verify that a refactoring tool is working. Existing tests in `tests/unit/refactoring` take an example script, execute the refactoring tool on it and compare it to a version of the script with the refactoring applied.
