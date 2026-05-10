import argparse
import json
from typing import Any

import httpx
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from app.core.settings import settings

console = Console()


def _raise_for_status(response: httpx.Response) -> None:
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        try:
            detail = response.json().get("detail", response.text)
        except json.JSONDecodeError:
            detail = response.text
        raise RuntimeError(str(detail)) from exc


def _resolve_company_id(client: httpx.Client, identifier: str) -> str:
    response = client.get("/companies", params={"limit": 100})
    _raise_for_status(response)
    for company in response.json():
        if company["id"] == identifier or company["name"].lower() == identifier.lower():
            return company["id"]
    raise RuntimeError(f"Company not found: {identifier}")


def _print_company_detail(company: dict[str, Any]) -> None:
    console.print(
        Panel.fit(f"[bold cyan]{company['name']}[/bold cyan]\n[dim]{company['industry']}[/dim]")
    )
    console.print(Markdown(f"### Overview\n{company['overview']}"))
    console.print(Markdown(f"### Products\n{company['products']}"))
    console.print(Markdown(f"### Competitors\n{company['competitors']}"))
    console.print(Markdown(f"### Recent News\n{company['recent_news']}"))


def research(company_name: str) -> None:
    console.print(f"[bold]Researching {company_name}...[/bold]")
    with httpx.Client(base_url=settings.API_BASE_URL, timeout=120) as client:
        response = client.post("/companies", json={"company_name": company_name})
        _raise_for_status(response)
        company = response.json()
    console.print(f"[green]Research saved (ID: {company['id']})[/green]\n")
    _print_company_detail(company)


def list_companies() -> None:
    with httpx.Client(base_url=settings.API_BASE_URL, timeout=30) as client:
        response = client.get("/companies")
        _raise_for_status(response)
        companies = response.json()
    table = Table(title="Researched Companies")
    table.add_column("ID", overflow="fold")
    table.add_column("Name")
    table.add_column("Industry")
    for c in companies:
        table.add_row(c["id"], c["name"], c["industry"])
    console.print(table)


def show_company(identifier: str) -> None:
    with httpx.Client(base_url=settings.API_BASE_URL, timeout=30) as client:
        cid = _resolve_company_id(client, identifier)
        response = client.get(f"/companies/{cid}")
        _raise_for_status(response)
    _print_company_detail(response.json())


def delete_company(identifier: str) -> None:
    with httpx.Client(base_url=settings.API_BASE_URL, timeout=30) as client:
        cid = _resolve_company_id(client, identifier)
        response = client.delete(f"/companies/{cid}")
        _raise_for_status(response)
    console.print("[green]Deleted.[/green]")


def list_sessions(identifier: str) -> None:
    with httpx.Client(base_url=settings.API_BASE_URL, timeout=30) as client:
        cid = _resolve_company_id(client, identifier)
        response = client.get(f"/companies/{cid}/sessions")
        _raise_for_status(response)
        sessions = response.json()
    if not sessions:
        console.print("[yellow]No sessions found.[/yellow]")
        return
    table = Table(title="Chat Sessions")
    table.add_column("ID", overflow="fold")
    table.add_column("Created At")
    for s in sessions:
        table.add_row(s["id"], s["created_at"])
    console.print(table)


def history(identifier: str, session_id: str) -> None:
    with httpx.Client(base_url=settings.API_BASE_URL, timeout=30) as client:
        cid = _resolve_company_id(client, identifier)
        response = client.get(f"/companies/{cid}/sessions/{session_id}/messages")
        _raise_for_status(response)
        messages = response.json()
    if not messages:
        console.print("[yellow]No messages found.[/yellow]")
        return
    for msg in messages:
        if msg["role"] == "user":
            console.print(f"\n[bold]You:[/bold] {msg['content']}")
        else:
            console.print("\n[bold]Company Lens:[/bold]")
            console.print(Markdown(msg["content"]))


def chat(identifier: str) -> None:
    with httpx.Client(base_url=settings.API_BASE_URL, timeout=120) as client:
        cid = _resolve_company_id(client, identifier)
        response = client.post(f"/companies/{cid}/sessions")
        _raise_for_status(response)
        sid = response.json()["id"]
        console.print(f"[green]Session: {sid}[/green]\nType 'exit' to quit.\n")

        while True:
            user_input = console.input("[bold]You:[/bold] ").strip()
            if user_input.lower() in {"exit", "quit"}:
                break
            if not user_input:
                continue
            console.print("[bold]Company Lens:[/bold] ", end="")
            with client.stream(
                "POST",
                f"/companies/{cid}/sessions/{sid}/messages",
                json={"content": user_input},
                timeout=120,
            ) as stream:
                _raise_for_status(stream)
                for line in stream.iter_lines():
                    if not line.startswith("data: "):
                        continue
                    payload = json.loads(line.removeprefix("data: "))
                    if payload["type"] == "text_delta":
                        console.print(payload["content"], end="")
                    elif payload["type"] == "error":
                        raise RuntimeError(payload["message"])
                    elif payload["type"] == "done":
                        console.print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Company Lens CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("research")
    p.add_argument("company_name", nargs="+")
    sub.add_parser("list")
    p = sub.add_parser("show")
    p.add_argument("company", nargs="+")
    p = sub.add_parser("delete")
    p.add_argument("company", nargs="+")
    p = sub.add_parser("sessions")
    p.add_argument("company", nargs="+")
    p = sub.add_parser("history")
    p.add_argument("company", nargs="+")
    p.add_argument("session_id")
    p = sub.add_parser("chat")
    p.add_argument("company", nargs="+")

    args = parser.parse_args()
    try:
        if args.command == "research":
            research(" ".join(args.company_name))
        elif args.command == "list":
            list_companies()
        elif args.command == "show":
            show_company(" ".join(args.company))
        elif args.command == "delete":
            delete_company(" ".join(args.company))
        elif args.command == "sessions":
            list_sessions(" ".join(args.company))
        elif args.command == "history":
            history(" ".join(args.company), args.session_id)
        elif args.command == "chat":
            chat(" ".join(args.company))
    except (httpx.HTTPError, RuntimeError) as exc:
        console.print(f"[red]Error:[/red] {exc}")


if __name__ == "__main__":
    main()
