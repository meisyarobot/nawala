import asyncio
import aiohttp
from pyrogram import Client, filters

API_ID = "20285194"
API_HASH = "3f7682be5bd1da9636974ca3d6934753"
BOT_TOKEN = "7267929870:AAHC2lojziLjI1ujugqM5iHLaDhSiPFlGkU"

CACHE_URL = "https://raw.githubusercontent.com/Skiddle-ID/blocklist/main/domains"

app = Client("domain_checker_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
domain_cache = []


async def fetch_domain_list():
    async with aiohttp.ClientSession() as session:
        async with session.get(CACHE_URL) as response:
            if response.status == 200:
                text = await response.text()
                return text.split("\n")
            else:
                raise Exception(f"Gagal mengambil daftar domain: {response.status}")


TRUSTPOSITIF_URL = "https://trustpositif.kominfo.go.id/"


async def check_domain_in_trustpositif(domain: str):
    """Memeriksa apakah domain terblokir melalui TrustPositif Kominfo."""
    async with aiohttp.ClientSession() as session:
        params = {'q': domain}  # Query parameter untuk pencarian domain
        async with session.get(TRUSTPOSITIF_URL, params=params) as response:
            if response.status == 200:
                # Parsing HTML untuk mendapatkan status domain
                soup = BeautifulSoup(await response.text(), 'html.parser')
                # Menyesuaikan selector untuk menemukan status domain
                result_text = soup.find("div", {"class": "alert-info"})
                if result_text:
                    return "Terblokir" in result_text.text
                else:
                    return False  # Tidak ditemukan, anggap tidak terblokir
            else:
                raise Exception(f"HTTP {response.status}: {response.reason}")


@app.on_message(filters.command("cek"))
async def check_domain(client, message):
    """Memeriksa apakah domain terblokir melalui TrustPositif Kominfo."""
    command_parts = message.text.split()

    if len(command_parts) < 2:
        await message.reply("Gunakan format: /cek domain.com")
        return

    domain_to_check = command_parts[1].strip()

    try:
        is_blocked = await check_domain_in_trustpositif(domain_to_check)
        result = f"Domain `{domain_to_check}` {'*terblokir*' if is_blocked else '*tidak terblokir*'}."
        await message.reply(result, parse_mode="markdown")
    except Exception as e:
        await message.reply(f"Gagal memeriksa domain: {e}")

@app.on_message(filters.command("refresh"))
async def refresh_cache(client, message):
    global domain_cache
    try:
        domain_cache = await fetch_domain_list()
        await message.reply("Cache daftar domain berhasil diperbarui!")
    except Exception as e:
        return await message.reply(f"Gagal memperbarui cache: {e}")


if __name__ == "__main__":
    app.run()
