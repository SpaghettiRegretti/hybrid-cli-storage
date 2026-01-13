#!/usr/bin/env python3
"""CLI File Storage dengan Hybrid Encryption (Modified Caesar + RSA) - Multi User"""
import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
import sys

# Import modules
from crypto_engine import HybridCryptoEngine
from key_manager import KeyManager
from file_manager import FileManager
from session_manager import SessionManager  # <-- New Module

app = typer.Typer(
    help="🔐 CLI File Storage dengan Hybrid Encryption (Modified Caesar + RSA)",
    add_completion=False
)
console = Console()

# Setup directories
BASE_DIR = Path(__file__).parent / "secure_storage"
STORAGE_DIR = BASE_DIR / "encrypted_files"

# Initialize Global Managers
# Note: KeyManager tidak di-init global lagi karena path-nya dinamis tergantung user
session_manager = SessionManager(BASE_DIR)
file_manager = FileManager(STORAGE_DIR)


# --- Helper Functions ---
def get_key_manager() -> KeyManager:
    """Helper untuk mendapatkan KeyManager milik user yang sedang login"""
    user_key_dir = session_manager.get_user_key_dir()
    return KeyManager(user_key_dir)

def get_crypto_engine() -> HybridCryptoEngine:
    """Get initialized crypto engine dengan kunci user aktif"""
    km = get_key_manager()
    private_key, public_key = km.load_keys()
    
    if not private_key or not public_key:
        current_user = session_manager.get_current_user()
        console.print(f"[red]❌ Keys not found for user: [bold]{current_user}[/bold]![/red]")
        console.print("[yellow]Please run 'init' first to generate keys for this user.[/yellow]")
        raise typer.Exit(1)
    return HybridCryptoEngine(private_key, public_key)


# --- User Management Commands (New) ---

@app.command()
def login(username: str):
    """Switch user / Login dengan profile berbeda"""
    users = session_manager.list_users()
    
    # Auto-register logic (opsional, untuk kemudahan)
    if username not in users:
        console.print(f"[yellow]⚠️  User '{username}' belum ada.[/yellow]")
        console.print(f"Gunakan [bold]register {username}[/bold] untuk membuat baru.")
        raise typer.Exit(1)

    session_manager.login(username)
    console.print(f"\n[green]✅ Login Successful![/green]")
    console.print(f"👤 Active User: [bold cyan]{username}[/bold cyan]")
    console.print(f"🔑 Key Path: {session_manager.get_user_key_dir()}\n")

@app.command()
def register(username: str):
    """Register user baru dan otomatis login"""
    users = session_manager.list_users()
    if username in users:
        console.print(f"[red]❌ User '{username}' sudah terdaftar![/red]")
        return

    session_manager.login(username) # Creates folder automatically
    console.print(f"\n[green]✅ User '{username}' created successfully![/green]")
    console.print("[yellow]🚀 Please run 'init' to generate your RSA keys.[/yellow]\n")

@app.command()
def whoami():
    """Cek user yang sedang aktif"""
    user = session_manager.get_current_user()
    console.print(Panel(
        f"[bold]User:[/bold] {user}\n"
        f"[bold]Keys:[/bold] {session_manager.get_user_key_dir()}",
        title="👤 Current Session",
        border_style="cyan"
    ))

@app.command()
def users():
    """List semua user yang terdaftar"""
    user_list = session_manager.list_users()
    current = session_manager.get_current_user()
    
    table = Table(title="👥 Registered Users")
    table.add_column("Username", style="cyan")
    table.add_column("Status", style="green")

    for u in user_list:
        status = "Active 👈" if u == current else ""
        table.add_row(u, status)
    console.print(table)


# --- Core Commands (Updated for Multi-User) ---

@app.command()
def init():
    """Initialize storage dan generate RSA keys untuk User Aktif"""
    current_user = session_manager.get_current_user()
    km = get_key_manager() # Load key manager dinamis

    console.print(f"\n[bold cyan]🚀 Initializing Secure Storage for: {current_user}[/bold cyan]\n")

    # Create directories
    BASE_DIR.mkdir(parents=True, exist_ok=True)

    # Check if keys already exist
    if km.keys_exist():
        console.print("[yellow]⚠️  Keys already exist for this user![/yellow]")
        overwrite = typer.confirm("Do you want to generate new keys? (This will invalidate files encrypted by this user)")
        if not overwrite:
            console.print("[green]✅ Using existing keys[/green]")
            return

    # Generate keys
    km.generate_key_pair(key_size=2048)

    console.print(f"\n[green]✅ Storage initialized successfully![/green]")
    console.print(f"📁 Storage location: {STORAGE_DIR}")
    console.print(f"🔑 Keys location: {session_manager.get_user_key_dir()}\n")

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
    """Encrypt dan simpan file ke storage (menggunakan kunci User Aktif)"""
    source_path = Path(file_path)
    current_user = session_manager.get_current_user()

    # Validate file
    if not source_path.exists():
        console.print(f"[red]❌ File not found: {file_path}[/red]")
        raise typer.Exit(1)

    if not source_path.is_file():
        console.print(f"[red]❌ Path is not a file: {file_path}[/red]")
        raise typer.Exit(1)

    console.print(f"\n[cyan]🔒 Encrypting file: {source_path.name}[/cyan]")
    console.print(f"[dim]👤 User context: {current_user}[/dim]")

    try:
        # Read file
        file_content = source_path.read_bytes()
        file_size_mb = len(file_content) / (1024 * 1024)
        console.print(f"📄 File size: {file_size_mb:.2f} MB")

        # Get crypto engine (Dynamic based on user)
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
    """Decrypt file dari storage (Hanya berhasil jika User Aktif = Pemilik File)"""
    console.print(f"\n[cyan]🔓 Decrypting file ID: {file_id}[/cyan]")
    console.print(f"[dim]👤 Using keys from user: {session_manager.get_current_user()}[/dim]\n")

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
        # Menangani error integritas atau salah kunci
        console.print(f"[red]❌ Decryption failed: {str(e)}[/red]")
        console.print("[yellow]💡 Hint: Are you logged in as the correct user? Only the user who encrypted the file can decrypt it.[/yellow]")
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
    table = Table(title="\n🔐 Encrypted Files in Storage (Shared)", show_header=True, header_style="bold cyan")
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
    """Generate new RSA key pair for Current User"""
    km = get_key_manager()
    current_user = session_manager.get_current_user()

    console.print(f"\n[bold cyan]🔑 Generate New RSA Key Pair for: {current_user}[/bold cyan]\n")

    if km.keys_exist():
        console.print("[red]⚠️  WARNING: Keys already exist![/red]")
        console.print("[red]Generating new keys will make all encrypted files unrecoverable![/red]\n")

        confirm = typer.confirm("Do you want to continue?")
        if not confirm:
            console.print("[cyan]Operation cancelled[/cyan]")
            return

    # Generate keys
    km.generate_key_pair(key_size=2048)

    console.print("\n[green]✅ New key pair generated successfully![/green]\n")


@app.command()
def info():
    """Show system information & Current User"""
    console.print("\n[bold cyan]ℹ️  System Information[/bold cyan]\n")

    # Current User Info
    current_user = session_manager.get_current_user()
    km = get_key_manager()
    key_info = km.get_key_info()

    user_status = "[green]Loaded[/green]" if key_info else "[red]Missing Keys (Run init)[/red]"

    console.print(f"[bold]👤 User Context:[/bold] {current_user}")
    
    if key_info:
        console.print("[bold]🔑 RSA Keys:[/bold]")
        console.print(f"   Key size: {key_info['key_size']} bits")
        console.print(f"   Private key: {key_info['private_key_path']}")
        console.print(f"   Public key: {key_info['public_key_path']}")
    else:
        console.print(f"[yellow]🔑 No keys found for user '{current_user}'[/yellow]")

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