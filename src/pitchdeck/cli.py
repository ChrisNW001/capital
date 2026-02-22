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
    save_json: Annotated[
        str,
        typer.Option("--json", help="Path for JSON output (always saved; default: replaces .md with .json)"),
    ] = "",
):
    """Generate a pitch deck from company documents."""
    import os

    from pitchdeck.engine.gaps import detect_gaps, fill_gaps_interactive
    from pitchdeck.engine.narrative import generate_deck
    from pitchdeck.engine.slides import get_slide_templates
    from pitchdeck.models import CompanyProfile, DocumentParseError, PitchDeckError, ProfileNotFoundError
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
        except FileNotFoundError:
            console.print(f"  [red]FAIL[/red] {path}: File not found")
            raise typer.Exit(1)
        except PermissionError:
            console.print(f"  [red]FAIL[/red] {path}: Permission denied")
            raise typer.Exit(1)
        except DocumentParseError as e:
            console.print(f"  [red]FAIL[/red] {path}: {e}")
            raise typer.Exit(1)
        except Exception as e:
            console.print(f"  [red]FAIL[/red] {path}: {type(e).__name__}: {e}")
            raise typer.Exit(1)

    # 2. Load VC profile
    console.print(f"\n[bold]Loading VC profile: {vc}[/bold]")
    try:
        vc_profile = load_vc_profile(vc)
        console.print(
            f"  [green]OK[/green] {vc_profile.name} "
            f"({len(vc_profile.thesis_points)} thesis points)"
        )
    except ProfileNotFoundError as e:
        console.print(f"  [red]FAIL[/red] {e}")
        console.print("  Run [bold]pitchdeck profiles[/bold] to see available profiles.")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"  [red]FAIL[/red] {type(e).__name__}: {e}")
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
    try:
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
    except PitchDeckError as e:
        console.print(f"\n[red]Generation failed: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"\n[red]Unexpected error during generation: {type(e).__name__}: {e}[/red]")
        raise typer.Exit(1)

    # 6. Save output
    try:
        save_markdown(deck, output)
        console.print(f"\n[bold green]Deck saved to {output}[/bold green]")
        console.print(f"  Slides: {len(deck.slides)}")
    except OSError as e:
        console.print(
            f"\n[bold red]Error: Failed to save deck to {output}: {e}[/bold red]"
        )
        console.print("[red]Check file permissions and disk space.[/red]")
        raise typer.Exit(1)

    # 7. Save JSON (always — path defaults to output with .json extension; --json overrides)
    if save_json:
        json_path = save_json
    else:
        json_path = output.rsplit(".", 1)[0] + ".json"
    try:
        with open(json_path, "w") as f:
            f.write(deck.model_dump_json(indent=2))
        console.print(f"  JSON: {json_path}")
    except OSError as e:
        console.print(
            f"\n[bold red]Error: Failed to save JSON to {json_path}: {e}[/bold red]"
        )
        console.print(
            "[red]The deck was saved as Markdown but cannot be validated. "
            "Check file permissions and disk space.[/red]"
        )
        raise typer.Exit(1)

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


@app.command()
def validate(
    deck_file: Annotated[
        str,
        typer.Argument(help="Path to deck JSON file"),
    ],
    vc: Annotated[
        str,
        typer.Option("--vc", "-v", help="VC profile name (without .yaml)"),
    ] = "earlybird",
    output: Annotated[
        str,
        typer.Option("--output", "-o", help="Validation report output path"),
    ] = "validation_report.md",
    threshold: Annotated[
        int,
        typer.Option("--threshold", "-t", help="Pass/fail threshold (0-100)"),
    ] = 60,
    skip_llm: Annotated[
        bool,
        typer.Option("--skip-llm", help="Skip LLM scoring (rule-based only)"),
    ] = False,
):
    """Score a pitch deck against VC-specific rubrics."""
    from pitchdeck.engine.validator import validate_deck
    from pitchdeck.models import PitchDeck, PitchDeckError, ProfileNotFoundError
    from pitchdeck.output import save_validation_report
    from pitchdeck.profiles import load_vc_profile

    # 1. Read deck JSON
    console.print(f"[bold]Loading deck: {deck_file}[/bold]")
    try:
        with open(deck_file) as f:
            deck_data = f.read()
    except FileNotFoundError:
        console.print(f"  [red]FAIL[/red] File not found: {deck_file}")
        raise typer.Exit(1)
    except OSError as e:
        console.print(f"  [red]FAIL[/red] Cannot read file: {e}")
        raise typer.Exit(1)

    import json as json_mod

    from pydantic import ValidationError

    try:
        deck = PitchDeck.model_validate_json(deck_data)
        console.print(
            f"  [green]OK[/green] {deck.company_name} "
            f"({len(deck.slides)} slides)"
        )
    except ValidationError as e:
        console.print(f"  [red]FAIL[/red] Invalid deck JSON schema:")
        for err in e.errors()[:5]:
            loc = " > ".join(str(l) for l in err["loc"])
            console.print(f"    {loc}: {err['msg']}")
        raise typer.Exit(1)
    except json_mod.JSONDecodeError as e:
        console.print(f"  [red]FAIL[/red] File is not valid JSON: {e}")
        console.print("  [dim]Hint: use the .json file produced by 'pitchdeck generate', not the .md file.[/dim]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"  [red]FAIL[/red] Cannot parse deck JSON: {e}")
        raise typer.Exit(1)

    # 2. Load VC profile
    console.print(f"\n[bold]Loading VC profile: {vc}[/bold]")
    try:
        vc_profile = load_vc_profile(vc)
        console.print(
            f"  [green]OK[/green] {vc_profile.name} "
            f"({len(vc_profile.custom_checks)} custom checks)"
        )
    except (ProfileNotFoundError, FileNotFoundError):
        console.print(f"  [red]FAIL[/red] Profile '{vc}' not found.")
        console.print("  Run [bold]pitchdeck profiles[/bold] to see available profiles.")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"  [red]FAIL[/red] Could not load profile '{vc}': {e}")
        raise typer.Exit(1)

    # 3. Validate
    if not 0 <= threshold <= 100:
        console.print(
            f"[red]Error: --threshold must be between 0 and 100, got {threshold}[/red]"
        )
        raise typer.Exit(1)

    if not skip_llm:
        import os

        if not os.environ.get("ANTHROPIC_API_KEY"):
            console.print(
                "[red]Error: ANTHROPIC_API_KEY not set. "
                "Use --skip-llm for rule-based scoring only.[/red]"
            )
            raise typer.Exit(1)

    try:
        if not skip_llm:
            with Progress(
                SpinnerColumn(),
                TextColumn(
                    "[progress.description]{task.description}"
                ),
                console=console,
            ) as progress:
                task = progress.add_task(
                    "Scoring deck with Claude...", total=None
                )
                result = validate_deck(
                    deck, vc_profile, threshold, skip_llm
                )
                progress.remove_task(task)
        else:
            console.print(
                "\n[bold]Running rule-based validation (--skip-llm)...[/bold]"
            )
            result = validate_deck(
                deck, vc_profile, threshold, skip_llm=True
            )
    except PitchDeckError as e:
        console.print(f"  [red]Validation failed: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"  [red]Unexpected error during validation: {type(e).__name__}: {e}[/red]")
        raise typer.Exit(1)

    # 4. Save report
    report_saved = False
    try:
        save_validation_report(result, output)
        report_saved = True
    except OSError as e:
        console.print(
            f"\n[bold red]Error: Failed to save report to {output}: {e}[/bold red]"
        )
        console.print("[red]Check disk space and directory permissions.[/red]")
    except Exception as e:
        console.print(
            f"\n[bold red]Error: Unexpected {type(e).__name__} while rendering/saving "
            f"report to {output}: {e}[/bold red]"
        )
        console.print(
            "[red]This may be a bug in the report renderer. "
            "Please report this issue.[/red]"
        )
        raise typer.Exit(1)

    # 5. Print summary
    pass_fail = "[green]PASS[/green]" if result.pass_fail else "[red]FAIL[/red]"
    console.print(f"\n[bold]Overall Score: {result.overall_score}/100 — {pass_fail}[/bold]")
    console.print("")
    for dim in result.dimension_scores:
        name = dim.dimension.replace("_", " ").title()
        console.print(f"  {name}: {dim.score}/100")

    passed_checks = sum(1 for c in result.custom_check_results if c.passed)
    total_checks = len(result.custom_check_results)
    if total_checks:
        console.print(
            f"\n  VC Checks: {passed_checks}/{total_checks} passed"
        )

    if result.improvement_priorities:
        console.print("\n[bold yellow]Top Improvements:[/bold yellow]")
        for i, p in enumerate(result.improvement_priorities[:5], 1):
            console.print(f"  {i}. {p}")

    if report_saved:
        console.print(f"\n[bold]Report saved to {output}[/bold]")
    else:
        console.print(f"\n[bold red]Report not saved — see error above.[/bold red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
