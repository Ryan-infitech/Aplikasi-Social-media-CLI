import mysql.connector
import os
import webbrowser
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout
from rich import box
from datetime import datetime
import traceback

console = Console()

def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host="127.0.0.1",
            user="user1",
            password="112233",
            database="socialmediadb"
        )
        return connection
        
    except mysql.connector.Error as err:
        console.print(f"[red]Database connection error: {err}[/red]")
        console.print("[yellow]Debug info:[/yellow]")
        console.print(traceback.format_exc())
        return None

def get_feed_with_comments():
    db = None
    cursor = None
    try:
        db = connect_to_db()
        if not db:
            console.print("[red]Couldn't establish database connection[/red]")
            return []
            
        cursor = db.cursor(dictionary=True, buffered=True)
        
        # Debug: Print connection status
        console.print("[dim]Database connection established[/dim]")
        
        # Get all posts with user information
        post_query = """
            SELECT 
                p.ID_Postingan,
                p.ID_Pengguna,
                p.Caption,
                p.Tanggal_Postingan,
                p.Jam,
                p.`Like`,
                p.Media,
                u.Nama AS Nama_Pengguna
            FROM Postingan p
            JOIN Pengguna u ON p.ID_Pengguna = u.ID_Pengguna
            ORDER BY p.Tanggal_Postingan ASC, p.Jam ASC
        """
        
        # Debug: Print query
        console.print("[dim]Executing post query...[/dim]")
        cursor.execute(post_query)
        
        posts = cursor.fetchall()
        
        # Debug: Print post count
        console.print(f"[dim]Found {len(posts)} posts[/dim]")
        
        # Get comments for each post
        for post in posts:
            comment_query = """
                SELECT  
                    k.ID_Komentar,
                    k.ID_Postingan,
                    k.ID_Pengguna,
                    k.Isi_komentar,
                    k.Tanggal_Komentar,
                    k.Jam,
                    u.Nama AS Nama_Pengguna
                FROM Komentar k
                JOIN Pengguna u ON k.ID_Pengguna = u.ID_Pengguna
                WHERE k.ID_Postingan = %s
                ORDER BY k.Tanggal_Komentar ASC, k.Jam ASC
            """
            cursor.execute(comment_query, (post['ID_Postingan'],))
            post['Komentar'] = cursor.fetchall()
            
        return posts
        
    except mysql.connector.Error as err:
        console.print(f"[red]Database error: {err}[/red]")
        console.print("[yellow]Debug info:[/yellow]")
        console.print(traceback.format_exc())
        return []
        
    except Exception as e:
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
        console.print("[yellow]Debug info:[/yellow]")
        console.print(traceback.format_exc())
        return []
        
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

def format_time(date_str, time_str):
    try:
        if not date_str or not time_str:
            return "Unknown time"
            
        post_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
        now = datetime.now()
        delta = now - post_datetime
        
        if delta.days == 0:
            if delta.seconds < 3600:
                minutes = delta.seconds // 60
                return f"{minutes} menit yang lalu"
            else:
                hours = delta.seconds // 3600
                return f"{hours} jam yang lalu"
        elif delta.days == 1:
            return "Kemarin"
        else:
            return f"{date_str} {time_str}"
    except Exception as e:
        console.print(f"[yellow]Time formatting error: {str(e)}[/yellow]")
        return f"{date_str} {time_str}"

def display_feed_with_comments(posts):
    try:
        if not posts:
            console.print(Panel("Belum ada postingan di beranda.", style="yellow"))
            return

        console.print("\n[bold blue]═══ Beranda ═══[/bold blue]\n")
        
        for post in posts:
            try:
                post_content = Text()
                post_content.append(f"👤 {post.get('Nama_Pengguna', 'Unknown User')}\n", style="bold cyan")
                post_content.append(f"📝 {post.get('Caption', 'No caption')}\n", style="white")
                
                timestamp = format_time(
                    str(post.get('Tanggal_Postingan', '')), 
                    str(post.get('Jam', ''))
                )
                post_content.append(f"🕒 {timestamp}\n", style="dim")
                post_content.append(f"❤️  {post.get('Like', 0)} likes\n", style="red")
                
                if post.get('Media'):
                    post_content.append("📎 Contains media\n", style="blue")
                
                comments = post.get('Komentar', [])
                if comments:
                    post_content.append("\n💬 Komentar:\n", style="yellow")
                    for komentar in comments:
                        comment_time = format_time(
                            str(komentar.get('Tanggal_Komentar', '')),
                            str(komentar.get('Jam', ''))
                        )
                        post_content.append(f"  └─ {komentar.get('Nama_Pengguna', 'Unknown User')}: ", style="green")
                        post_content.append(f"{komentar.get('Isi_komentar', 'No comment content')}", style="white")
                        post_content.append(f" ({comment_time})\n", style="dim")
                else:
                    post_content.append("\n💬 Belum ada komentar\n", style="dim")
                
                console.print(Panel(
                    post_content,
                    title=f"[white]Post #{post.get('ID_Postingan', 'Unknown')}[/white]",
                    border_style="blue",
                    box=box.ROUNDED
                ))
                console.print("")
                
            except Exception as e:
                console.print(f"[red]Error displaying post: {str(e)}[/red]")
                continue
                
    except Exception as e:
        console.print(f"[red]Error displaying feed: {str(e)}[/red]")

def display_menu():
    menu = Table(box=box.ROUNDED)
    menu.add_column("Pilihan", style="cyan")
    menu.add_column("Aksi", style="green")
    
    menu.add_row("1", "Buat postingan")
    menu.add_row("2", "Like postingan")
    menu.add_row("3", "Tambah komentar")
    menu.add_row("4", "Lihat media")
    menu.add_row("5", "Kirim Pesan")
    menu.add_row("6", "Lihat Pesan")
    menu.add_row("7", "Keluar")
    
    console.print(Panel(menu, title="Menu", border_style="blue"))

def send_message(sender_id):
    db = None
    cursor = None
    try:
        recipient_query = """
            SELECT ID_Pengguna, Nama 
            FROM Pengguna 
            WHERE ID_Pengguna != %s
        """
        
        db = connect_to_db()
        if not db:
            return
        
        cursor = db.cursor(dictionary=True)
        cursor.execute(recipient_query, (sender_id,))
        users = cursor.fetchall()
        
        console.print("\n[bold blue]═══ Pilih Penerima Pesan ═══[/bold blue]")
        user_table = Table(box=box.ROUNDED)
        user_table.add_column("No.", style="cyan")
        user_table.add_column("Nama Pengguna", style="green")
        
        for i, user in enumerate(users, 1):
            user_table.add_row(str(i), user['Nama'])
        
        console.print(user_table)
        
        recipient_choice = int(console.input("\n[cyan]Pilih nomor pengguna yang akan dikirim pesan[/cyan]: ")) - 1
        
        if recipient_choice < 0 or recipient_choice >= len(users):
            console.print("[red]× Pilihan tidak valid.[/red]")
            return
        
        recipient_id = users[recipient_choice]['ID_Pengguna']
        message_text = console.input("\n[cyan]Tulis pesan Anda[/cyan]: ")
        
        message_query = """
            INSERT INTO Pesan (Pengirim, Penerima, Isi_pesan, Tanggal_pesan, Jam)
            VALUES (%s, %s, %s, CURDATE(), CURTIME())
        """
        cursor.execute(message_query, (sender_id, recipient_id, message_text))
        db.commit()
        
        console.print("\n[green]✓ Pesan berhasil dikirim![/green]")
        
    except ValueError:
        console.print("\n[red]× Pilihan harus berupa angka.[/red]")
    except Exception as e:
        console.print(f"\n[red]× Gagal mengirim pesan: {str(e)}[/red]")
        if db:
            db.rollback()
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

def view_messages(user_id):
    db = None
    cursor = None
    try:
        db = connect_to_db()
        if not db:
            return
        
        cursor = db.cursor(dictionary=True)
        
        message_query = """
            SELECT 
                p.ID_Pesan,
                CASE 
                    WHEN p.Pengirim = %s THEN 'Anda' 
                    ELSE pengirim.Nama 
                END AS Nama_Pengirim,
                CASE 
                    WHEN p.Pengirim = %s THEN penerima.Nama 
                    ELSE 'Anda' 
                END AS Nama_Penerima,
                p.Isi_pesan,
                p.Tanggal_pesan,
                p.Jam
            FROM Pesan p
            JOIN Pengguna pengirim ON p.Pengirim = pengirim.ID_Pengguna
            JOIN Pengguna penerima ON p.Penerima = penerima.ID_Pengguna
            WHERE p.Pengirim = %s OR p.Penerima = %s
            ORDER BY p.Tanggal_pesan DESC, p.Jam DESC
        """
        
        cursor.execute(message_query, (user_id, user_id, user_id, user_id))
        messages = cursor.fetchall()
        
        console.print("\n[bold blue]═══ Daftar Pesan ═══[/bold blue]")
        
        if not messages:
            console.print(Panel("Tidak ada pesan.", style="yellow"))
            return
        
        for msg in messages:
            timestamp = format_time(
                str(msg.get('Tanggal_pesan', '')), 
                str(msg.get('Jam', ''))
            )
            
            message_content = Text()
            message_content.append(f"👤 {msg['Nama_Pengirim']} → {msg['Nama_Penerima']}\n", style="bold cyan")
            message_content.append(f"📝 {msg['Isi_pesan']}\n", style="white")
            message_content.append(f"🕒 {timestamp}", style="dim")
            
            console.print(Panel(
                message_content,
                border_style="blue",
                box=box.ROUNDED
            ))
            console.print("")
        
    except Exception as e:
        console.print(f"\n[red]× Gagal melihat pesan: {str(e)}[/red]")
        console.print("[yellow]Debug info:[/yellow]")
        console.print(traceback.format_exc())
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

def create_post(id_user):
    db = None
    cursor = None
    try:
        console.print("\n[bold blue]═══ Buat Postingan Baru ═══[/bold blue]")
        caption = console.input("\n📝 [cyan]Tulis caption postingan Anda[/cyan]: ")
        
        media_path = None
        if console.input("\n📎 [cyan]Apakah Anda ingin menambahkan media? (y/n)[/cyan]: ").lower() == 'y':
            media_path = console.input("📂 [cyan]Masukkan path file media[/cyan]: ")

        db = connect_to_db()
        if not db:
            return
            
        cursor = db.cursor()
        
        query = """
            INSERT INTO Postingan (ID_Pengguna, Caption, Tanggal_Postingan, Jam, `Like`, Media)
            VALUES (%s, %s, CURDATE(), CURTIME(), 0, %s)
        """
        cursor.execute(query, (id_user, caption, media_path))
        db.commit()
        
        console.print("\n[green]✓ Postingan berhasil dibuat![/green]")
        
    except Exception as e:
        console.print(f"\n[red]Gagal membuat postingan: {str(e)}[/red]")
        if db:
            db.rollback()
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

def like_post(posts):
    db = None
    cursor = None
    try:
        post_id = int(console.input("\n[cyan]Masukkan #Nomor postingan untuk like[/cyan]: "))
        if not any(p['ID_Postingan'] == post_id for p in posts):
            console.print("[red]× Postingan tidak ditemukan.[/red]")
            return
            
        db = connect_to_db()
        if not db:
            return
            
        cursor = db.cursor()
        
        query = "UPDATE Postingan SET `Like` = `Like` + 1 WHERE ID_Postingan = %s"
        cursor.execute(query, (post_id,))
        db.commit()
        
        console.print(f"\n[green]✓ Berhasil menyukai postingan #{post_id}![/green]")
        
    except ValueError:
        console.print("\n[red]× #Nomor postingan harus berupa angka.[/red]")
    except Exception as e:
        console.print(f"\n[red]× Gagal menyukai postingan: {str(e)}[/red]")
        if db:
            db.rollback()
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

def add_comment(posts, id_user):
    db = None
    cursor = None
    try:
        post_id = int(console.input("\n[cyan]Masukkan #Nomor postingan untuk berkomentar[/cyan]: "))
        if not any(p['ID_Postingan'] == post_id for p in posts):
            console.print("[red]× Postingan tidak ditemukan.[/red]")
            return
            
        komentar = console.input("\n[cyan]Tulis komentar Anda[/cyan]: ")
        
        db = connect_to_db()
        if not db:
            return
            
        cursor = db.cursor()
        
        query = """
            INSERT INTO Komentar (ID_Postingan, ID_Pengguna, Isi_komentar, Tanggal_Komentar, Jam)
            VALUES (%s, %s, %s, CURDATE(), CURTIME())
        """
        cursor.execute(query, (post_id, id_user, komentar))
        db.commit()
        
        console.print("\n[green]✓ Komentar berhasil ditambahkan![/green]")
        
    except ValueError:
        console.print("\n[red]× #Nomor postingan harus berupa angka.[/red]")
    except Exception as e:
        console.print(f"\n[red]× Gagal menambahkan komentar: {str(e)}[/red]")
        if db:
            db.rollback()
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

def view_media(posts):
    try:
        post_id = int(console.input("\n[cyan]Masukkan #Nomor postingan untuk melihat media[/cyan]: "))
        post = next((p for p in posts if p['ID_Postingan'] == post_id), None)
        
        if not post or not post.get('Media'):
            console.print("[red]× Media tidak ditemukan untuk postingan ini.[/red]")
            return
            
        media_path = post['Media']
        if media_path.startswith(("http://", "https://")):
            webbrowser.open(media_path)
            console.print("\n[green]✓ Membuka media di browser...[/green]")
        elif os.path.exists(media_path):
            os.system(f"xdg-open {media_path}")  # Linux
            console.print("\n[green]✓ Membuka media...[/green]")
        else:
            console.print("\n[red]× File media tidak ditemukan.[/red]")
            
    except ValueError:
        console.print("\n[red]× #Nomor postingan harus berupa angka.[/red]")
    except Exception as e:
        console.print(f"\n[red]× Gagal membuka media: {str(e)}[/red]")

def beranda(id_user):
    while True:
        try:
            console.print("[dim]Mengambil data feed...[/dim]")
            feed = get_feed_with_comments()
            console.clear()
            display_feed_with_comments(feed)
            display_menu()
            
            choice = console.input("[bold cyan]Pilih[/bold cyan]: ")

            if choice == "1":
                create_post(id_user)
            elif choice == "2":
                like_post(feed)
            elif choice == "3":
                add_comment(feed, id_user)
            elif choice == "4":
                view_media(feed)
            elif choice == "5":
                send_message(id_user)
            elif choice == "6":
                view_messages(id_user)
            elif choice == "7":
                console.print("[yellow]Keluar dari beranda.[/yellow]")
                break
            else:
                console.print("[red]Pilihan tidak valid.[/red]")
            
            console.input("\n[dim]Tekan Enter untuk melanjutkan...[/dim]")
            
        except Exception as e:
            console.print(f"[red]Terjadi kesalahan: {str(e)}[/red]")
            console.print("[yellow]Debug info:[/yellow]")
            console.print(traceback.format_exc())
            console.input("\n[dim]Tekan Enter untuk melanjutkan...[/dim]")
                    
        except KeyboardInterrupt:
            console.print("\n[yellow]Program dihentikan oleh pengguna.[/yellow]")
            break
            
        except EOFError:
            console.print("\n[yellow]Input dihentikan.[/yellow]")
            break

if __name__ == "__main__":
    try:
        # Untuk pengujian, gunakan ID pengguna default
        test_user_id = 1
        beranda(test_user_id)
    except Exception as e:
        console.print(f"[red]Fatal error: {str(e)}[/red]")
        console.print("[yellow]Debug info:[/yellow]")
        console.print(traceback.format_exc())
    finally:
        console.print("[dim]Program selesai.[/dim]")