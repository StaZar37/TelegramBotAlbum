from typing import List
from aiogram import Dispatcher, Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import MediaGroupFilter
from aiogram.types import ContentType
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram_media_group import media_group_handler
import os
from aiogram.dispatcher import FSMContext
import time

token = '5363867723:AAE1qLkuokVY8kznynM7oO2XC-B7pmw0ye8'

bot = Bot(token=token)
dp = Dispatcher(bot, storage=MemoryStorage())

class StateGroup(StatesGroup): # создаем стейты
    name_alb = State()
    image = State()
    dir = State()
    
@dp.message_handler(commands=['start'], state=None)  # по команде старт запускаем бота, не добавляя никакого стейта
async def get_name_alb(message: types.Message):
    await message.answer('Введите название альбома')
    await StateGroup.name_alb.set() # устанавливает первое состояние


@dp.message_handler(state=StateGroup.name_alb) # в этом хендлере принимает состояние установленное ранее
async def name_album(message: types.Message, state: FSMContext): # устанавливаем нужные параметры 
    dir_name = message.text
    os.mkdir(dir_name) # создаем папку с введеным названием от пользователя
    await state.update_data(alb_name=dir_name) # обновляем данные стейтов, чтобы в дальнейшем можно было принимать их в других хендлерах
    await message.answer('Альбом успешно создан, теперь отправьте фото (2-5)')
    await StateGroup.image.set() # устанавливает второе состояние


@dp.message_handler(MediaGroupFilter(is_media_group=True),  content_types=ContentType.PHOTO, state=StateGroup.image)  # устанавливаем нужные параметры и передаем стейт, переданный выше
@media_group_handler
async def album_handler(messages: List[types.Message], state: FSMContext):  # устанавливаем нужные параметры 
    data = await state.get_data() # получаем данные из стейтов в предыдущих хендлерах
    dir_name = data.get('alb_name') # берем название альбом и передаем его переменной
    await types.ChatActions.upload_photo()
    for message in messages:
        await message.photo[-1].download(destination_dir=f'{dir_name}/') # качаем все фото, которые отправил пользователь
    await message.answer('Фото успешно загружены')
    time.sleep(1)
    await message.answer('Чтобы получить фото из определенного альбома, напишите его название')
    await StateGroup.dir.set() # устанавливает третее состояние

@dp.message_handler(state=StateGroup.dir, content_types=ContentType.TEXT)
async def name_album(message: types.Message, state: FSMContext):
    dir_name = message.text
    path = f'E:\My works\Python\works\\botalbum\{dir_name}\photos' # путь, куда будет грузиться фото
    media = types.MediaGroup() # аля какой то массив, що принимает пачку фото
    for photo in os.listdir(path):
        media.attach_photo(types.InputFile(path + '/' + photo)) # добаавление фото в массив media
    await bot.send_media_group(message.from_user['id'], media=media)
    await state.finish() # конец работы
        
if __name__ == "__main__":
    executor.start_polling(dp)
