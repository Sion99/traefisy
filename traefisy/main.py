import typer
from rich.console import Console
from rich.table import Table
from . import utils
from .db.db import get_db, init_db
from .utils import add_router, is_router_duplicate, get_routers
from sqlalchemy.orm import Session
import yaml

app = typer.Typer()
console = Console()


@app.command()
def init():
    init_db()

    db: Session = next(get_db())

    # Welcome 메시지
    console.print("[bold cyan]Welcome to traefisy![/bold cyan]\n")

    # EntryPoints 설정
    if typer.confirm("Would you like to configure HTTP and HTTPS EntryPoints?", default=True):
        http_port = typer.prompt("Please enter the HTTP port", default="80")
        https_port = typer.prompt("Please enter the HTTPS port", default="443")

    # TLS/HTTPS 설정
    tls = False

    if typer.confirm("Would you like to enable HTTPS using Let's Encrypt?", default=True):
        acme_email = typer.prompt("Please enter your ACME email")
        cert_directory = typer.prompt("Please enter the directory to save certificates")
        tls = True

    # 라우터 설정 (반복문)
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

    # 미들웨어 설정
    # if typer.confirm("Would you like to configure middleware?", default=True):
    #     if typer.confirm("Would you like to redirect HTTP to HTTPS?", default=True):
    #
    #     if typer.confirm("Would you like to set up Basic Auth?", default=False):
    #         # Basic Auth 설정 로직 추가 가능
    #         pass

    # 라우터 추가 예시

    # 추가 로직


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

    removed = utils.remove_router(db, identifier)
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

    # dynamic_conf.yml 파일 생성
    config = {
        "http": {
            "routers": {},
            "services": {},
            "middlewares": {}
        }
    }

    for router in routers:
        config["http"]["routers"][router.name] = {
            "rule": f"Host(`{router.domain}`)",
            "service": router.service_name,
            "entryPoints": [router.entrypoints]
        }

        if router.tls:
            config["http"]["routers"][router.name]["tls"] = {"certResolver": "letsencrypt"}

        config["http"]["services"][router.service_name] = {
            "loadBalancer": {
                "servers": [
                    {"url": router.service_url}
                ]
            }
        }

    with open('../dynamic_conf.yml', 'w') as file:
        yaml.dump(config, file)

    console.print("[green]dynamic_conf.yml has been generated.[/green]")


if __name__ == "__main__":
    app()
