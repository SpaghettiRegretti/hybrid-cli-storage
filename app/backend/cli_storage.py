#!/usr/bin/env python3
"""CLI File Storage dengan Hybrid Encryption (Modified Caesar + RSA)"""
import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
import sys

from crypto_engine import HybridCryptoEngine
from key_manager import KeyManager
from file_manager import FileManager

app = typer.Typer(
    help="🔐 CLI File Storage dengan Hybrid Encryption (Modified Caesar + RSA)",
    add_completion=False
)
console = Console()

# Setup directories
BASE_DIR = Path(__file__).parent / "secure_storage"
KEYS_DIR = BASE_DIR / "keys"
STORAGE_DIR = BASE_DIR / "encrypted_files"

# Initialize managers
key_manager = KeyManager(KEYS_DIR)
file_manager = FileManager(STORAGE_DIR)


def get_crypto_engine() -> HybridCryptoEngine:
    """Get initialized crypto engine with keys"""
    private_key, public_key = key_manager.load_keys()
    if not private_key or not public_key:
        console.print("[red]❌ Keys not found! Please run 'init' first.[/red]")
        raise typer.Exit(1)
    return HybridCryptoEngine(private_key, public_key)


@app.command()
def init():
    """Initialize storage dan generate RSA keys"""
    console.print("\n[bold cyan]🚀 Initializing Secure Storage System[/bold cyan]\n")

    # Create directories
    BASE_DIR.mkdir(parents=True, exist_ok=True)

    # Check if keys already exist
    if key_manager.keys_exist():
        console.print("[yellow]⚠️  Keys already exist![/yellow]")
        overwrite = typer.confirm("Do you want to generate new keys? (This will invalidate all encrypted files)")
        if not overwrite:
            console.print("[green]✅ Using existing keys[/green]")
            return

    # Generate keys
    key_manager.generate_key_pair(key_size=2048)

    console.print(f"\n[green]✅ Storage initialized successfully![/green]")
    console.print(f"📁 Storage location: {STORAGE_DIR}")
    console.print(f"🔑 Keys location: {KEYS_DIR}\n")

    info_panel = Panel(
        "[bold]Encryption Method:[/bold]\n"
        "• Layer 1: Modified Caesar Cipher (dynamic shift per byte)\n"
        "• Layer 2: RSA-2048 (metadata protection)\n\n"
        "[bold cyan]Use 'help' command to see available operations[/bold cyan]",
        title="🔐 Hybrid Encryption",
        border_style="cyan"
    )
    console.print(info_panel)


@app.command()
def encrypt(file_path: str):
    """Encrypt dan simpan file ke storage"""
    source_path = Path(file_path)

    # Validate file
    if not source_path.exists():
        console.print(f"[red]❌ File not found: {file_path}[/red]")
        raise typer.Exit(1)

    if not source_path.is_file():
        console.print(f"[red]❌ Path is not a file: {file_path}[/red]")
        raise typer.Exit(1)

    console.print(f"\n[cyan]🔒 Encrypting file: {source_path.name}[/cyan]")

    try:
        # Read file
        file_content = source_path.read_bytes()
        file_size_mb = len(file_content) / (1024 * 1024)
        console.print(f"📄 File size: {file_size_mb:.2f} MB")

        # Get crypto engine
        crypto_engine = get_crypto_engine()

        # Encrypt
        console.print("🔐 Applying Modified Caesar Cipher (Layer 1)...")
        console.print("🔐 Encrypting metadata with RSA (Layer 2)...")
        encrypted_content, metadata = crypto_engine.encrypt_file(file_content, source_path.name)

        # Save to storage
        file_id = file_manager.save_encrypted_file(encrypted_content, metadata, source_path.name)

        console.print(f"\n[bold green]✅ File encrypted successfully![/bold green]")
        console.print(f"📝 File ID: [bold]{file_id}[/bold]")
        console.print(f"💾 Saved to storage\n")

        console.print("[yellow]⚠️  Keep this File ID to decrypt later![/yellow]\n")

    except Exception as e:
        console.print(f"[red]❌ Encryption failed: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def decrypt(file_id: str, output_path: str):
    """Decrypt file dari storage"""
    console.print(f"\n[cyan]🔓 Decrypting file ID: {file_id}[/cyan]\n")

    try:
        # Load encrypted file
        encrypted_content, metadata = file_manager.load_encrypted_file(file_id)

        # Get crypto engine
        crypto_engine = get_crypto_engine()

        # Decrypt
        console.print("🔓 Decrypting metadata with RSA (Layer 2)...")
        console.print("🔓 Decrypting content with Modified Caesar (Layer 1)...")
        decrypted_content, original_filename = crypto_engine.decrypt_file(encrypted_content, metadata)

        # Save decrypted file
        output_file = Path(output_path)
        output_file.write_bytes(decrypted_content)

        file_size_mb = len(decrypted_content) / (1024 * 1024)

        console.print(f"\n[bold green]✅ File decrypted successfully![/bold green]")
        console.print(f"📄 Original filename: {original_filename}")
        console.print(f"💾 Saved to: {output_file}")
        console.print(f"📊 File size: {file_size_mb:.2f} MB\n")

    except ValueError as e:
        console.print(f"[red]❌ Decryption failed: {str(e)}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]❌ Error: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def list():
    """List semua file terenkripsi di storage"""
    files = file_manager.list_files()

    if not files:
        console.print("\n[yellow]📭 No encrypted files in storage[/yellow]\n")
        return

    # Create table
    table = Table(title="\n🔐 Encrypted Files in Storage", show_header=True, header_style="bold cyan")
    table.add_column("File ID", style="yellow", width=10)
    table.add_column("Original Filename", style="green")
    table.add_column("Size", style="cyan", justify="right")
    table.add_column("Timestamp", style="magenta")

    for file_info in files:
        size_kb = file_info['size'] / 1024
        size_str = f"{size_kb:.2f} KB" if size_kb < 1024 else f"{size_kb / 1024:.2f} MB"
        timestamp = file_info['timestamp'][:19].replace('T', ' ')

        table.add_row(
            file_info['file_id'],
            file_info['original_filename'],
            size_str,
            timestamp
        )

    console.print(table)

    # Show stats
    stats = file_manager.get_storage_stats()
    console.print(f"\n[bold]Total files:[/bold] {stats['total_files']}")
    console.print(f"[bold]Total size:[/bold] {stats['total_size_mb']} MB\n")


@app.command()
def delete(file_id: str):
    """Delete encrypted file dari storage"""
    # Get file info first
    file_info = file_manager.get_file_info(file_id)

    if not file_info:
        console.print(f"[red]❌ File ID '{file_id}' not found[/red]")
        raise typer.Exit(1)

    # Confirm deletion
    console.print(f"\n[yellow]⚠️  You are about to delete:[/yellow]")
    console.print(f"   File ID: {file_id}")
    console.print(f"   Filename: {file_info['original_filename']}\n")

    confirm = typer.confirm("Are you sure you want to delete this file?")

    if not confirm:
        console.print("[cyan]Deletion cancelled[/cyan]")
        return

    # Delete
    success = file_manager.delete_file(file_id)

    if success:
        console.print(f"\n[green]✅ File deleted successfully[/green]\n")
    else:
        console.print(f"\n[red]❌ Failed to delete file[/red]\n")
        raise typer.Exit(1)


@app.command()
def keygen():
    """Generate new RSA key pair"""
    console.print("\n[bold cyan]🔑 Generate New RSA Key Pair[/bold cyan]\n")

    if key_manager.keys_exist():
        console.print("[red]⚠️  WARNING: Keys already exist![/red]")
        console.print("[red]Generating new keys will make all encrypted files unrecoverable![/red]\n")

        confirm = typer.confirm("Do you want to continue?")
        if not confirm:
            console.print("[cyan]Operation cancelled[/cyan]")
            return

    # Generate keys
    key_manager.generate_key_pair(key_size=2048)

    console.print("\n[green]✅ New key pair generated successfully![/green]\n")


@app.command()
def info():
    """Show system information"""
    console.print("\n[bold cyan]ℹ️  System Information[/bold cyan]\n")

    # Key info
    key_info = key_manager.get_key_info()
    if key_info:
        console.print("[bold]🔑 RSA Keys:[/bold]")
        console.print(f"   Key size: {key_info['key_size']} bits")
        console.print(f"   Private key: {key_info['private_key_path']}")
        console.print(f"   Public key: {key_info['public_key_path']}")
    else:
        console.print("[yellow]🔑 No keys found (run 'init' first)[/yellow]")

    console.print()

    # Storage info
    stats = file_manager.get_storage_stats()
    console.print("[bold]📦 Storage:[/bold]")
    console.print(f"   Location: {STORAGE_DIR}")
    console.print(f"   Total files: {stats['total_files']}")
    console.print(f"   Total size: {stats['total_size_mb']} MB")

    console.print()

    # Encryption info
    info_panel = Panel(
        "[bold]Layer 1: Modified Caesar Cipher[/bold]\n"
        "• Dynamic shift per byte based on position\n"
        "• Salt-based randomization\n"
        "• Fast encryption for large files\n\n"
        "[bold]Layer 2: RSA Encryption[/bold]\n"
        "• 2048-bit key size\n"
        "• Protects Caesar parameters and metadata\n"
        "• Ensures key confidentiality",
        title="🔐 Encryption Method",
        border_style="green"
    )
    console.print(info_panel)
    console.print()


if __name__ == "__main__":
    app(prog_name="hybrid-cli-storage")
