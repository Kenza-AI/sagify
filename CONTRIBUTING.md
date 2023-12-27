## General Guidelines
- Every new functionality should be accompanied with solid unit tests. We haven't set any threshold regarding code coverage % as we want to be pragmatic.
- Every bug that is fixed should come with related unit tests.
- Regarding coding style, we follow PEP8 with the exception of letting up to 100 characters per line. We think that 80 characters is quite limiting and may lead to very short variable names, and thus unreadable code.

## Branching Model
- Standard Fork & Pull Request Workflow is used in this project
- Every new functionality should be created in a branch (from master branch) with name format `feature/new-functionality-name`
- Every bug should be fixed in a branch (from master branch) with name format `fix/bug-name`
- All branches will be merged to master branch

## Setup Environment
- Create a virtualenv. For example, `mkvirtualenv sagify`.
- Run `pip install -r requirements.txt` to install dependencies 
- Ready to rock!

## Testing Locally
- `make test`: Runs tests with pytest
- `make test-all`: Runs tests on py27, py35 and py36 with tox and pytest

## Linting Locally
- `make lint`

## Other commands:
- `clean-pyc`: remove Python file artifacts