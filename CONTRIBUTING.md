# Contributing to Ludo 🎮

Thank you for considering a contribution to **Ludo**! This document outlines how to contribute code, report issues, and understand the project's licensing and copyright policies.

## How to Contribute 🛠️

1. **Reporting Issues:**

    If you find a bug, have a feature request, or need help, please open an issue in the GitHub Issues section. When reporting bugs, please include:

    - A clear, descriptive title.
    - A detailed description of the issue.
    - Steps to reproduce the problem.
    - Expected vs. actual behavior.
    - Environment details (OS, app version, etc.).
    - Logs or screenshots (if applicable).

2. **Submitting Code:**

    To contribute code, follow these steps:

    1. **Fork the repository** and clone your fork.
    2. **Create a new branch** for your feature or bug fix.
    3. **Write clean, documented code** following the project’s style.
    4. **Run static checks** using `ruff` and `mypy` before submitting a pull request (your changes should not introduce new warnings or errors from these tools).
    5. **Test your changes** before submitting.
    6. **Commit and push** your changes.
    7. **Open a pull request** with a clear description of your changes.

## Code Style & Guidelines 📝

### General Rule: Follow PEP8

Most of the code in Ludo should adhere to **PEP8** standards:

- Use `snake_case` for functions, variables, and method names.
- Use `PascalCase` for class names.

For more details, refer to the official [PEP8 style guide](https://pep8.org/).

**Example (PEP8-compliant class):**

```python
class GameInfoWidget(QFrame):
    """Widget that displays game information."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Initializes the UI elements."""
        pass
```

### Qt-Specific Code: When to Use Qt Naming Conventions

For subclasses of Qt widgets that are **intended to behave exactly like built-in Qt widgets** (with minimal modifications), follow Qt’s naming style:

- Use `camelCase` for functions, variables, and method names.
- Use `PascalCase` for class names.
- Match Qt’s built-in method names when overriding behavior.
- Keep properties/methods in line with Qt’s conventions to allow seamless integration.

**Example (Qt-style for a custom checkbox behaving like a native checkbox):**

```python
class SpriteSheetCheckBox(QCheckBox):
    """A QCheckBox with spritesheet support."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.loadSpriteSheet()

    def loadSpriteSheet(self):
        """Loads the checkbox images from a spritesheet."""
        pass
```

### When to Stick to PEP8 for Qt Widgets

If a class **subclasses a Qt widget but primarily contains custom logic**, it should follow PEP8 conventions.

- Do not use `camelCase` for general-purpose methods.
- Reserve Qt-style names only when overriding Qt behavior.
- Treat the class as a Python module with a Qt base class.

## Licensing & Copyright 📝

### License Requirements

*As a contributor, you have the right to choose a license for the files you contribute, with the following guidelines:*

- Core functionality must be licensed under the **Mozilla Public License (MPL) 2.0.**
- Standalone utilities, helper functions, and reusable components may be licensed under the **MIT License.**
- Final approval of licensing decisions rests with the project maintainers to ensure consistency and cohesion across the project.

### Copyright Policy

- **You retain copyright** over any contributions you make to the project.
- If your contribution is significant, please **add your name** to the copyright header of the files you modify or create.
- **Do not remove** existing names from copyright headers, even if the code changes over time.

### Copyright Headers

**MPL 2.0 Copyright Header example:**

```python
#############################################################################
##
## Copyright (C) 2025 Killian-W, John Doe.
## All rights reserved.
##
## This file is part of the Ludo project.
##
## Licensed under the Mozilla Public License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at:
##     https://www.mozilla.org/en-US/MPL/2.0/
##
## This software is provided "as is," without warranties or conditions
## of any kind, either express or implied. See the License for details.
##
#############################################################################
```

**MIT Copyright Header example:**

```python
#############################################################################
##
## Copyright (C) 2025 Killian-W, Jane Doe.
## All rights reserved.
##
## This file is part of the Ludo project.
##
## Licensed under the MIT License.
## You may obtain a copy of the License at:
##     https://opensource.org/licenses/MIT
##
## This software is provided "as is," without warranty of any kind.
##
#############################################################################
```

## Code of Conduct 🤝

We are committed to providing a welcoming and harassment-free experience for everyone. We expect all participants to:

- Be respectful and inclusive.
- Exercise empathy and kindness.
- Be open to constructive feedback.
- Focus on what is best for the community.
- Show courtesy and respect in all interactions.

Unacceptable behavior will not be tolerated and may result in temporary or permanent exclusion from project participation.

## Thank You 🙏

Your contributions make Ludo better! We appreciate your time and effort in helping improve the project. Happy coding! 🚀
