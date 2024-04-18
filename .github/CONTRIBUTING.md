# Contributing to harambot

PRs are welcome provided they follow the guidelines and procedures below.

## Procedure
1. Open an issue/feature request to discuss the changes you want to make
2. Fork the repository
3. Create a new branch
4. Make your changes
5. Create tests for your changes
6. Run tests
7. Commit your changes
8. Push your changes
9. Create a pull request

## Guidelines
- Follow the GitHub Community Guidelines
- Be responsive and open to discussions and suggestions from the project maintainers and contributors
- Toxic behavior or bullying will not be tolerated

## Setting up development environment

### Prerequisites
- Python 3.8 or higher
- pyenv
- pyenv-virtualenv
- poetry

### Environment setup
Use the following commands to setup your local environment
```
git clone [your fork url]
cd harambot
pyenv virtual-env 3.8 harambot
pyenv local harambot
poerty install --with dev
precommit install
precommit autoupdate
precommit run --all-files

```

### Running tests
You can run the tests by running the following from the projects root directory
```
pytest
```
