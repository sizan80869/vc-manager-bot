
import os
import logging

from telethon import TelegramClient, functions
from telethon.sessions import StringSession
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)

BOT_TOKEN = os.environ["BOT_TOKEN"]
API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION = os.environ["SESSION"]
CHANNEL = os.environ["CHANNEL"]
ADMIN_ID = int(os.environ["ADMIN_ID"])

logging.basicConfig(level=logging.INFO)

client = TelegramClient(
    StringSession(SESSION),
    API_ID,
    API_HASH
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔴 LIVE STREAM MANAGER\n\n"
        "/status - Live Status\n"
        "/endvc - End Channel Live"
    )


async def status(update, context):
    if update.effective_user.id != ADMIN_ID:
        return

    try:
        channel = await client.get_entity(CHANNEL)
        result = await client(
            functions.channels.GetFullChannelRequest(channel)
        )

        call = result.full_chat.call

        if call:
            await update.message.reply_text(
                "🟢 Channel Live is ACTIVE"
            )
        else:
            await update.message.reply_text(
                "🔴 No active Live Stream"
            )

    except Exception as e:
        await update.message.reply_text(
            f"Error: {str(e)[:300]}"
        )


async def endvc(update, context):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized")
        return

    try:
        channel = await client.get_entity(CHANNEL)

        result = await client(
            functions.channels.GetFullChannelRequest(channel)
        )

        call = result.full_chat.call

        if not call:
            await update.message.reply_text(
                "🔴 No active Live Stream found."
            )
            return

        await client(
            functions.phone.DiscardGroupCallRequest(
                call=call
            )
        )

        await update.message.reply_text(
            "✅ Channel Live Stream Ended!"
        )

    except Exception as e:
        await update.message.reply_text(
            f"❌ Failed: {str(e)[:300]}"
        )


async def main():
    await client.connect()

    if not await client.is_user_authorized():
        raise RuntimeError("Telegram user session is not authorized")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("endvc", endvc))

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    print("Live Stream Manager is running!")

    import asyncio
    await asyncio.Event().wait()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
