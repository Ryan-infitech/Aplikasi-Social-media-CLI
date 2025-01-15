import mysql.connector
from getpass import getpass
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.layout import Layout
from rich import box
import bcrypt
from beranda import beranda

console = Console()

db_config = {
    "host": "127.0.0.1",
    "user": "user1",
    "password": "112233",
    "database": "socialmediadb"
}


def connect_to_db():
    return mysql.connector.connect(**db_config)

def create_login_layout():
    """Buat layout login"""
    layout = Layout()
    layout.split_column(
        Layout(Panel(
            "[bold blue][size=24]Login Social Media[/size][/bold blue]\n" 
            "[dim][size=18]Masukkan Akun Anda[/size][/dim]", 
            title="[green]Welcome[/green]", 
            border_style="blue", 
            box=box.ROUNDED,
            padding=(10, 50),  # Memberikan ruang vertikal (2) dan horizontal (4)
        ), name="centered")
    )
    return layout

def login():
    try:
        # Layout login
        layout = create_login_layout()
        console.print(layout)

        # Input email dan password
        email = Prompt.ask("[cyan]Email[/cyan]")
        password = console.input("[cyan]Password: [/cyan]")

        # Validasi input
        if not email or not password:
            console.print(Panel(
                "[bold red]❌ Email dan password tidak boleh kosong.[/bold red]",
                border_style="red",
                box=box.ROUNDED
            ))
            return

        # Membuka koneksi ke database
        conn = connect_to_db()
        cursor = conn.cursor(dictionary=True)

        # Query untuk memeriksa email
        query = "SELECT * FROM Pengguna WHERE Email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()

        if user and bcrypt.checkpw(password.encode('utf-8'), user['Password'].encode('utf-8')):
            console.print(Panel(
                f"[bold green]✅ Selamat datang, {user['Nama']}! Anda berhasil login.[/bold green]",
                border_style="green",
                box=box.ROUNDED
            ))
            beranda(user['ID_Pengguna'])
        else:
            console.print(Panel(
                "[bold red]❌ Email atau password salah.[/bold red]",
                border_style="red",
                box=box.ROUNDED
            ))
    except mysql.connector.Error as err:
        console.print(Panel(
            f"[bold red]❌ Error: {err}[/bold red]",
            border_style="red",
            box=box.ROUNDED
        ))
    finally:
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    login()