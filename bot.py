import telebot
from telebot import types
import math

BOT_TOKEN = '7519954055:AAHpU9k09rIJJkx2zDK1MsZXhAFBjfH2iQA'
ADMIN_ID = 6525504920
bot = telebot.TeleBot(BOT_TOKEN)

dollar_kursi = 12600

narxlar = {
    "odnatonniy": {
        "garpun": {"≤3.6": 1.8, ">3.6": 2.5},
        "nogarpun": {"≤3.6": 1.3, ">3.6": 2.0}
    },
    "pechat": {
        "garpun": {"≤3.6": 3.5, ">3.6": 4.5},
        "nogarpun": {"≤3.6": 3.0, ">3.6": 5.0}
    }
}

foydalanuvchi_holat = {}

@bot.message_handler(commands=['start'])
def start_handler(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🧱 Odnatonniy", "🖼️ Pechat")
    bot.send_message(message.chat.id, "🧱 Patalok turini tanlang:", reply_markup=markup)

@bot.message_handler(commands=['setkurs'])
def set_kurs(message):
    if message.from_user.id != ADMIN_ID:
        return bot.reply_to(message, "⛔ Sizda bu buyruq uchun ruxsat yo‘q.")
    try:
        global dollar_kursi
        kurs = int(message.text.split()[1])
        dollar_kursi = kurs
        bot.reply_to(message, f"✅ Kurs yangilandi: {kurs:,} so‘m")
    except:
        bot.reply_to(message, "❌ Foydalanish: /setkurs 12800")

@bot.message_handler(func=lambda m: m.text in ["🧱 Odnatonniy", "🖼️ Pechat"])
def tur_tanlandi(message):
    tur = "odnatonniy" if "Odnatonniy" in message.text else "pechat"
    foydalanuvchi_holat[message.chat.id] = {"tur": tur}
    bot.send_message(message.chat.id, "📏 Eni metrda (masalan: 3.45):")

@bot.message_handler(func=lambda m: m.chat.id in foydalanuvchi_holat and "eni" not in foydalanuvchi_holat[m.chat.id])
def eni_qabul(message):
    try:
        eni = float(message.text.replace(',', '.'))
        foydalanuvchi_holat[message.chat.id]["eni"] = eni
        bot.send_message(message.chat.id, "📐 Bo‘yni metrda (masalan: 5):")
    except:
        bot.send_message(message.chat.id, "❌ Noto‘g‘ri. Masalan: 3.45")

@bot.message_handler(func=lambda m: m.chat.id in foydalanuvchi_holat and "eni" in foydalanuvchi_holat[m.chat.id])
def boyi_qabul(message):
    try:
        boyi = float(message.text.replace(',', '.'))
        info = foydalanuvchi_holat.pop(message.chat.id)
        eni = info["eni"]
        tur = info["tur"]
        kvadrat = eni * boyi

        # 1. Narxlar
        key = ">3.6" if eni > 3.6 else "≤3.6"
        narx1_usd = narxlar[tur]["nogarpun"][key]
        narx2_usd = narxlar[tur]["garpun"][key]
        narx1 = round(narx1_usd * kvadrat * dollar_kursi)
        narx2 = round(narx2_usd * kvadrat * dollar_kursi)

        # 2. Baget hisoblash
        baget_uzunligi = round((eni + boyi) * 2, 2)
        baget_donasi = 2.5
        baget_soni = math.ceil(baget_uzunligi / baget_donasi)
        yakuniy_baget_uzunlik = baget_soni * baget_donasi
        baget_narx = round(yakuniy_baget_uzunlik * 0.45 * dollar_kursi)

        # 3. Javob
        javob = f"""📐 Eni: {eni} m
📐 Bo‘yi: {boyi} m
🔲 Kvadrat: {round(kvadrat, 2)} m²

🔹 Garpunsiz narx: {narx1:,} so‘m
🔸 Garpunli narx: {narx2:,} so‘m

🪵 Baget kerak: {baget_uzunligi} m
📦 1 dona = 2.5 m → Sizga {baget_soni} dona kerak
📏 Yakuniy uzunlik: {yakuniy_baget_uzunlik} m
💰 Baget narxi: {baget_narx:,} so‘m""".replace(",", " ")

        bot.send_message(message.chat.id, javob)

    except:
        bot.send_message(message.chat.id, "❌ Noto‘g‘ri. Masalan: 5")

bot.polling(none_stop=True)
