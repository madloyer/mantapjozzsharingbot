import json
import string
import random
from bot import Client
from configs import markup, btn, fsubs_dict, config
from pyrogram import filters, types, errors


@Client.on_message(
    filters.incoming
    & ~filters.command(["start", "help", "ping", "batch"])
    & filters.private
    & filters.user(config.admins + [config.owner])
)
async def on_sended_msg(c: Client, m: types.Message):
    base_link = f"https://t.me/{c.username}?"
    random_string = "".join(
        random.choice(string.ascii_letters + string.digits)
        for _ in range(random.randint(10, 20))
    )
    with open("database.json", "r", encoding="utf-8") as f:
        try:
            datas = json.load(f)
        except json.decoder.JSONDecodeError:
            datas = []
    url = f"{base_link}start={random_string}"
    if m.chat.id == c.db.id:
        msg = await m.edit_reply_markup(
            markup(
                [
                    [
                        btn("Share Link", url=f"https://t.me/share/url?url={url}"),
                    ]
                ]
            )
        )
    else:
        msg = await m.copy(c.db.id)
        await m.reply(
            f"Ini Link yang bisa kamu share: `{url}`",
            reply_markup=markup(
                [[btn("Share Link", url=f"https://t.me/share/url?url={url}")]]
            ),
        )
    datas.append(
        {"chat_id": msg.chat.id, "msg_id": msg.id, "shorten_link": random_string}
    )
    with open("database.json", "w", encoding="utf-8") as f:
        json.dump(datas, f, indent=4)


@Client.on_message(filters.command("start"))
async def get_msg(c: Client, m: types.Message):
    if len(m.command) <= 1:
        await c.send_logger(f"{m.from_user.mention} melakukan start pada bot")
        return await m.reply(f"Halo {m.from_user.first_name}")
    try:
        for link in fsubs_dict.values():
            chat = await c.get_chat(link)
            member_status = (await c.get_chat_member(chat.id, m.from_user.id)).status
            if (
                member_status.MEMBER
                or member_status.ADMINISTRATOR
                or member_status.OWNER
            ):
                break
    except errors.UserNotParticipant:
        return await m.reply(
            "Silakan masuk kedalam semua grup/channel dibawah ini",
            reply_markup=markup(c.btn),
        )
    with open("database.json", "r", encoding="utf-8") as f:
        datas = json.load(f)
        for data in datas:
            if data["shorten_link"] == m.command[1]:
                if isinstance(data["msg_id"], list):
                    for msg_id in data["msg_id"]:
                        await c.copy_message(m.chat.id, data["chat_id"], msg_id)
                else:
                    await c.copy_message(m.chat.id, data["chat_id"], data["msg_id"])
                break
