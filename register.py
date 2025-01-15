import mysql.connector
from getpass import getpass
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.layout import Layout
from rich import box
import bcrypt


# Buat instance Console untuk tampilan lebih baik
console = Console()


# Konfigurasi koneksi database
db_config = {
    "host": "127.0.0.1",
    "user": "user1",
    "password": "112233",
    "database": "socialmediadb"
}


def create_welcome_layout():
    """Buat layout selamat datang"""
    layout = Layout()
    layout.split_column(
        Layout(Panel(
            "[bold blue][size=54]Selamat Datang di Aplikasi Social Media[/size][/bold blue]\n\n" 
            "[dim][size=54]      Silakan Register dahulu[/size][/dim]", 
            title="[green]Welcome[/green]", 
            border_style="blue", 
            box=box.ROUNDED,
            padding=(10, 40),
        ), name="centered")
    )
    return layout

def register():
    try:
        # Membuka koneksi ke database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()


        # Layout welcome
        console.print(create_welcome_layout())


        console.print("\n[bold blue]===[ REGISTRASI PENGGUNA ]===[/bold blue]", justify="center")
        

        nama = Prompt.ask("[cyan]Nama Lengkap[/cyan]")
        email = Prompt.ask("[cyan]Email[/cyan]")


        # Periksa apakah email sudah terdaftar
        cursor.execute("SELECT * FROM Pengguna WHERE Email = %s", (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            console.print("\n[bold red]❌ Email sudah terdaftar. Silakan gunakan email lain.[/bold red]")
            return


        password = console.input("[cyan]Password: [/cyan]")
        confirm_password = console.input("[cyan]Konfirmasi Password: [/cyan]")


        if password != confirm_password:
            console.print("\n[bold red]❌ Password tidak cocok. Silakan coba lagi.[/bold red]")
            return


        # Hash password menggunakan bcrypt
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


        # Menyimpan data pengguna ke dalam database
        query = """
        INSERT INTO Pengguna (Nama, Email, Password, Tanggal_Daftar) 
        VALUES (%s, %s, %s, CURDATE())
        """
        cursor.execute(query, (nama, email, hashed_password))
        conn.commit()


        console.print(Panel(
            f"[bold green]✅ Selamat {nama}, akun Anda telah berhasil terdaftar :) Silahkan login[/bold green]",
            border_style="green",
            box=box.ROUNDED
        ))

    except mysql.connector.Error as err:
        console.print(f"\n[bold red]❌ Error: {err}[/bold red]")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def show_homepage(user_id):
    console.print(Panel(
        f"[bold green]Selamat datang di beranda, pengguna {user_id}![/bold green]",
        border_style="green",
        box=box.ROUNDED
    ))

if __name__ == "__main__":

    register()