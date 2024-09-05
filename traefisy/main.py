import typer
from rich.console import Console
from rich.table import Table
from traefisy.db.db import get_db, init_db, check_if_db_exists
from traefisy.utils import add_router, is_router_duplicate, get_routers, get_acme_info, save_acme_info, remove_router
from sqlalchemy.orm import Session
from ruamel.yaml import YAML
import subprocess

import os

app = typer.Typer()
console = Console()


@app.command()
def init():
    if not check_if_db_exists():
        return

    init_db()

    db: Session = next(get_db())

    # Welcome 메시지
    console.print("[bold cyan]Welcome to traefisy![/bold cyan]\n")

    # TLS/HTTPS 설정
    tls = False

    settings = get_acme_info(db)

    if not settings:
        if typer.confirm("Would you like to enable HTTPS using Let's Encrypt?", default=True):
            acme_email = typer.prompt("Please enter your ACME email")
            cert_dir = typer.prompt(
                "Please enter the directory to save certificates (Press enter to choose default option)",
                default="/etc/letsencrypt/live/default"
            )
            save_acme_info(db, acme_email, cert_dir)
            tls = True
        else:
            tls = False
    else:
        acme_email = settings.acme_email
        cert_dir = settings.cert_dir
        tls = True

    console.print(f"Using ACME email: [green]{acme_email}[/green]")
    console.print(f"ACME keys will be placed: [green]{cert_dir}[/green]")

    # 라우터 설정
    while True:
        if not typer.confirm("Would you like to add a router?", default=True):
            break

        router_name = typer.prompt("Router name")
        routing_rule = typer.prompt("Please enter the routing rule (e.g., example.yourdomain.com)")
        service_name = typer.prompt("Please enter the service name to link with the router")
        service_url = typer.prompt("Please enter the service URL")

        # 중복 체크
        if is_router_duplicate(db, router_name, routing_rule):
            console.print(f"[red]Error: Routing information already exists.[/red]")
            continue

        add_router(db=db, name=router_name, domain=routing_rule, service_name=service_name, service_url=service_url,
                   entrypoints="websecure", tls=tls)
        console.print(f"[green]{router_name} router has been successfully added![/green]\n")


@app.command()
def add():
    db: Session = next(get_db())

    router_name = typer.prompt("Router name")
    routing_rule = typer.prompt("Please enter the routing rule (e.g., example.yourdomain.com)")
    service_name = typer.prompt("Please enter the service name to link with the router")
    service_url = typer.prompt("Please enter the service URL")
    tls = typer.confirm("Do you want to enable TLS (HTTPS)?", default=True)

    if is_router_duplicate(db, router_name, routing_rule):
        console.print(f"[red]Error: Routing information already exists.[/red]")
        return

    add_router(db=db, name=router_name, domain=routing_rule, service_name=service_name, service_url=service_url,
               entrypoints="websecure", tls=tls)
    console.print(f"[green]{router_name} router has been successfully added![/green]\n")


@app.command()
def rm(identifier: str):
    db: Session = next(get_db())

    removed = remove_router(db, identifier)
    if removed:
        console.print(f"[green]Router has been deleted successfully.[/green]")
    else:
        console.print(f"[green]Router not found.[/green]")


@app.command()
def show():
    db: Session = next(get_db())
    routers = get_routers(db)

    table = Table(title="Router List")

    # 테이블 열 정의
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="magenta")
    table.add_column("Domain", style="green")
    table.add_column("Service Name", style="blue")
    table.add_column("Service URL", style="yellow")
    table.add_column("Entry Points", style="red")
    table.add_column("TLS", justify="center", style="bold cyan")

    # 라우터 목록을 테이블에 추가
    for router in routers:
        table.add_row(
            router.id[:8],
            router.name,
            router.domain,
            router.service_name,
            router.service_url,
            router.entrypoints,
            "Enabled" if router.tls else "Disabled"
        )

    # 테이블 출력
    console.print(table)


@app.command()
def export():
    db: Session = next(get_db())
    routers = get_routers(db)
    settings = get_acme_info(db)

    # dynamic_conf.yml 파일 생성
    dynamic_conf = {
        "http": {
            "routers": {},
            "services": {},
            "middlewares": {
                "https-redirect": {
                    "redirectScheme": {
                        "scheme": "https"
                    }
                }
            }
        }
    }

    for router in routers:
        dynamic_conf["http"]["routers"][router.name] = {
            "rule": f"Host(`{router.domain}`)",
            "service": router.service_name,
            "entryPoints": [router.entrypoints]
        }

        if router.tls:
            dynamic_conf["http"]["routers"][router.name]["tls"] = {"certResolver": "letsencrypt"}

        dynamic_conf["http"]["services"][router.service_name] = {
            "loadBalancer": {
                "servers": [
                    {"url": router.service_url}
                ]
            }
        }

    yaml = YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)

    with open('./dynamic_conf.yml', 'w') as file:
        yaml.dump(dynamic_conf, file)

    console.print("[green]dynamic_conf.yml has been generated.[/green]")

    # Static Configuration 파일 생성 (traefik.yml)
    cert_file = f"{settings.cert_dir}/fullchain.pem"
    key_file = f"{settings.cert_dir}/privkey.pem"

    static_config = {
        "api": {
            "dashboard": True,
            "insecure": True
        },
        "providers": {
            "docker": {
                "endpoint": "unix:///var/run/docker.sock",
                "exposedByDefault": False,
                "watch": True
            },
            "file": {
                "filename": "./dynamic_conf.yml",
                "watch": True
            }
        },
        "entryPoints": {
            "web": {
                "address": ":80",
                "http": {
                    "redirections": {
                        "entryPoint": {
                            "to": "websecure",
                            "scheme": "https",
                            "permanent": True
                        }
                    }
                }
            },
            "websecure": {
                "address": ":443"
            }
        },
        "tls": {
            "stores": {
                "default": {
                    "defaultCertificate": {
                        "certFile": cert_file,
                        "keyFile": key_file
                    }
                }
            }
        },
        "certificatesResolvers": {
            "letsencrypt": {
                "acme": {
                    "email": settings.acme_email,
                    "storage": "./acme.json",
                    "httpChallenge": {
                        "entryPoint": "web"
                    }
                }
            }
        }
    }

    with open('./traefik.yml', 'w') as file:
        yaml.dump(static_config, file)

    console.print("[green]traefik.yml has been generated.[/green]")


@app.command()
def run():
    db: Session = next(get_db())
    settings = get_acme_info(db)

    export()

    cert_file_path = f"{settings.cert_dir}/fullchain.pem"
    key_file_path = f"{settings.cert_dir}/privkey.pem"

    # acme.json 파일 생성 및 권한 설정
    acme_file_path = "./acme.json"

    # acme.json 파일이 없으면 생성
    if not os.path.exists(acme_file_path):
        console.print("[yellow]Creating acme.json file...[/yellow]")
        with open(acme_file_path, 'w') as acme_file:
            acme_file.write('{}')  # 빈 JSON 객체로 초기화
        console.print("[green]acme.json has been created.[/green]")

    # 파일 권한을 600으로 설정
    console.print("[yellow]Setting permissions for acme.json...[/yellow]")
    os.chmod(acme_file_path, 0o600)
    console.print("[green]Permissions for acme.json have been set to 600.[/green]")

    yaml = YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)

    # docker-compose.yml 파일 생성
    docker_compose_content = {
        "version": "3.8",
        "services": {
            "reverse-proxy": {
                "image": "traefik:v3.1",
                "network_mode": "host",
                "command": ["--configFile=/traefik.yml"],
                "ports": [
                    "80:80",
                    "443:443",
                    "8080:8080"
                ],
                "volumes": [
                    "/var/run/docker.sock:/var/run/docker.sock",
                    "/etc/localtime:/etc/localtime:ro",
                    "./dynamic_conf.yml:/dynamic_conf.yml",
                    "./traefik.yml:/traefik.yml",
                    f"{cert_file_path}:/fullchain.pem",
                    f"{key_file_path}:/privkey.pem",
                    "./acme.json:/acme.json"
                ]
            }
        }
    }

    # docker-compose.yml 파일 저장
    with open('./docker-compose.yml', 'w') as file:
        yaml.dump(docker_compose_content, file)

    console.print("[green]docker-compose.yml has been generated.[/green]")

    # Docker Compose로 Traefik 실행
    try:
        console.print("[yellow]Stopping any running Traefik instances...[/yellow]")
        subprocess.run(["docker", "compose", "down"], check=True)

        console.print("[yellow]Starting Traefik using Docker Compose...[/yellow]")
        subprocess.run(["docker", "compose", "up", "-d"], check=True)
        console.print("[green]Traefik is up and running![/green]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error occurred while starting Traefik: {e}[/red]")


if __name__ == "__main__":
    app()
