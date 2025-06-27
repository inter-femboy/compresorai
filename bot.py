# bot.py
import asyncio
import os
import time
from aiogram import Bot, Dispatcher
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, ContentType, BufferedInputFile
import config
import utils

# Initialize bot and dispatcher
bot = Bot(token=config.TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)

# Define states
class CompressStates(StatesGroup):
    collecting_files = State()

# Handler for /start command
@dp.message(Command("start"))
async def start(message: Message):
    await message.reply("🎉 Welcome! I can compress your files into 7zip and zip archives. "
                       "Send /compress to start, then send your files one by one. When done, send /done.")

# Handler for /help command
@dp.message(Command("help"))
async def help_command(message: Message):
    await message.reply("ℹ️ To use this bot, send /compress to start sending files. "
                       "After sending all files, send /done to get the compressed archives.")

# Handler for /compress command
@dp.message(Command("compress"))
async def compress_command(message: Message, state: FSMContext):
    user_id = message.from_user.id
    temp_dir = f"temp/{user_id}"
    os.makedirs(temp_dir, exist_ok=True)
    await state.update_data(temp_dir=temp_dir)
    await state.set_state(CompressStates.collecting_files)
    await message.reply("📂 Please send the files you want to compress. When finished, send /done.")

# Handler for receiving documents in collecting_files state
@dp.message(lambda message: message.content_type == ContentType.DOCUMENT, StateFilter(CompressStates.collecting_files))
async def handle_document(message: Message, state: FSMContext):
    data = await state.get_data()
    temp_dir = data['temp_dir']
    file_info = await bot.get_file(message.document.file_id)
    file_path = file_info.file_path
    # Generate unique filename with timestamp
    local_file_path = os.path.join(temp_dir, f"{int(time.time())}_{message.document.file_name}")
    await bot.download_file(file_path, local_file_path)
    await message.reply(f"📄 File received: {message.document.file_name}")

# Handler for /done command
@dp.message(Command("done"), StateFilter(CompressStates.collecting_files))
async def done_compressing(message: Message, state: FSMContext):
    data = await state.get_data()
    temp_dir = data['temp_dir']
    files = [os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if os.path.isfile(os.path.join(temp_dir, f))]
    if not files:
        await message.reply("🚫 No files to compress.")
        await state.finish()
        return
    await message.reply("🔄 Compressing your files...")
    zip_archive = os.path.join(temp_dir, "archive.zip")
    seven_zip_archive = os.path.join(temp_dir, "archive.7z")
    utils.compress_to_zip(files, zip_archive)
    utils.compress_to_7zip(files, seven_zip_archive)
    # Send archives
    with open(zip_archive, 'rb') as f:
        zip_file = BufferedInputFile(f.read(), filename="archive.zip")
        await bot.send_document(message.chat.id, document=zip_file)
    with open(seven_zip_archive, 'rb') as f:
        seven_zip_file = BufferedInputFile(f.read(), filename="archive.7z")
        await bot.send_document(message.chat.id, document=seven_zip_file)
    await message.reply("✅ Archives sent successfully!")
    # Clean up
    utils.cleanup_temp_dir(temp_dir)
    await state.finish()

# Handler for other messages in collecting_files state
@dp.message(StateFilter(CompressStates.collecting_files))
async def handle_other_messages(message: Message):
    await message.reply("ℹ️ Please send files or use /done when finished.")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())