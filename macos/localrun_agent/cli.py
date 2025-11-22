"""
LocalRun Agent CLI
Comandos para gestionar el agente
"""

import os
import sys
import json
import signal
import subprocess
from pathlib import Path
from typing import Optional

import click

from localrun_agent.server import run_server


CONFIG_DIR = Path.home() / ".localrun"
CONFIG_FILE = CONFIG_DIR / "agent.json"
PLIST_PATH = Path.home() / "Library" / "LaunchAgents" / "com.localrun.agent.plist"
LOG_FILE = Path.home() / "Library" / "Logs" / "localrun-agent.log"


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """LocalRun Agent - Servicio local para LocalRun"""
    pass


@cli.command()
@click.option("--port", default=47777, help="Puerto del servidor")
@click.option("--host", default="127.0.0.1", help="Host del servidor")
@click.option("--log-level", default="info", help="Nivel de logs")
def serve(port: int, host: str, log_level: str):
    """Ejecutar servidor (usado por LaunchAgent)"""
    try:
        run_server(port=port, host=host, log_level=log_level)
    except KeyboardInterrupt:
        click.echo("\nServidor detenido")
        sys.exit(0)


@cli.command()
def install():
    """Instalar como servicio (LaunchAgent)"""
    try:
        # Crear directorio de config
        CONFIG_DIR.mkdir(exist_ok=True)

        # Obtener path del ejecutable
        localrun_agent_bin = subprocess.check_output(
            ["which", "localrun-agent"],
            text=True
        ).strip()

        # Crear plist
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.localrun.agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>{localrun_agent_bin}</string>
        <string>serve</string>
        <string>--port</string>
        <string>47777</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>{LOG_FILE}</string>
    <key>StandardErrorPath</key>
    <string>{LOG_FILE}</string>
    <key>WorkingDirectory</key>
    <string>{Path.home()}</string>
</dict>
</plist>
"""

        # Crear directorio LaunchAgents si no existe
        PLIST_PATH.parent.mkdir(parents=True, exist_ok=True)

        # Escribir plist
        with open(PLIST_PATH, "w") as f:
            f.write(plist_content)

        click.echo(f"✅ LaunchAgent instalado en {PLIST_PATH}")
        click.echo("\nPara iniciar el servicio:")
        click.echo("  localrun-agent start")

    except Exception as e:
        click.echo(f"❌ Error instalando servicio: {e}", err=True)
        sys.exit(1)


@cli.command()
def uninstall():
    """Desinstalar servicio"""
    try:
        # Detener servicio primero
        if PLIST_PATH.exists():
            subprocess.run(
                ["launchctl", "unload", str(PLIST_PATH)],
                check=False,
                capture_output=True
            )

        # Eliminar plist
        if PLIST_PATH.exists():
            PLIST_PATH.unlink()
            click.echo(f"✅ LaunchAgent eliminado")

        # Eliminar config
        if CONFIG_FILE.exists():
            CONFIG_FILE.unlink()
            click.echo(f"✅ Configuración eliminada")

        click.echo("\n✨ LocalRun Agent desinstalado correctamente")

    except Exception as e:
        click.echo(f"❌ Error desinstalando: {e}", err=True)
        sys.exit(1)


@cli.command()
def start():
    """Iniciar servicio"""
    try:
        if not PLIST_PATH.exists():
            click.echo("❌ Servicio no instalado. Ejecuta: localrun-agent install")
            sys.exit(1)

        # Cargar LaunchAgent
        result = subprocess.run(
            ["launchctl", "load", str(PLIST_PATH)],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            click.echo("✅ LocalRun Agent iniciado")
            click.echo(f"\nServicio corriendo en http://localhost:47777")
            click.echo("Ver logs: localrun-agent logs")
        else:
            # Puede ya estar cargado
            if "already loaded" in result.stderr.lower():
                click.echo("⚠️  Servicio ya está corriendo")
            else:
                click.echo(f"❌ Error iniciando: {result.stderr}")
                sys.exit(1)

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def stop():
    """Detener servicio"""
    try:
        if not PLIST_PATH.exists():
            click.echo("❌ Servicio no instalado")
            sys.exit(1)

        result = subprocess.run(
            ["launchctl", "unload", str(PLIST_PATH)],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            click.echo("✅ LocalRun Agent detenido")
        else:
            if "not currently loaded" in result.stderr.lower():
                click.echo("⚠️  Servicio ya está detenido")
            else:
                click.echo(f"❌ Error deteniendo: {result.stderr}")
                sys.exit(1)

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def restart():
    """Reiniciar servicio"""
    click.echo("Deteniendo servicio...")
    ctx = click.get_current_context()
    ctx.invoke(stop)
    
    click.echo("\nIniciando servicio...")
    ctx.invoke(start)


@cli.command()
def status():
    """Ver estado del servicio"""
    try:
        # Verificar si está cargado en launchctl
        result = subprocess.run(
            ["launchctl", "list"],
            capture_output=True,
            text=True
        )

        is_running = "com.localrun.agent" in result.stdout

        # Leer config
        config = {}
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE) as f:
                config = json.load(f)

        # Mostrar estado
        click.echo("LocalRun Agent Status")
        click.echo("=" * 40)
        
        if is_running:
            click.echo("Estado:     🟢 Running")
            click.echo(f"Puerto:     {config.get('port', 47777)}")
            click.echo(f"PID:        {config.get('pid', 'N/A')}")
            click.echo(f"Versión:    {config.get('version', 'N/A')}")
            click.echo(f"\nURL:        http://localhost:{config.get('port', 47777)}")
        else:
            click.echo("Estado:     🔴 Stopped")

        click.echo(f"\nConfig:     {CONFIG_FILE}")
        click.echo(f"LaunchAgent: {PLIST_PATH}")
        click.echo(f"Logs:       {LOG_FILE}")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--follow", "-f", is_flag=True, help="Seguir logs en tiempo real")
@click.option("--lines", "-n", default=50, help="Número de líneas a mostrar")
def logs(follow: bool, lines: int):
    """Ver logs del servicio"""
    try:
        if not LOG_FILE.exists():
            click.echo("❌ No hay logs disponibles")
            sys.exit(1)

        if follow:
            # Seguir logs en tiempo real
            subprocess.run(["tail", "-f", str(LOG_FILE)])
        else:
            # Mostrar últimas N líneas
            subprocess.run(["tail", f"-n{lines}", str(LOG_FILE)])

    except KeyboardInterrupt:
        click.echo("\nDetenido")
        sys.exit(0)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
