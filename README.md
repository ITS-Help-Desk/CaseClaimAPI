# Case Claim API
This project is a web API for the management of ITS case claims as well as generating statistics for quality assurance processes.

## Contributing
Before contributing to this project, please contact the project manager [@AndrewAlbizati](https://github.com/AndrewAlbizati) to see how you can help. Once you've been approved to add a feature, please create a new branch from the project to begin your work. While you are programming, please ensure that you are adhering to the [PEP 8](https://peps.python.org/pep-0008/) style guide. Once you are done, please pull the latest changes from the `main` branch to your branch, then create a pull request detailing your changes. This will then be subject to approval from the project managers. Once approved, your branch will be merged with `main`.

### Setting up Development Environment
1. Begin by installing
[Git](https://git-scm.com/downloads) for version control,
[Visual Studio Code](https://code.visualstudio.com/download) for code editing, and
[Python 3.11](https://www.python.org/downloads/).

2. Run the following command to download the repository:

`git clone https://github.com/ITS-Help-Desk/CaseClaimAPI.git`

3. Run the following command to install [pipenv](https://pipenv.pypa.io/en/latest/index.html):

`pip install pipenv --user`

4. Once inside the repository, run the following command to install dependencies:

`pipenv install`

5. Once all packages are installed, create a `.env` file in the main directory to contain all necessary environment variables. An example is:
```
ALLOWED_HOSTS='[]'
SECRET_KEY='secret goes here'
DEBUG='true'
```

6. Run the following command to run the project:

`python manage.py runserver`

Once you've run this command, if everything is setup correctly, your output should look like:
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
March 28, 2025 - 22:58:28
Django version 5.1.7, using settings 'api.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

## Dependencies
- Django [5.1.7](https://pypi.org/project/Django/)
- python-dotenv [1.1.0](https://pypi.org/project/python-dotenv/)