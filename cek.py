import asyncio
import aiohttp
from pyrogram import Client, filters

API_ID = "20285194" 
API_HASH = "3f7682be5bd1da9636974ca3d6934753"
BOT_TOKEN = "7205568594:AAHnOWzalPnRsscu0Rk160rgB9uvpJ8dgsM"

CACHE_URL = "https://raw.githubusercontent.com/Skiddle-ID/blocklist/main/domains"

app = Client("domain_checker_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
domain_cache = []


async def fetch_domain_list():
    """Mengambil daftar domain dari URL."""
    async with aiohttp.ClientSession() as session:
        async with session.get(CACHE_URL) as response:
            if response.status == 200:
                text = await response.text()
                return text.split("\n")
            else:
                raise Exception(f"Gagal mengambil daftar domain: {response.status}")


@app.on_message(filters.command("cek"))
async def check_domain(client, message):
    global domain_cache
    command_parts = message.text.split()
    
    if len(command_parts) < 2:
        await message.reply("Gunakan format: /cek domain.com")
        return

    domain_to_check = command_parts[1].strip()

    # Cek cache, jika kosong, ambil dari URL
    if not domain_cache:
        domain_cache = await fetch_domain_list()

    is_blocked = domain_to_check in domain_cache
    result = f"Domain `{domain_to_check}` {'*terblokir*' if is_blocked else '*tidak terblokir*'}."
    await message.reply(result, parse_mode="markdown")


@app.on_message(filters.command("refresh"))
async def refresh_cache(client, message):
    global domain_cache
    try:
        domain_cache = await fetch_domain_list()
        await message.reply("Cache daftar domain berhasil diperbarui!")
    except Exception as e:
        await message.reply(f"Gagal memperbarui cache: {e}")


if __name__ == "__main__":
    app.run()
