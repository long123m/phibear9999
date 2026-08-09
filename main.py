import discord
from discord.ext import commands
from groq import Groq
import datetime
import re

# 1. Dán Groq API Key của bác vào đây (bắt đầu bằng gsk_...)
GROQ_API_KEY = "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"

# 2. Dán Discord Bot Token của bác vào đây
DISCORD_TOKEN = "MTUzNTk5NDI1NjI5NTA3NTk1MQ.GSmxAX.9RGy1G68DgGuQzIUs-YpjoU_myLMqcuRSvuVyI"

# Thời gian Mute phạt (Ví dụ: 5 phút = 300 giây)
MUTE_DURATION_MINUTES = 5 

# ==============================================================================
# DANH SÁCH TỪ CẤM / CHỬI THỀ (Bác có thể tự thêm từ mới vào các ngoặc bên dưới)
# ==============================================================================
BAD_WORDS = [
    # ĐM, ĐMA, ĐMM...
    r"\bđm\b", r"\bdm\b", r"\bđmá\b", r"\bdma\b", r"\bđmm\b", r"\bdmm\b", 
    r"\bđmme\b", r"\bđmmn\b", r"\bdmcs\b", r"\bđmcs\b", r"\bđcm\b", r"\bdcm\b",
    r"\bdcmm\b", r"\bđcmm\b", r"\bđmkh\b", r"\bdmkh\b", r"\bđmch\b", r"\bđịt\b",
    r"\bdit\b", r"\bđịt mẹ\b", r"\bdit me\b", r"\bđịt má\b", r"\bdit ma\b",
    r"\bđịt bà\b", r"\bdit ba\b", r"\bđịt con\b", r"\bdit con\b", r"\bđm tinh\b",

    # VL, VCL, CL...
    r"\bvl\b", r"\bvcl\b", r"\bvcc\b", r"\bvcll\b", r"\bcl\b", r"\bclgt\b", 
    r"\bcđm\b", r"\bvlxx\b", r"\bclm\b", r"\bclme\b", r"\bclmn\b", r"\bvlon\b",

    # BỘ PHẬN SINH DỤC & TỪ THÔ TỤC
    r"\bcặc\b", r"\bcac\b", r"\bcc\b", r"\bccc\b", r"\blồn\b", r"\blon\b", 
    r"\blol\b", r"\blồnn\b", r"\blồn\b", r"\bcặc\b", r"\buồi\b", r"\buoi\b", 
    r"\bbuồi\b", r"\bbuoi\b", r"\bdái\b", r"\bdai\b", r"\bchim\b", r"\bvú\b", 
    r"\bvu\b", r"\bđít\b", r"\bdit\b", r"\bchim cút\b",

    # SÚC VẬT / XÚC PHẠM
    r"\bóc chó\b", r"\boc cho\b", r"\bóc chó\b", r"\bchó đẻ\b", r"\bcho de\b",
    r"\bcon chó\b", r"\bcon cho\b", r"\bđồ chó\b", r"\bdo cho\b", r"\bchó cái\b",
    r"\bđồ lợn\b", r"\bdo lon\b", r"\bsúc vật\b", r"\bsuc vat\b", r"\bquái vật\b",
    r"\bthằng điên\b", r"\bthang dien\b", r"\bcon điên\b", r"\bcon dien\b",
    r"\bngu học\b", r"\bngu hoc\b", r"\bngu vcl\b", r"\bngu vl\b", r"\bngu cặc\b",
    r"\bđồ ngu\b", r"\bdo ngu\b", r"\bthằng ngu\b", r"\bthang ngu\b",

    # XÚC PHẠM GIA ĐÌNH
    r"\bmẹ mày\b", r"\bme may\b", r"\bcha mày\b", r"\bcha may\b", r"\bbố mày\b", 
    r"\bbo may\b", r"\bbà mày\b", r"\bba may\b", r"\bông nội mày\b", r"\bmẹ kiếp\b",
    r"\bme kiep\b", r"\bphò\b", r"\bpho\b", r"\bcon đĩ\b", r"\bcon di\b",
    r"\bđĩ\b", r"\bdi\b", r"\bđĩ thõa\b", r"\blàm đĩ\b", r"\bcave\b",

    # CÁC TỪ LÁCH / VIẾT TẮT KHÁC
    r"\bđoãn\b", r"\bdmm\b", r"\bdcm\b", r"\bdmm\b", r"\bdkm\b", r"\bđkm\b",
    r"\bdmnh\b", r"\bvc\b", r"\bvkl\b", r"\bvãi lồn\b", r"\bvai lon\b",
    r"\bvãi cặc\b", r"\bvai cac\b", r"\bvãi đái\b", r"\bvai dai\b"
]

groq_client = Groq(api_key=GROQ_API_KEY)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"🤖 AI Bot + AutoMod siêu cấp đã online: {bot.user}")

@bot.event
async def on_message(message):
    # Bỏ qua tin nhắn của chính Bot
    if message.author == bot.user:
        return

    content_lower = message.content.lower()

    # -------------------------------------------------------------
    # TÍNH NĂNG 1: TỰ ĐỘNG PHÁT HIỆN CHỬI THỀ & MUTE CẤM CHAT
    # -------------------------------------------------------------
    is_bad_word = False
    for pattern in BAD_WORDS:
        if re.search(pattern, content_lower):
            is_bad_word = True
            break

    if is_bad_word:
        try:
            # Xóa tin nhắn chửi thề
            await message.delete()

            # Mute người dùng (Timeout)
            duration = datetime.timedelta(minutes=MUTE_DURATION_MINUTES)
            await message.author.timeout(duration, reason="Chửi thề / Phát ngôn vi phạm quy định")

            # Cảnh báo trên channel
            await message.channel.send(
                f"🚫 {message.author.mention} đã bị **MUTE {MUTE_DURATION_MINUTES} phút** vì sử dụng từ ngữ không chuẩn mực!"
            )
            return  # Dừng lại không xử lý gọi AI nữa
        except discord.Forbidden:
            await message.channel.send(
                f"⚠️ {message.author.mention} chửi thề nhưng Bot thiếu quyền (Administrator / Moderate Members) để Mute!"
            )
            return
        except Exception as e:
            print(f"⚠️ Lỗi Mute: {e}")

    # -------------------------------------------------------------
    # TÍNH NĂNG 2: GỌI AI TRẢ LỜI KHI ĐƯỢC TAG TÊN
    # -------------------------------------------------------------
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

bot.run(DISCORD_TOKEN)
