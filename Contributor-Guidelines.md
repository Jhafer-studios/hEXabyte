Contributing to hEXabyte Dev

Thank you for your interest in contributing to the hEXabyte Voxel Sandbox project! Since this is a prototype, your feedback, bug reports, and code contributions are invaluable.

1. Code of Conduct

This project is licensed under the GNU General Public License v3 (GPLv3). By contributing, you agree that your code and contributions will also be licensed under GPLv3. Please be respectful and considerate of other contributors.

2. Setting Up Your Development Environment

To work on hEXabyte, you need Python and the necessary libraries.

Clone the Repository:

git clone [https://github.com/Jhafer-studios/hEXabyte.git](https://github.com/Jhafer-studios/hEXabyte.git)
cd hEXabyte


Create a Virtual Environment: (Recommended)

python -m venv game_env
# On Windows:
.\game_env\Scripts\activate
# On macOS/Linux:
source game_env/bin/activate


Install Dependencies:

pip install ursina


Run the Game:

python hexabyte_dev.py


3. Reporting Bugs and Issues

If you find a problem, please check the existing issues before creating a new one.

Be Descriptive: Include the exact steps to reproduce the bug.

Provide Environment Details: Note your Operating System, Python version, and Ursina version.

Include Tracebacks: If the program crashes, copy the entire error traceback from the console.

4. Contributing Code (Pull Requests)

We welcome feature additions and bug fixes! Please follow these steps to ensure a smooth contribution process:

Fork the Repository and clone your fork.

Create a New Branch for your work (e.g., feature/add-new-entity or fix/npc-crash).

Make your changes. Try to adhere to the existing code style (simple, well-commented Python).

Test your changes. Ensure the game runs without errors and your changes don't break existing functionality (especially object placement and NPC movement).

Commit your changes with a clear, concise commit message.

Push your branch and open a Pull Request (PR) against the main branch of the official repository.

We will review your PR and provide feedback as quickly as possible.
