import aiohttp
import os
from pyrogram import Client, filters

API_ID = "20285194" 
API_HASH = "3f7682be5bd1da9636974ca3d6934753"
BOT_TOKEN = "7205568594:AAHnOWzalPnRsscu0Rk160rgB9uvpJ8dgsM"

DOMAINS_URL = "https://raw.githubusercontent.com/Skiddle-ID/blocklist/main/domains"
DOMAIN_FILE = "domains.txt"
domain_cache = []

app = Client("domain_manager_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


def load_domains_from_file():
    """Memuat daftar domain dari file lokal."""
    if os.path.exists(DOMAIN_FILE):
        with open(DOMAIN_FILE, "r") as file:
            return [line.strip() for line in file.readlines()]
    return []


def save_domains_to_file():
    """Menyimpan daftar domain ke file lokal."""
    with open(DOMAIN_FILE, "w") as file:
        file.write("\n".join(domain_cache))


@app.on_message(filters.command("add"))
async def add_domain(client, message):
    """Menambahkan domain ke daftar cache."""
    global domain_cache
    command_parts = message.text.split()

    if len(command_parts) < 2:
        await message.reply("Gunakan format: /add domain.com")
        return

    domain_to_add = command_parts[1].strip()

    if domain_to_add in domain_cache:
        await message.reply(f"Domain `{domain_to_add}` sudah ada dalam daftar.")
    else:
        domain_cache.append(domain_to_add)
        save_domains_to_file()
        await message.reply(f"Domain `{domain_to_add}` berhasil ditambahkan!")


@app.on_message(filters.command("del"))
async def delete_domain(client, message):
    """Menghapus domain dari daftar cache."""
    global domain_cache
    command_parts = message.text.split()

    if len(command_parts) < 2:
        await message.reply("Gunakan format: /del domain.com")
        return

    domain_to_delete = command_parts[1].strip()

    if domain_to_delete in domain_cache:
        domain_cache.remove(domain_to_delete)
        save_domains_to_file()
        await message.reply(f"Domain `{domain_to_delete}` berhasil dihapus!")
    else:
        await message.reply(f"Domain `{domain_to_delete}` tidak ditemukan dalam daftar.")


@app.on_message(filters.command("list"))
async def list_domains(client, message):
    """Menampilkan daftar semua domain dalam cache."""
    global domain_cache

    if not domain_cache:
        await message.reply("Daftar domain kosong.")
        return

    response_text = "Daftar domain dalam cache:\n\n"
    for domain in domain_cache:
        response_text += f"- `{domain}`\n"

    await message.reply(response_text)


@app.on_message(filters.command("info"))
async def check_all_domains(client, message):
    """Memeriksa status semua domain dalam cache."""
    global domain_cache

    response_text = "Daftar status domain:\n\n"
    for domain in domain_cache:
        is_blocked = domain in domain_cache
        response_text += f"Domain `{domain}` {'*terblokir*' if is_blocked else '*tidak terblokir*'}.\n"

    await message.reply(response_text)


@app.on_message(filters.command("refresh"))
async def refresh_cache(client, message):
    """Memperbarui cache daftar domain."""
    global domain_cache
    try:
        domain_cache = await fetch_domain_list()
        save_domains_to_file()
        await message.reply("Cache daftar domain berhasil diperbarui!")
    except Exception as e:
        await message.reply(f"Gagal memperbarui cache: {e}")


@app.on_message(filters.command("cek"))
async def check_domain(client, message):
    """Memeriksa apakah domain terblokir."""
    global domain_cache
    command_parts = message.text.split()

    if len(command_parts) < 2:
        await message.reply("Gunakan format: /cek domain.com")
        return

    domain_to_check = command_parts[1].strip()

    is_blocked = domain_to_check in domain_cache
    result = f"Domain `{domain_to_check}` {'*terblokir*' if is_blocked else '*tidak terblokir*'}."
    await message.reply(result)


async def fetch_domain_list():
    """Mengambil daftar domain dari URL."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(DOMAINS_URL) as response:
                if response.status == 200:
                    text = await response.text()
                    return text.splitlines()
                else:
                    raise Exception(f"HTTP {response.status}: {response.reason}")
    except Exception as e:
        raise Exception(f"Error fetching domain list: {e}")


if __name__ == "__main__":
    domain_cache = load_domains_from_file()
    app.run()
