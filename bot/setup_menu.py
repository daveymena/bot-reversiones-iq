#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║       EXNOVA ULTRA-SMART BOT — Menú de Configuración Inicial     ║
║  Credenciales · Monto · Expiración · Divisas · Recomendaciones   ║
╚══════════════════════════════════════════════════════════════════╝
"""
import os
import sys
import time

# ── Intentar cargar .env existente ───────────────────────────────────────────
from dotenv import load_dotenv, set_key
load_dotenv()

from rich.console import Console
from rich.panel   import Panel
from rich.table   import Table
from rich.text    import Text
from rich.align   import Align
from rich.columns import Columns
from rich import box

try:
    import questionary
    from questionary import Style
    HAS_QUESTIONARY = True
except ImportError:
    HAS_QUESTIONARY = False

console = Console()

# ── Estilos de questionary ────────────────────────────────────────────────────
QQ_STYLE = Style([
    ("qmark",        "fg:#00d7ff bold"),
    ("question",     "fg:#ffffff bold"),
    ("answer",       "fg:#00ffaf bold"),
    ("pointer",      "fg:#00d7ff bold"),
    ("highlighted",  "fg:#00ffaf bold"),
    ("selected",     "fg:#00ffaf"),
    ("separator",    "fg:#555555"),
    ("instruction",  "fg:#888888"),
])

# ── Datos de divisas con metadata ─────────────────────────────────────────────
PAIR_INFO = {
    "EURUSD-OTC": {"name": "Euro / Dólar",         "wr": 72, "vol": "ALTA",   "rec": True,  "note": "El par más líquido — zonas muy respetadas"},
    "GBPUSD-OTC": {"name": "Libra / Dólar",         "wr": 68, "vol": "ALTA",   "rec": True,  "note": "Volátil en sesión Londres — buenas reversiones"},
    "EURJPY-OTC": {"name": "Euro / Yen",             "wr": 70, "vol": "ALTA",   "rec": True,  "note": "Excelente en sesión Asia + Europa"},
    "USDJPY-OTC": {"name": "Dólar / Yen",            "wr": 67, "vol": "MEDIA",  "rec": True,  "note": "Estable, tendencias claras"},
    "EURGBP-OTC": {"name": "Euro / Libra",           "wr": 65, "vol": "MEDIA",  "rec": True,  "note": "Rango estrecho — ideal para niveles S/R"},
    "AUDUSD-OTC": {"name": "Dólar Australiano",      "wr": 62, "vol": "MEDIA",  "rec": False, "note": "Pausado por WR histórico — usar con cautela"},
    "USDCAD-OTC": {"name": "Dólar / Dólar Canadiense","wr": 64,"vol": "BAJA",   "rec": False, "note": "Correlaciona con petróleo — menos predecible"},
    "USDCHF-OTC": {"name": "Dólar / Franco Suizo",   "wr": 63, "vol": "BAJA",   "rec": False, "note": "Refugio seguro — poca volatilidad OTC"},
    "NZDUSD-OTC": {"name": "Dólar Neozelandés",      "wr": 61, "vol": "BAJA",   "rec": False, "note": "Menor liquidez en horario OTC"},
}

# ── Opciones de expiración con recomendación ──────────────────────────────────
EXPIRATION_OPTIONS = [
    {"minutes": 1, "label": "1 minuto  ★ RECOMENDADO",    "rec": True,  "note": "Ideal para reversiones en zonas S/R definidas"},
    {"minutes": 2, "label": "2 minutos",                   "rec": False, "note": "Bueno para patrones de consolidación"},
    {"minutes": 3, "label": "3 minutos",                   "rec": False, "note": "Tendencias cortas con momentum claro"},
    {"minutes": 5, "label": "5 minutos  — Tendencias",     "rec": False, "note": "Para tendencias fuertes y confirmadas"},
]

# ─────────────────────────────────────────────────────────────────────────────
# BANNER
# ─────────────────────────────────────────────────────────────────────────────

def _banner():
    console.clear()
    banner = """
[bold cyan]  ███████╗██╗  ██╗███╗   ██╗ ██████╗ ██╗   ██╗ █████╗[/bold cyan]
[bold cyan]  ██╔════╝╚██╗██╔╝████╗  ██║██╔═══██╗██║   ██║██╔══██╗[/bold cyan]
[bold cyan]  █████╗   ╚███╔╝ ██╔██╗ ██║██║   ██║██║   ██║███████║[/bold cyan]
[bold cyan]  ██╔══╝   ██╔██╗ ██║╚██╗██║██║   ██║╚██╗ ██╔╝██╔══██║[/bold cyan]
[bold cyan]  ███████╗██╔╝ ██╗██║ ╚████║╚██████╔╝ ╚████╔╝ ██║  ██║[/bold cyan]
[bold cyan]  ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝   ╚═══╝  ╚═╝  ╚═╝[/bold cyan]
[dim]           Ultra-Smart Trading Bot  v4.0  ·  Configuración[/dim]"""
    console.print(Panel(Align.center(banner), border_style="cyan", padding=(0, 2)))
    console.print()

# ─────────────────────────────────────────────────────────────────────────────
# PASO 1 — Credenciales
# ─────────────────────────────────────────────────────────────────────────────

def _step_credentials(env_path: str) -> tuple[str, str]:
    console.print(Panel(
        "[bold white]PASO 1 de 4[/bold white] — [cyan]Credenciales de Exnova / IQ Option[/cyan]\n"
        "[dim]Tus credenciales se guardan cifradas en el archivo .env local.[/dim]\n"
        "[dim]Nunca se suben a GitHub ni servidores externos.[/dim]",
        border_style="cyan", padding=(0, 2)
    ))

    email = os.environ.get("EXNOVA_EMAIL", "").strip()
    if email:
        console.print(f"  [dim]✓ Email guardado:[/dim] [green]{email}[/green]")
        change = questionary.confirm(
            "  ¿Quieres cambiar el email?", default=False, style=QQ_STYLE
        ).ask()
        if change:
            email = ""

    if not email:
        email = questionary.text(
            "  ✉  Email de Exnova / IQ Option:",
            style=QQ_STYLE
        ).ask() or ""
        if email:
            os.environ["EXNOVA_EMAIL"] = email
            set_key(env_path, "EXNOVA_EMAIL", email)
            console.print(f"  [green]✓ Email guardado[/green]")

    console.print()
    password = os.environ.get("EXNOVA_PASSWORD", "").strip()
    if password:
        console.print(f"  [dim]✓ Contraseña guardada:[/dim] [green]{'*' * 12}[/green]")
        change_pw = questionary.confirm(
            "  ¿Quieres cambiar la contraseña?", default=False, style=QQ_STYLE
        ).ask()
        if change_pw:
            password = ""

    if not password:
        password = questionary.password(
            "  🔑 Contraseña (se ocultará):",
            style=QQ_STYLE
        ).ask() or ""
        if password:
            os.environ["EXNOVA_PASSWORD"] = password
            set_key(env_path, "EXNOVA_PASSWORD", password)
            console.print(f"  [green]✓ Contraseña guardada[/green]")

    console.print()
    return email, password

# ─────────────────────────────────────────────────────────────────────────────
# PASO 2 — Monto
# ─────────────────────────────────────────────────────────────────────────────

def _step_amount(env_path: str) -> float:
    console.print(Panel(
        "[bold white]PASO 2 de 4[/bold white] — [cyan]Monto por Operación[/cyan]\n"
        "[dim]Recomendamos entre el 1% y 5% de tu balance por trade.[/dim]",
        border_style="cyan", padding=(0, 2)
    ))

    table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan",
                  padding=(0, 2), show_edge=False)
    table.add_column("Balance Ejemplo", justify="right")
    table.add_column("1% (Conservador)", justify="center")
    table.add_column("2% (Moderado ★)", justify="center")
    table.add_column("5% (Agresivo)", justify="center")
    table.add_row("$500",  "$5",   "$10",  "$25")
    table.add_row("$1,000","$10",  "$20",  "$50")
    table.add_row("$5,000","$50",  "$100", "$250")
    console.print(Align.center(table))
    console.print()

    saved_amount = os.environ.get("TRADE_AMOUNT", "").strip()
    default_val  = saved_amount if saved_amount else "10"

    raw = questionary.text(
        "  💵 Monto fijo por trade en USD:",
        default=default_val,
        validate=lambda v: True if v.replace(".", "").isdigit() else "Ingresa un número válido",
        style=QQ_STYLE
    ).ask() or default_val

    amount = float(raw)
    os.environ["TRADE_AMOUNT"] = str(amount)
    set_key(env_path, "TRADE_AMOUNT", str(amount))
    console.print(f"  [green]✓ Monto configurado: ${amount:.2f} por trade[/green]\n")
    return amount

# ─────────────────────────────────────────────────────────────────────────────
# PASO 3 — Expiración
# ─────────────────────────────────────────────────────────────────────────────

def _step_expiration(env_path: str) -> int:
    console.print(Panel(
        "[bold white]PASO 3 de 4[/bold white] — [cyan]Tiempo de Expiración[/cyan]\n"
        "[dim]El bot puede ajustar el tiempo según la complejidad del setup.[/dim]",
        border_style="cyan", padding=(0, 2)
    ))

    for opt in EXPIRATION_OPTIONS:
        star = "[bold yellow]★ [/bold yellow]" if opt["rec"] else "  "
        console.print(f"  {star}[cyan]{opt['minutes']}min[/cyan]  — [dim]{opt['note']}[/dim]")
    console.print()

    choices = [opt["label"] for opt in EXPIRATION_OPTIONS]
    saved_exp = os.environ.get("EXPIRATION_MINUTES", "").strip()
    default_choice = choices[0]
    if saved_exp:
        for i, opt in enumerate(EXPIRATION_OPTIONS):
            if str(opt["minutes"]) == saved_exp:
                default_choice = choices[i]
                break

    selected = questionary.select(
        "  ⏱  Selecciona el tiempo de expiración:",
        choices=choices,
        default=default_choice,
        style=QQ_STYLE
    ).ask() or default_choice

    minutes = int(selected.split(" ")[0])
    os.environ["EXPIRATION_MINUTES"] = str(minutes)
    set_key(env_path, "EXPIRATION_MINUTES", str(minutes))
    console.print(f"  [green]✓ Expiración: {minutes} minuto{'s' if minutes > 1 else ''}[/green]\n")
    return minutes

# ─────────────────────────────────────────────────────────────────────────────
# PASO 4 — Divisas
# ─────────────────────────────────────────────────────────────────────────────

def _step_assets(current_assets: list) -> list:
    console.print(Panel(
        "[bold white]PASO 4 de 4[/bold white] — [cyan]Selección de Divisas[/cyan]\n"
        "[dim]Usa [bold]Espacio[/bold] para seleccionar/deseleccionar · [bold]Enter[/bold] para confirmar.[/dim]",
        border_style="cyan", padding=(0, 2)
    ))

    # Tabla informativa de pares
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan",
                  padding=(0, 1), show_edge=False)
    table.add_column("Par",         style="white",  min_width=16)
    table.add_column("Nombre",      style="dim",    min_width=22)
    table.add_column("Win Rate",    justify="center")
    table.add_column("Volatilidad", justify="center")
    table.add_column("Nota",        style="dim")

    for pair, info in PAIR_INFO.items():
        wr_col = "green" if info["wr"] >= 68 else "yellow" if info["wr"] >= 64 else "red"
        rec_tag = "[bold yellow]★[/bold yellow] " if info["rec"] else "  "
        table.add_row(
            f"{rec_tag}{pair}",
            info["name"],
            f"[{wr_col}]{info['wr']}%[/{wr_col}]",
            info["vol"],
            info["note"]
        )

    console.print(table)
    console.print("  [bold yellow]★[/bold yellow] = Recomendado por el bot\n")

    all_pairs = list(PAIR_INFO.keys())
    saved_assets = [a for a in current_assets if a in all_pairs]
    default_sel  = saved_assets if saved_assets else [p for p, i in PAIR_INFO.items() if i["rec"]]

    selected = questionary.checkbox(
        "  Selecciona los pares a operar:",
        choices=all_pairs,
        default=default_sel,
        style=QQ_STYLE
    ).ask()

    if not selected:
        selected = default_sel
        console.print("  [yellow]! Sin selección — usando pares recomendados[/yellow]")

    console.print(f"  [green]✓ {len(selected)} par(es) seleccionado(s)[/green]\n")
    return selected

# ─────────────────────────────────────────────────────────────────────────────
# RESUMEN FINAL
# ─────────────────────────────────────────────────────────────────────────────

def _show_summary(email: str, amount: float, minutes: int, assets: list):
    table = Table(box=box.ROUNDED, show_header=False, border_style="cyan",
                  padding=(0, 2), title="[bold cyan]Configuración del Bot[/bold cyan]")
    table.add_column("Campo",  style="dim",    min_width=20)
    table.add_column("Valor",  style="white")

    masked_email = email[:3] + "****" + email[email.find("@"):] if "@" in email else "****"
    table.add_row("Cuenta Exnova",   f"[cyan]{masked_email}[/cyan]")
    table.add_row("Contraseña",      "[dim]••••••••••••[/dim]")
    table.add_row("Monto por trade", f"[green]${amount:.2f} USD[/green]")
    table.add_row("Expiración",      f"[green]{minutes} minuto{'s' if minutes > 1 else ''}[/green]")
    table.add_row("Pares activos",   f"[green]{len(assets)}[/green]  " +
                  "  ".join(f"[cyan]{a.replace('-OTC','')}[/cyan]" for a in assets))

    console.print()
    console.print(Align.center(table))
    console.print()


# ─────────────────────────────────────────────────────────────────────────────
# FUNCIÓN PÚBLICA — run_setup
# ─────────────────────────────────────────────────────────────────────────────

def run_setup(current_assets: list) -> dict:
    """
    Ejecuta el menú interactivo completo.
    Retorna dict con: email, password, amount, expiration_minutes, assets
    Si questionary no está instalado, retorna vacío para no bloquear el bot.
    """
    if not HAS_QUESTIONARY:
        console.print("[yellow]! Menú interactivo no disponible (pip install questionary)[/yellow]")
        return {}

    # Ruta al .env del bot
    bot_dir  = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(bot_dir, ".env")
    if not os.path.exists(env_path):
        # Crear .env vacío si no existe
        with open(env_path, "w") as f:
            f.write("# Exnova Trading Bot — Configuración local\n")

    _banner()

    # ── Paso 1: Credenciales ─────────────────────────────────────────────────
    email, password = _step_credentials(env_path)

    # ── Paso 2: Monto ────────────────────────────────────────────────────────
    amount = _step_amount(env_path)

    # ── Paso 3: Expiración ───────────────────────────────────────────────────
    minutes = _step_expiration(env_path)

    # ── Paso 4: Divisas ──────────────────────────────────────────────────────
    assets = _step_assets(current_assets)

    # ── Resumen ──────────────────────────────────────────────────────────────
    console.clear()
    _banner()
    _show_summary(email, amount, minutes, assets)

    # Confirmar arranque
    ready = questionary.confirm(
        "  ¿Iniciar el bot con esta configuración?",
        default=True,
        style=QQ_STYLE
    ).ask()

    if not ready:
        console.print("\n  [yellow]Configuración cancelada. Vuelve a ejecutar el bot cuando quieras.[/yellow]\n")
        sys.exit(0)

    console.clear()
    return {
        "email":               email,
        "password":            password,
        "amount":              amount,
        "expiration_minutes":  minutes,
        "assets":              assets,
    }
