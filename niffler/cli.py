"""
Rich interactive CLI for Niffler — Autonomous Travel & Citizen FinTech Super-Agent.
"""

import sys
import argparse
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from .travel.flights import FlightRadar
from .travel.hotels import HotelRadar
from .travel.trains import IRCTCRadar
from .travel.buses import BusRadar
from .travel.booking_handoff import BookingHandoffEngine
from .citizen.itr_optimizer import ITROptimizer
from .citizen.epf_explorer import EPFExplorer
from .web.server import start_server
from .config import NifflerConfig, BharatConfig

console = Console()


def print_banner():
    banner = """
[bold gold1]   _   _ ___ _____ _____ _     _____ ____  [/bold gold1]
[bold gold1]  | \\ | |_ _|  ___|  ___| |   | ____|  _ \\ [/bold gold1]
[bold gold1]  |  \\| || || |_  | |_  | |   |  _| | |_) |[/bold gold1]
[bold gold1]  | |\\  || ||  _| |  _| | |___| |___|  _ < [/bold gold1]
[bold gold1]  |_| \\_|___|_|   |_|   |_____|_____|_| \\_\\ [/bold gold1]
[bold yellow]✨ Autonomous Travel Concierge & Citizen FinTech Agent ✨[/bold yellow]
[dim italic]  "Sniffing out the cheapest flights, IRCTC seats, tax refunds & EPF gold"[/dim italic]
"""
    console.print(banner)


def handle_flights(args):
    radar = FlightRadar()
    origin = args.origin.upper()
    dest = args.destination.upper()
    console.print(f"[*] Scanning flight fares across airlines from [bold]{origin}[/bold] to [bold]{dest}[/bold]...\n")
    flights = radar.search_flights(origin, dest, max_price=args.max_price, direct_only=args.direct)

    table = Table(title=f"Flight Options: {origin} ➔ {dest}", box=box.ROUNDED)
    table.add_column("Airline", style="bold cyan")
    table.add_column("Flight No.", style="dim")
    table.add_column("Departure", justify="center")
    table.add_column("Arrival", justify="center")
    table.add_column("Duration", justify="center")
    table.add_column("Stops", justify="center")
    table.add_column("Fare (INR)", justify="right", style="bold green")
    table.add_column("Tags", style="yellow")

    for f in flights:
        tag = "🏆 LOWEST" if f.is_cheapest else ("⚡ FASTEST" if f.is_fastest else "")
        stops_str = "Non-stop" if f.stops == 0 else f"{f.stops} stop"
        table.add_row(
            f.airline,
            f.flight_number,
            f.departure_time,
            f.arrival_time,
            f.duration,
            stops_str,
            f"₹{f.price_inr:,}",
            tag
        )

    console.print(table)


def handle_hotels(args):
    radar = HotelRadar()
    city = args.city.title()
    console.print(f"[*] Discovering stays & homestays in [bold]{city}[/bold]...\n")
    hotels = radar.search_hotels(city, max_budget=args.budget, couple_friendly_only=args.couple)

    table = Table(title=f"Stays & Homestays in {city}", box=box.ROUNDED)
    table.add_column("Property", style="bold white")
    table.add_column("Type", style="cyan")
    table.add_column("Location", style="dim")
    table.add_column("Rating", justify="center", style="yellow")
    table.add_column("Price/Night", justify="right", style="bold green")
    table.add_column("Highlights")

    for h in hotels:
        highlights = ", ".join(h.amenities[:2])
        if h.couple_friendly:
            highlights += " • Couple Friendly"
        table.add_row(
            h.name,
            h.property_type,
            h.location,
            f"★ {h.user_rating} ({h.reviews_count:,})",
            f"₹{h.price_per_night_inr:,}",
            highlights
        )

    console.print(table)


def handle_trains(args):
    radar = IRCTCRadar()
    orig = args.origin.upper()
    dest = args.destination.upper()
    console.print(f"[*] Checking IRCTC routes & seat availability from [bold]{orig}[/bold] to [bold]{dest}[/bold]...\n")
    trains = radar.search_trains(orig, dest)

    table = Table(title=f"IRCTC Trains: {orig} ➔ {dest}", box=box.ROUNDED)
    table.add_column("Train No.", style="bold cyan")
    table.add_column("Train Name", style="white")
    table.add_column("Dep - Arr", justify="center")
    table.add_column("Duration", justify="center")
    table.add_column("Live Berths / Availability", style="green")

    for t in trains:
        classes_str = " | ".join(f"{k}: {v}" for k, v in t.classes_available.items())
        table.add_row(
            t.train_number,
            t.train_name,
            f"{t.departure_time} - {t.arrival_time}",
            t.travel_time,
            classes_str
        )

    console.print(table)
    advisory = radar.get_tatkal_advisory()
    console.print(Panel(
        f"[bold yellow]Tatkal Opening Windows:[/bold yellow]\n• AC Classes: {advisory['ac_tatkal_opens']}\n• Non-AC Classes: {advisory['non_ac_tatkal_opens']}\n\n[bold green]Pro-Tips:[/bold green]\n{advisory['pro_tips']}",
        title="⏰ IRCTC Tatkal Master Guide",
        box=box.ROUNDED
    ))


def handle_itr(args):
    optimizer = ITROptimizer()
    console.print("[*] Running Autonomous Tax Optimization (Old vs New Regime)...\n")
    res = optimizer.optimize_and_generate_itr(
        pan=args.pan,
        name=args.name,
        gross_salary=args.salary,
        sec_80c=args.sec80c,
        sec_80d=args.sec80d,
        hra_exemption=args.hra,
        tds_deducted=args.tds
    )

    table = Table(title=f"ITR Showdown: Assessment Year {res.assessment_year}", box=box.ROUNDED)
    table.add_column("Metric", style="bold")
    table.add_column("New Tax Regime (115BAC)", justify="right", style="cyan")
    table.add_column("Old Tax Regime", justify="right", style="magenta")

    table.add_row("Gross Salary", f"₹{res.new_regime.gross_salary:,}", f"₹{res.old_regime.gross_salary:,}")
    table.add_row("Exemptions & Deductions", f"₹{res.new_regime.exemptions_and_deductions:,}", f"₹{res.old_regime.exemptions_and_deductions:,}")
    table.add_row("Net Taxable Income", f"₹{res.new_regime.net_taxable_income:,}", f"₹{res.old_regime.net_taxable_income:,}")
    table.add_row("Tax Before Cess", f"₹{res.new_regime.tax_before_cess:,}", f"₹{res.old_regime.tax_before_cess:,}")
    table.add_row("87A Rebate", f"₹{res.new_regime.rebate_87a:,}", f"₹{res.old_regime.rebate_87a:,}")
    table.add_row("Health & Education Cess (4%)", f"₹{res.new_regime.health_education_cess:,}", f"₹{res.old_regime.health_education_cess:,}")
    table.add_row("[bold]Total Tax Payable[/bold]", f"[bold green]₹{res.new_regime.total_tax_payable:,}[/bold green]", f"[bold yellow]₹{res.old_regime.total_tax_payable:,}[/bold yellow]")

    console.print(table)
    rec_text = "New Tax Regime" if res.recommended_regime == "NEW_REGIME" else "Old Tax Regime"
    console.print(Panel(
        f"[bold green]🏆 Recommendation: Choose {rec_text}[/bold green]\n"
        f"You save [bold]₹{res.tax_savings_inr:,}[/bold] in annual taxes!\n\n"
        f"Compliant ITR-1 (Sahaj) JSON payload generated successfully.",
        title="Tax Verdict",
        box=box.ROUNDED
    ))


def handle_epf(args):
    explorer = EPFExplorer()
    console.print("[*] Inspecting EPF Passbook & Government Compounding Corpus...\n")
    summary = explorer.parse_or_simulate_account(
        uan=args.uan,
        monthly_basic_da=args.basic,
        years_of_service=args.tenure,
        starting_epf_balance=args.balance
    )
    rules = explorer.check_withdrawal_eligibility(args.tenure, summary.employee_share_balance_inr)
    proj = explorer.project_retirement_corpus(monthly_basic_da=args.basic, current_balance=summary.total_epf_balance_inr)

    table = Table(title=f"EPFO Account Summary (UAN: {summary.uan})", box=box.ROUNDED)
    table.add_column("Account Component", style="bold")
    table.add_column("Current Balance", justify="right", style="bold green")

    table.add_row("Employee Share (12% contrib)", f"₹{summary.employee_share_balance_inr:,}")
    table.add_row("Employer Share (3.67% to PF)", f"₹{summary.employer_share_balance_inr:,}")
    table.add_row("Pension Scheme (8.33% to EPS)", f"₹{summary.pension_scheme_balance_inr:,}")
    table.add_row("[bold cyan]Total EPF Accumulation[/bold cyan]", f"[bold cyan]₹{summary.total_epf_balance_inr:,}[/bold cyan]")
    console.print(table)

    console.print(Panel(
        f"[bold green]Estimated Retirement Corpus at Age 58:[/bold green] [bold white]₹{proj.projected_corpus_at_58_inr:,}[/bold white]\n"
        f"Total Compounding Interest Earned: [bold green]₹{proj.total_interest_earned_inr:,}[/bold green]\n\n"
        f"[bold yellow]Withdrawal Rules:[/bold yellow]\n"
        f"• Medical (Form 31): {rules.form_31_medical['rule']}\n"
        f"• Housing (Form 31): {'Eligible' if rules.form_31_housing['eligible'] else 'Ineligible'} ({rules.form_31_housing['rule']})\n"
        f"• Full Settlement (Form 19): {rules.form_19_full_settlement['rule']}",
        title="EPFO Advisory & Wealth Projection",
        box=box.ROUNDED
    ))


def main():
    print_banner()
    parser = argparse.ArgumentParser(description="Niffler: Autonomous Travel & Citizen FinTech Super-Agent")
    subparsers = parser.add_subparsers(dest="command")

    # travel
    travel_parser = subparsers.add_parser("travel", help="Travel search operations")
    travel_sub = travel_parser.add_subparsers(dest="subcommand")

    p_flights = travel_sub.add_parser("flights")
    p_flights.add_argument("origin", default="DEL", nargs="?")
    p_flights.add_argument("destination", default="BLR", nargs="?")
    p_flights.add_argument("--max-price", type=int, default=None)
    p_flights.add_argument("--direct", action="store_true")

    p_hotels = travel_sub.add_parser("hotels")
    p_hotels.add_argument("city", default="GOA", nargs="?")
    p_hotels.add_argument("--budget", type=int, default=None)
    p_hotels.add_argument("--couple", action="store_true")

    p_trains = travel_sub.add_parser("trains")
    p_trains.add_argument("origin", default="NDLS", nargs="?")
    p_trains.add_argument("destination", default="MMCT", nargs="?")

    # itr
    p_itr = subparsers.add_parser("itr", help="Tax calculation & ITR-1 generator")
    p_itr.add_argument("salary", type=int, default=1200000, nargs="?")
    p_itr.add_argument("--sec80c", type=int, default=150000)
    p_itr.add_argument("--sec80d", type=int, default=25000)
    p_itr.add_argument("--hra", type=int, default=120000)
    p_itr.add_argument("--tds", type=int, default=75000)
    p_itr.add_argument("--pan", type=str, default="ABCDE1234F")
    p_itr.add_argument("--name", type=str, default="Shubhransh Gupta")

    # epf
    p_epf = subparsers.add_parser("epf", help="EPF passbook analyzer & retirement calculator")
    p_epf.add_argument("basic", type=int, default=50000, nargs="?")
    p_epf.add_argument("--tenure", type=float, default=4.5)
    p_epf.add_argument("--balance", type=int, default=350000)
    p_epf.add_argument("--uan", type=str, default="101234567890")

    # web
    p_web = subparsers.add_parser("web", help="Start the interactive web portal")
    p_web.add_argument("--port", type=int, default=8501)
    p_web.add_argument("--host", type=str, default="127.0.0.1")

    args = parser.parse_args()

    if args.command == "travel":
        if args.subcommand == "flights":
            handle_flights(args)
        elif args.subcommand == "hotels":
            handle_hotels(args)
        elif args.subcommand == "trains":
            handle_trains(args)
        else:
            travel_parser.print_help()
    elif args.command == "itr":
        handle_itr(args)
    elif args.command == "epf":
        handle_epf(args)
    elif args.command == "web":
        start_server(host=args.host, port=args.port)
    else:
        # Default run flight search demo
        console.print("[yellow]Tip: Run with `travel`, `itr`, `epf`, or `web` subcommands.[/yellow]\n")
        class DemoArgs:
            origin = "DEL"
            destination = "BLR"
            max_price = None
            direct = False
        handle_flights(DemoArgs())


if __name__ == "__main__":
    main()
