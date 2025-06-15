# Case Claim API
This project is a web API for the management of ITS case claims as well as generating statistics for quality assurance processes.

## Contributing
Before contributing to this project, please contact the project manager [@AndrewAlbizati](https://github.com/AndrewAlbizati) to see how you can help. Once you've been approved to add a feature, please create a new branch from the project to begin your work. While you are programming, please ensure that you are adhering to the [PEP 8](https://peps.python.org/pep-0008/) style guide. Once you are done, please pull the latest changes from the `main` branch to your branch, then create a pull request detailing your changes. This will then be subject to approval from the project managers. Once approved, your branch will be merged with `main`.

### Deployment
1. Begin by installing
[Git](https://git-scm.com/downloads) for version control and [Docker Desktop](https://www.docker.com/) for deployment (Docker CLI and Docker Compose will also work).

2. Run the following command to download the repository:

`git clone https://github.com/ITS-Help-Desk/CaseClaimAPI.git`


3. Create a `.env` file in the main directory to contain all necessary environment variables. An example is:
```
ALLOWED_HOSTS='[]'
SECRET_KEY='secret goes here'
DEBUG='true'
```

4. Run the following command to build and run the project:

`docker-compose up --build`

Once you've run this command, if everything is set up correctly, your output should look like:
```
Creating caseclaimapi_web_1 ... done
Attaching to caseclaimapi_web_1
web_1  | Loading .env environment variables...
web_1  | 2025-06-15 22:44:50,997 INFO     Starting server at tcp:port=8000:interface=0.0.0.0
web_1  | 2025-06-15 22:44:50,998 INFO     HTTP/2 support not enabled (install the http2 and tls Twisted extras)
web_1  | 2025-06-15 22:44:50,998 INFO     Configuring endpoint tcp:port=8000:interface=0.0.0.0
web_1  | 2025-06-15 22:44:51,000 INFO     Listening on TCP address 0.0.0.0:8000
```

5. Connect to `localhost:8000/caseflow-admin` to view the admin dashboard.