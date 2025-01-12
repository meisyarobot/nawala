import asyncio
import aiohttp
from pyrogram import Client, filters

API_ID = "20285194" 
API_HASH = "3f7682be5bd1da9636974ca3d6934753"
BOT_TOKEN = "7205568594:AAHnOWzalPnRsscu0Rk160rgB9uvpJ8dgsM"

CACHE_URL = "https://raw.githubusercontent.com/Skiddle-ID/blocklist/main/domains"

domain_cache = []
DOMAINS_FILE = "domains.txt"

app = Client("domain_manager_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


def load_domains():
    """Memuat daftar domain dari file."""
    try:
        with open(DOMAINS_FILE, "r") as file:
            return set(line.strip() for line in file.readlines())
    except FileNotFoundError:
        return set()


def save_domains(domains):
    """Menyimpan daftar domain ke file."""
    with open(DOMAINS_FILE, "w") as file:
        file.write("\n".join(sorted(domains)))


@app.on_message(filters.command("add"))
async def add_domain(client, message):
    command_parts = message.text.split()
    if len(command_parts) < 2:
        await message.reply("Gunakan format: /add domain.com")
        return

    domain_to_add = command_parts[1].strip()
    domains = load_domains()

    if domain_to_add in domains:
        await message.reply(f"Domain `{domain_to_add}` sudah ada dalam daftar.", parse_mode="markdown")
    else:
        domains.add(domain_to_add)
        save_domains(domains)
        await message.reply(f"Domain `{domain_to_add}` berhasil ditambahkan.", parse_mode="markdown")


@app.on_message(filters.command("del"))
async def del_domain(client, message):
    command_parts = message.text.split()
    if len(command_parts) < 2:
        await message.reply("Gunakan format: /del domain.com")
        return

    domain_to_del = command_parts[1].strip()
    domains = load_domains()

    if domain_to_del in domains:
        domains.remove(domain_to_del)
        save_domains(domains)
        await message.reply(f"Domain `{domain_to_del}` berhasil dihapus.", parse_mode="markdown")
    else:
        await message.reply(f"Domain `{domain_to_del}` tidak ditemukan dalam daftar.", parse_mode="markdown")


@app.on_message(filters.command("info"))
async def list_domains(client, message):
    domains = load_domains()

    if not domains:
        await message.reply("Belum ada domain yang ditambahkan.")
    else:
        domain_list = "\n".join([f"- {domain}" for domain in sorted(domains)])
        await message.reply(f"Daftar domain aktif:\n\n{domain_list}")


if __name__ == "__main__":
    app.run()
