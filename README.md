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

`daphne -p 8000 api.asgi:application`

Once you've run this command, if everything is setup correctly, your output should look like:
```
2025-05-29 18:35:45,318 INFO     Starting server at tcp:port=8000:interface=127.0.0.1
2025-05-29 18:35:45,319 INFO     HTTP/2 support not enabled (install the http2 and tls Twisted extras)
2025-05-29 18:35:45,319 INFO     Configuring endpoint tcp:port=8000:interface=127.0.0.1
2025-05-29 18:35:45,319 INFO     Listening on TCP address 127.0.0.1:8000
```

## Dependencies
- Django [5.1.7](https://pypi.org/project/Django/)
- python-dotenv [1.1.0](https://pypi.org/project/python-dotenv/)