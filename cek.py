import os
import requests
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram import Client, filters
from pyrogram.types import Message


API_ID = "20285194"
API_HASH = "3f7682be5bd1da9636974ca3d6934753"
BOT_TOKEN = "7267929870:AAHC2lojziLjI1ujugqM5iHLaDhSiPFlGkU"

DOWNLOAD_URL = 'https://trustpositif.kominfo.go.id/assets/db/domains'

DOWNLOAD_DIR = "domains_data"
LIST_DOMAIN_FILE = "listdomain.txt"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

domain_list = set()

app = Client("trustpositif_bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

downloaded_file = os.path.join(DOWNLOAD_DIR, "domains.txt")

def download_domains():
    try:
        response = requests.get(DOWNLOAD_URL)
        response.raise_for_status()
        with open(downloaded_file, "wb") as file:
            file.write(response.content)
        print("File domains berhasil diunduh.")
    except requests.RequestException as e:
        print(f"Gagal mengunduh file: {e}")

def check_domain(domain):
    try:
        with open(downloaded_file, "r") as file:
            domains = file.readlines()
        domains = [d.strip() for d in domains]
        if domain in domains:
            return "TERBLOKIR"
        else:
            return "TIDAK TERBLOKIR"
    except FileNotFoundError:
        return "Data domain belum diunduh."

def ensure_domains_file_exists():
    if not os.path.exists(downloaded_file):
        print("File domains.txt tidak ditemukan. Mengunduh ulang...")
        download_domains()

@app.on_message(filters.command("add"))
async def add_domain(client, message: Message):
    command_parts = message.text.split()
    if len(command_parts) < 2:
        await message.reply("Gunakan format: /add domain.com")
        return
    domain_to_add = command_parts[1].strip()
    try:
        with open(LIST_DOMAIN_FILE, "a") as file:
            file.write(domain_to_add + "\n")
        await message.reply(f"Domain `{domain_to_add}` berhasil ditambahkan ke list.")
    except Exception as e:
        await message.reply(f"Gagal menambah domain: {e}")

@app.on_message(filters.command("del"))
async def del_domain(client, message: Message):
    command_parts = message.text.split()
    if len(command_parts) < 2:
        await message.reply("Gunakan format: /del domain.com")
        return
    domain_to_remove = command_parts[1].strip()
    try:
        with open(LIST_DOMAIN_FILE, "r") as file:
            lines = file.readlines()
        with open(LIST_DOMAIN_FILE, "w") as file:
            for line in lines:
                if line.strip() != domain_to_remove:
                    file.write(line)
        await message.reply(f"Domain `{domain_to_remove}` berhasil dihapus dari list.")
    except Exception as e:
        await message.reply(f"Gagal menghapus domain: {e}")

@app.on_message(filters.command("list"))
async def list_domains(client, message: Message):
    try:
        with open(LIST_DOMAIN_FILE, "r") as file:
            domains = file.readlines()
        domains = [d.strip() for d in domains]
        if domains:
            response_text = "Daftar domain:\n\n"
            for domain in domains:
                response_text += f"- `{domain}`\n"
            await message.reply(response_text)
        else:
            await message.reply("Tidak ada domain yang ditemukan.")
    except FileNotFoundError:
        await message.reply("File `listdomain.txt` tidak ditemukan.")

@app.on_message(filters.command("info"))
async def info_domains(client, message: Message):
    try:
        with open(LIST_DOMAIN_FILE, "r") as file:
            list_domains = file.readlines()
        list_domains = [d.strip() for d in list_domains]
        with open(downloaded_file, "r") as file:
            downloaded_domains = file.readlines()
        downloaded_domains = [d.strip() for d in downloaded_domains]
        
        blocked_domains = []
        not_blocked_domains = []
        for domain in list_domains:
            if domain in downloaded_domains:
                blocked_domains.append(domain)
            else:
                not_blocked_domains.append(domain)
        
        response_text = "Hasil pengecekan:\n\n"
        if blocked_domains:
            response_text += "TERBLOKIR:\n" + "\n".join([f"- `{domain}`" for domain in blocked_domains]) + "\n\n"
        if not_blocked_domains:
            response_text += "TIDAK TERBLOKIR:\n" + "\n".join([f"- `{domain}`" for domain in not_blocked_domains]) + "\n"
        
        await message.reply(response_text)
    except FileNotFoundError:
        await message.reply("File `listdomain.txt` atau data domain yang terunduh belum tersedia.")

def delete_domains_file():
    try:
        if os.path.exists(downloaded_file):
            os.remove(downloaded_file)
            print("File domains telah dihapus.")
    except Exception as e:
        print(f"Terjadi kesalahan saat menghapus file: {e}")

scheduler = AsyncIOScheduler()
scheduler.add_job(download_domains, "interval", minutes=10)
scheduler.add_job(delete_domains_file, "interval", minutes=10)

ensure_domains_file_exists()

scheduler.start()

app.run()
