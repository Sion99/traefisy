# traefisy
![PyPI](https://img.shields.io/pypi/v/traefisy?label=pypi%20traefisy)
![PyPI - Downloads](https://img.shields.io/pypi/dm/traefisy)


**Traefisy** is a simple and powerful CLI tool that automates the configuration of [Traefik](https://doc.traefik.io/traefik/) reverse proxy settings. It allows you to easily manage routing rules, generate configuration files, and deploy Traefik in a Docker environment with minimal effort.

## Key Features

- **Easy Initialization**: Quickly set up Traefik reverse proxy with default or custom settings.
- **Dynamic Router Management**: Add, delete, and view routing rules dynamically.
- **Automatic Certificate Management**: Easily configure Let's Encrypt SSL certificates.
- **Docker Integration**: Automatically generate and run `docker-compose.yml` to deploy Traefik with the specified settings.
- **ACME Support**: Automatically manage SSL certificates through Let's Encrypt.

## Installation

You can install Traefisy directly from PyPI using `pip`:

```bash
pip install traefisy
```

## Usage
### Initialize Traefisy
To start using Traefisy, run the init command. This will guide you through the setup process, including setting up HTTP/HTTPS entry points, Let's Encrypt for SSL certificates, and adding initial routing rules.

```bash
traefisy init
```
During the initialization, you will be prompted to:
- Configure HTTP and HTTPS ports
- Set up Let's Encrypt for SSL certificates (optional)
- Add routing rules for your services

**Example:**
```
$ traefisy init
Welcome to traefisy!

Would you like to configure HTTP and HTTPS EntryPoints? [Y/n]: y
Please enter the HTTP port [80]: 
Please enter the HTTPS port [443]: 

Would you like to enable HTTPS using Let's Encrypt? [Y/n]: y
Please enter your ACME email: example@example.com
Please enter the directory to save certificates (Press enter to choose default option) [/etc/letsencrypt/live/default]: 

Would you like to add a router? [Y/n]: y
Router name: backend-router
Please enter the routing rule (e.g., example.yourdomain.com): api.example.com
Please enter the service name to link with the router: backend-service
Please enter the service URL: http://localhost:8080
```

### View Current Routers
To view all the currently configured routers, use the show command:

```bash
traefisy show
```
This will display the list of routers and their configurations in a table format.

```
                                              Router List
┏━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ ID       ┃ Name           ┃ Domain         ┃ Service Name  ┃ Service URL    ┃ Entry Points ┃   TLS   ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ 532251d2 │ traefik-dashb… │ traefik.a-eye… │ traefik-serv… │ http://localh… │ websecure    │ Enabled │
│ ff7f992e │ netdata        │ netdata.a-eye… │ netdata-serv… │ http://localh… │ websecure    │ Enabled │
└──────────┴────────────────┴────────────────┴───────────────┴────────────────┴──────────────┴─────────┘
```

### Add New Router
After the initialization, you can dynamically add more routers without reinitializing. Use the add command to add a new router to the configuration.
```bash
traefisy add
```

**Example:**
```
$ traefisy add
Router name: frontend-router
Please enter the routing rule (e.g., example.yourdomain.com): www.example.com
Please enter the service name to link with the router: frontend-service
Please enter the service URL: http://localhost:3000
```

### Remove a Router
If you need to delete an existing router, use the rm command with either the router's name or ID.
```bash
traefisy rm <router_name or id>
```

**Example:**
```
$ traefisy rm backend-router
Router has been deleted successfully.
```
You can also delete a router using its ID (first 8 characters are sufficient):
```
$ traefisy rm 12345678
Router has been deleted successfully.
```



### Run Traefisy
To deploy Traefik with the generated configuration, use the run command. This will automatically generate dynamic_conf.yml, traefik.yml, and docker-compose.yml, and start Traefik using Docker.
```bash
traefisy run
```
This command:
- Generates all necessary configuration files.
- Starts Traefik in a Docker container.
- Manages SSL certificates through Let's Encrypt.
