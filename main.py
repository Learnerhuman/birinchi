import json
import random
from aiogram import Bot, Dispatcher, executor, types
import asyncio

TOKEN = "8286292205:AAHavxWX8LhMIlBDApmFv_ezvpqYrW1ZlNo"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

with open("jsonfile.json", "r", encoding="utf-8") as f:
    QUESTIONS = json.load(f)

sessions = {}

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("Assalomu alaykum!\nTest boshlash uchun /question deb yozing.")

@dp.message_handler(commands=["question"])
async def ask_range(message: types.Message):
    await message.answer("Savollar oralig'ini kiriting. Masalan: 10-30")

@dp.message_handler(commands=["finish"])
async def finish_test(message: types.Message):
    uid = message.from_user.id
    if uid in sessions:
        data = sessions[uid]
        await message.answer(f"Test yakunlandi!\nNatija: {data['score']}/{data['total']}")
        del sessions[uid]
    else:
        await message.answer("Faol test yo'q.")

@dp.message_handler(lambda msg: "-" in msg.text)
async def start_test(message: types.Message):
    try:
        a, b = map(int, message.text.split("-"))
        selected = [q for q in QUESTIONS if a <= q["id"] <= b]
        random.shuffle(selected)

        sessions[message.from_user.id] = {
            "questions": selected,
            "index": 0,
            "score": 0,
            "total": len(selected),
            "last_poll": None,
            "last_correct": None
        }

        await send_quiz(message.from_user.id, message.chat.id)

    except:
        await message.answer("Format xato. Masalan: 1-25")

async def send_quiz(user_id, chat_id):
    if user_id not in sessions:
        return

    data = sessions[user_id]
    if data["index"] >= data["total"]:
        await bot.send_message(chat_id, f"Test tugadi!\nNatija: {data['score']}/{data['total']}")
        del sessions[user_id]
        return

    q = data["questions"][data["index"]]

    options = q["options"].copy()
    correct_text = options[0]      # jsonda 1-variant to'g'ri
    random.shuffle(options)       # variantlarni aralashtiramiz
    correct_index = options.index(correct_text)

    poll = await bot.send_poll(
        chat_id=chat_id,
        question=q["question"],
        options=options,
        type="quiz",
        correct_option_id=correct_index,
        is_anonymous=False,
        open_period=30             # 30 soniya
    )

    data["last_poll"] = poll.poll.id
    data["last_correct"] = correct_index

@dp.poll_answer_handler()
async def handle_answer(poll_answer: types.PollAnswer):
    for uid, data in sessions.items():
        if poll_answer.poll_id == data.get("last_poll"):
            chosen = poll_answer.option_ids[0]

            if chosen == data["last_correct"]:
                data["score"] += 1

            data["index"] += 1
            await send_quiz(uid, poll_answer.user.id)
            break

if __name__ == "__main__":
    executor.start_polling(dp)
