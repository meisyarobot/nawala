import os
import requests
import asyncio
from pyrogram import Client, filters

API_ID = "20285194"
API_HASH = "3f7682be5bd1da9636974ca3d6934753"
BOT_TOKEN = "7267929870:AAHC2lojziLjI1ujugqM5iHLaDhSiPFlGkU"

DOMAIN_FILE = "domain.txt"
ADMIN_USER_ID = 1623499141

app = Client("domain_checker_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def check_domain(domain):
    try:
        response = requests.get(f"https://api.internetworkpositif.go.id/check?domain={domain}")
        data = response.json()
        return data.get("status") == "terblokir"
    except Exception as e:
        print(f"Error checking domain {domain}: {e}")
        return False

def read_domains():
    if os.path.exists(DOMAIN_FILE):
        with open(DOMAIN_FILE, "r") as file:
            return [line.strip() for line in file.readlines()]
    return []

async def send_notification(client, domain):
    await client.send_message(ADMIN_USER_ID, f"Domain `{domain}` terblokir!")

async def check_domains_periodically(client):
    while True:
        domains = read_domains()
        for domain in domains:
            if check_domain(domain):
                print(f"Domain {domain} terblokir.")
                await send_notification(client, domain)
            else:
                print(f"Domain {domain} tidak terblokir.")
        await asyncio.sleep(600)  

@app.on_message(filters.command("info"))
async def check_all_domains(client, message):
    domains = read_domains()
    response_text = "Daftar status domain:\n\n"
    for domain in domains:
        is_blocked = check_domain(domain)
        response_text += f"Domain `{domain}` {'*terblokir*' if is_blocked else '*tidak terblokir*'}.\n"
    
    await message.reply(response_text)

@app.on_message(filters.command("add"))
async def add_domain(client, message):
    command_parts = message.text.split()
    if len(command_parts) < 2:
        await message.reply("Gunakan format: /add domain.com")
        return

    domain_to_add = command_parts[1].strip()
    if not domain_to_add:
        await message.reply("Domain tidak valid.")
        return

    with open(DOMAIN_FILE, "a") as file:
        file.write(domain_to_add + "\n")

    await message.reply(f"Domain `{domain_to_add}` berhasil ditambahkan.")

@app.on_message(filters.command("del"))
async def delete_domain(client, message):
    command_parts = message.text.split()
    if len(command_parts) < 2:
        await message.reply("Gunakan format: /del domain.com")
        return

    domain_to_delete = command_parts[1].strip()
    if not domain_to_delete:
        await message.reply("Domain tidak valid.")
        return

    domains = read_domains()
    if domain_to_delete in domains:
        domains.remove(domain_to_delete)
        with open(DOMAIN_FILE, "w") as file:
            file.writelines([domain + "\n" for domain in domains])
        
        await message.reply(f"Domain `{domain_to_delete}` berhasil dihapus.")
    else:
        await message.reply(f"Domain `{domain_to_delete}` tidak ditemukan di daftar.")

@app.on_message(filters.command("cek"))
async def check_single_domain(client, message):
    command_parts = message.text.split()

    if len(command_parts) < 2:
        await message.reply("Gunakan format: /cek domain.com")
        return

    domain_to_check = command_parts[1].strip()

    if not domain_to_check:
        await message.reply("Domain tidak valid.")
        return

    is_blocked = check_domain(domain_to_check)
    result = f"Domain `{domain_to_check}` {'*terblokir*' if is_blocked else '*tidak terblokir*'}."
    await message.reply(result)

async def main():
    await app.start()
    await check_domains_periodically(app)

app.run(main())
