"""Typer CLI application for pitch deck generation."""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

app = typer.Typer(
    name="pitchdeck",
    help="Generate investor-grade pitch decks from company documents.",
    rich_markup_mode="rich",
)
console = Console()


@app.command()
def generate(
    input_files: Annotated[
        list[str],
        typer.Argument(help="Paths to company PDFs or DOCXs"),
    ],
    vc: Annotated[
        str,
        typer.Option("--vc", "-v", help="VC profile name (without .yaml)"),
    ] = "earlybird",
    output: Annotated[
        str,
        typer.Option("--output", "-o", help="Output Markdown file path"),
    ] = "deck.md",
    skip_gaps: Annotated[
        bool,
        typer.Option("--skip-gaps", help="Skip interactive gap-filling"),
    ] = False,
):
    """Generate a pitch deck from company documents."""
    import os

    from pitchdeck.engine.gaps import detect_gaps, fill_gaps_interactive
    from pitchdeck.engine.narrative import generate_deck
    from pitchdeck.engine.slides import get_slide_templates
    from pitchdeck.models import CompanyProfile
    from pitchdeck.output import save_markdown
    from pitchdeck.parsers import extract_document
    from pitchdeck.profiles import load_vc_profile

    # Check API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        console.print(
            "[red]Error: ANTHROPIC_API_KEY environment variable not set[/red]"
        )
        raise typer.Exit(1)

    # 1. Parse documents
    console.print(f"[bold]Parsing {len(input_files)} document(s)...[/bold]")
    combined_text = ""
    for path in input_files:
        try:
            text = extract_document(path)
            combined_text += (
                f"\n\n--- Document: {Path(path).name} ---\n\n{text}"
            )
            console.print(f"  [green]OK[/green] {path} ({len(text)} chars)")
        except Exception as e:
            console.print(f"  [red]FAIL[/red] {path}: {e}")
            raise typer.Exit(1)

    # 2. Load VC profile
    console.print(f"\n[bold]Loading VC profile: {vc}[/bold]")
    try:
        vc_profile = load_vc_profile(vc)
        console.print(
            f"  [green]OK[/green] {vc_profile.name} "
            f"({len(vc_profile.thesis_points)} thesis points)"
        )
    except Exception as e:
        console.print(f"  [red]FAIL[/red] {e}")
        raise typer.Exit(1)

    # 3. Build initial company profile from extracted text
    company = CompanyProfile(
        name="",
        product_name="",
        one_liner="",
        founded_year=0,
        employee_count=0,
        revenue_eur=0,
        revenue_type="revenue",
        funding_stage="bootstrapped",
        raw_document_text=combined_text,
    )

    # 4. Detect and fill gaps
    templates = get_slide_templates(vc_profile)
    gaps = detect_gaps(company, templates)
    if gaps and not skip_gaps:
        console.print(
            f"\n[bold yellow]Found {len(gaps)} information gaps:[/bold yellow]"
        )
        company = fill_gaps_interactive(company, gaps)
    elif gaps:
        console.print(f"\n[dim]Skipping {len(gaps)} gaps (--skip-gaps)[/dim]")

    # 5. Generate deck
    console.print(f"\n[bold]Generating {len(templates)}-slide deck...[/bold]")
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(
            "Generating slides with Claude...", total=None
        )
        deck = generate_deck(company, vc_profile, templates)
        progress.remove_task(task)

    # 6. Save output
    save_markdown(deck, output)
    console.print(f"\n[bold green]Deck saved to {output}[/bold green]")
    console.print(f"  Slides: {len(deck.slides)}")
    if deck.gaps_identified:
        console.print(
            f"  [yellow]Remaining gaps: {len(deck.gaps_identified)}[/yellow]"
        )


@app.command()
def profiles():
    """List available VC profiles."""
    from pitchdeck.profiles import list_profiles

    available = list_profiles()
    if not available:
        console.print(
            "[yellow]No profiles found in profiles/ directory[/yellow]"
        )
    else:
        console.print("[bold]Available VC profiles:[/bold]")
        for name in available:
            console.print(f"  - {name}")


if __name__ == "__main__":
    app()
