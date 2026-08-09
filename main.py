import discord
from discord.ext import commands
from groq import Groq
import datetime
import re
from flask import Flask
import threading

# Tạo Web Server giả lập cho Render
app = Flask('')

@app.route('/')
def home():
    return "Bot Discord AI + AutoMod đang chạy 24/7 ngon lành!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = threading.Thread(target=run_web)
    t.start()

# 1. Dán Groq API Key của bác vào đây (bắt đầu bằng gsk_...)
GROQ_API_KEY = "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"

# 2. Dán Discord Bot Token của bác vào đây
DISCORD_TOKEN = "MTUzNTk5NDI1NjI5NTA3NTk1MQ.Gmz2tS.bcvW-hhi14uvi0ZGOwvXkJdqB1dXkzxleHgAgQ"

# Thời gian Mute phạt (Ví dụ: 5 phút)
MUTE_DURATION_MINUTES = 5 

# DANH SÁCH TỪ CẤM / CHỬI THỀ
BAD_WORDS = [
    r"\bđm\b", r"\bdm\b", r"\bđmá\b", r"\bdma\b", r"\bđmm\b", r"\bdmm\b", 
    r"\bđmme\b", r"\bđmmn\b", r"\bdmcs\b", r"\bđmcs\b", r"\bđcm\b", r"\bdcm\b",
    r"\bdcmm\b", r"\bđcmm\b", r"\bđmkh\b", r"\bdmkh\b", r"\bđmch\b", r"\bđịt\b",
    r"\bdit\b", r"\bđịt mẹ\b", r"\bdit me\b", r"\bđịt má\b", r"\bdit ma\b",
    r"\bvl\b", r"\bvcl\b", r"\bvcc\b", r"\bvcll\b", r"\bcl\b", r"\bclgt\b", 
    r"\bcặc\b", r"\bcac\b", r"\bcc\b", r"\bccc\b", r"\blồn\b", r"\blon\b", 
    r"\blol\b", r"\bbuồi\b", r"\bbuoi\b", r"\bóc chó\b", r"\bchó đẻ\b",
    r"\bcon chó\b", r"\bsúc vật\b", r"\bngu học\b", r"\bđồ ngu\b"
]

groq_client = Groq(api_key=GROQ_API_KEY)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"🤖 AI Bot + AutoMod đã online: {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    content_lower = message.content.lower()

    # 1. Quét chửi thề & Mute
    is_bad_word = False
    for pattern in BAD_WORDS:
        if re.search(pattern, content_lower):
            is_bad_word = True
            break

    if is_bad_word:
        try:
            await message.delete()
            duration = datetime.timedelta(minutes=MUTE_DURATION_MINUTES)
            await message.author.timeout(duration, reason="Chửi thề / Vi phạm quy định")
            await message.channel.send(
                f"🚫 {message.author.mention} đã bị **MUTE {MUTE_DURATION_MINUTES} phút** vì sử dụng từ ngữ không chuẩn mực!"
            )
            return
        except discord.Forbidden:
            await message.channel.send(
                f"⚠️ {message.author.mention} chửi thề nhưng Bot thiếu quyền (Administrator / Moderate Members) để Mute!"
            )
            return
        except Exception as e:
            print(f"⚠️ Lỗi Mute: {e}")

    # 2. Gọi AI trả lời khi tag tên
    if bot.user.mentioned_in(message):
        async with message.channel.typing():
            try:
                user_prompt = message.content.replace(f'<@{bot.user.id}>', '').strip()

                if not user_prompt:
                    await message.channel.send(f"Dạ bác {message.author.mention}, bác cần em giúp gì ạ?")
                    return

                completion = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "Bạn là một trợ lý AI thông minh, thân thiện và nói tiếng Việt xưng hô bác - em."},
                        {"role": "user", "content": user_prompt}
                    ],
                )

                answer = completion.choices[0].message.content

                if len(answer) > 1900:
                    answer = answer[:1900] + "...\n*(Dài quá em cắt bớt nhé bác!)*"

                await message.channel.send(f"{message.author.mention} {answer}")

            except Exception as e:
                print(f"⚠️ Chi tiết lỗi AI: {e}")
                await message.channel.send(f"Bị lỗi rồi bác ơi! Lỗi: `{e}`")

    await bot.process_commands(message)

# Kích hoạt web server chạy song song
keep_alive()

# Chạy Bot Discord
bot.run(DISCORD_TOKEN)
