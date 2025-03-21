import os
import discord
from discord.ext import commands
import asyncio
import ssl
import aiohttp
from dotenv import load_dotenv
from myserver import server_on

# โหลดค่า Token จาก .env
load_dotenv()

MAIN_TOKEN = os.getenv("MAIN_TOKEN")
TOKENS = os.getenv("TOKENS").split(",")
GUILD_IDS = [int(gid) for gid in os.getenv("GUILD_IDS").split(",")]
MAX_PER_TOKEN = int(os.getenv("MAX_PER_TOKEN", 20))
DELAY_PER_USER = int(os.getenv("DELAY_PER_USER", 3))
DELAY_BETWEEN_ROUNDS = int(os.getenv("DELAY_BETWEEN_ROUNDS", 900))

# แก้ไขปัญหา SSL สำหรับ Windows VPS
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

# สร้างบอทหลัก
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ บอทหลักออนไลน์: {bot.user}")

@bot.command()
async def dm_embed(ctx):
    await ctx.send("📨 เริ่มส่งข้อความ DM...")

    all_members = []
    for guild_id in GUILD_IDS:
        guild = bot.get_guild(guild_id)
        if not guild:
            await ctx.send(f"❌ ไม่พบเซิร์ฟเวอร์ ID {guild_id}")
            continue
        for member in guild.members:
            if not member.bot:
                all_members.append(member)

    await ctx.send(f"👥 พบสมาชิกทั้งหมด {len(all_members)} คน")

    embed = discord.Embed(
        title="CZ Shop ร้านค้าขายโปร Free fire 🚀",
        description=(
            "+ เริ่มต้นแค่วันละ 35 บาท เท่านั้น !!\n"
            "+ CZ Panel `มอง ล็อคไหล่ สไนล็อค สไนสับไว`\n"
            "+ CZ Modmenu `มองเส้น ล็อคหัว`\n"
            "+ เติมเงินออโต้ รองรับธนาคาร และวอเล็ท"
        ),
        color=discord.Color.blue()
    ).add_field(
        name="🌐 เว็บไซต์",
        value="[ซื้อ CZ panel คลิกที่นี่](https://czshop.rdcw.xyz/)",
        inline=False
    ).set_image(url="https://i.postimg.cc/9f4tRtF4/Annotation-2025-03-16-005706.png")

    current_index = 0
    round_count = 1

    while current_index < len(all_members):
        await ctx.send(f"🔁 เริ่มรอบที่ {round_count}")

        async def send_dm(token, index):
            intents = discord.Intents.default()
            intents.members = True
            client = discord.Client(intents=intents)

            @client.event
            async def on_ready():
                nonlocal current_index
                print(f"🟢 โทเค่น {index+1} ({client.user}) พร้อม")
                success, failed = 0, 0

                for i in range(MAX_PER_TOKEN):
                    if current_index >= len(all_members):
                        break

                    member = all_members[current_index]
                    current_index += 1
                    try:
                        await member.send(embed=embed)
                        success += 1
                        print(f"✅ ส่งให้ {member.name}")
                    except discord.Forbidden:
                        failed += 1
                        print(f"❌ ปิด DM: {member.name}")
                    except Exception as e:
                        failed += 1
                        print(f"⚠️ Error: {member.name} -> {e}")

                    await asyncio.sleep(DELAY_PER_USER)

                print(f"✅ โทเค่น {index+1} ส่งสำเร็จ {success} คน, ล้มเหลว {failed} คน")
                await client.close()

            try:
                await client.start(token)
            except Exception as e:
                print(f"❌ โทเค่น {index+1} มีปัญหา: {e}")

        tasks = [asyncio.create_task(send_dm(token, i)) for i, token in enumerate(TOKENS)]
        await asyncio.gather(*tasks)

        await ctx.send(f"⏸️ พัก {DELAY_BETWEEN_ROUNDS // 60} นาที ก่อนเริ่มรอบถัดไป...")
        await asyncio.sleep(DELAY_BETWEEN_ROUNDS)
        round_count += 1

    await ctx.send("✅ ส่งข้อความครบทุกคนแล้ว!")
server_on()
bot.run(MAIN_TOKEN)
