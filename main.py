import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
import yaml

app = typer.Typer()
console = Console()


def save_config(config: dict, filename: str = "dynamic_conf.yml"):
    with open(filename, "w") as file:
        yaml.dump(config, file)


@app.command()
def init():
    config = {
        "entryPoints": {},
        "http": {
            "routers": {},
            "services": {},
            "middlewares": {}
        },
        "tls": []
    }

    # Welcome 메시지
    console.print("[bold cyan]Welcome to Traefisy initialization![/bold cyan]\n")

    # EntryPoints 설정
    if Confirm.ask("Would you like to configure HTTP and HTTPS EntryPoints?", default=True):
        http_port = Prompt.ask("Please enter the HTTP port", default="80")
        https_port = Prompt.ask("Please enter the HTTPS port", default="443")
        config["entryPoints"]["web"] = {"address": f":{http_port}"}
        config["entryPoints"]["websecure"] = {"address": f":{https_port}"}

    # 라우터 설정 (반복문)
    while True:
        if not Confirm.ask("Would you like to add a router?", default=True):
            break

        router_name = Prompt.ask("Router name")
        routing_rule = Prompt.ask("Please enter the routing rule (e.g., Host(\"example.com\"))")
        service_name = Prompt.ask("Please enter the service name to link with the router")
        service_url = Prompt.ask("Please enter the service URL")

        config["http"]["routers"][router_name] = {
            "rule": routing_rule,
            "service": service_name,
            "entryPoints": ["web", "websecure"]
        }
        config["http"]["services"][service_name] = {
            "loadBalancer": {
                "servers": [
                    {"url": service_url}
                ]
            }
        }

        console.print(f"[green]{router_name} router has been successfully added![/green]\n")

    # TLS/HTTPS 설정
    if Confirm.ask("Would you like to enable HTTPS using Let's Encrypt?", default=True):
        acme_email = Prompt.ask("Please enter your ACME email")
        cert_directory = Prompt.ask("Please enter the directory to save certificates")
        config["tls"].append({
            "certificates": [
                {
                    "certFile": f"{cert_directory}/cert.pem",
                    "keyFile": f"{cert_directory}/key.pem"
                }
            ]
        })
        config["http"]["routers"][router_name]["tls"] = {"certResolver": "letsencrypt"}

    # 미들웨어 설정
    if Confirm.ask("Would you like to configure middleware?", default=True):
        if Confirm.ask("Would you like to redirect HTTP to HTTPS?", default=True):
            config["http"]["middlewares"]["redirect-to-https"] = {
                "redirectScheme": {
                    "scheme": "https"
                }
            }
            config["http"]["routers"][router_name]["middlewares"] = ["redirect-to-https"]

        if Confirm.ask("Would you like to set up Basic Auth?", default=False):
            # Basic Auth 설정 로직 추가 가능
            pass

    # 설정 파일 저장
    save_config(config)
    console.print("\n[bold cyan]Traefik configuration completed and saved in 'dynamic_conf.yml'.[/bold cyan]")


if __name__ == "__main__":
    app()
