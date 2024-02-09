import asyncio
import logging

# для работы нужно установить aiogram (в терминале запустить команду: pip install aiogram)
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.types import Message, PreCheckoutQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from token1 import tokeno, ukassa

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token=tokeno)  # tokeno - токен бота следует добавить в файл "templates/token.py"
dp = Dispatcher()

balance = 0  # начальный баланс бота


# Хэндлер на команду /pay - выводит 2 инлайн-кнопки "Пополнить баланс" и "Проверить баланс"
@dp.message(Command("pay"))
async def pay_money(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Пополнить баланс",
        callback_data='add_balance')
    )
    builder.add(types.InlineKeyboardButton(
        text="Проверить баланс",
        callback_data='show_balance')
    )
    builder.adjust(1)
    await message.answer("Вот ссылка на оплату", reply_markup=builder.as_markup(resize_keyboard=True))

# обработчик нажатия кнопки "Проверить баланс" - выводит баланс бота
@dp.callback_query(F.data.startswith("show_balance"))
async def callbacks_num(callback: types.CallbackQuery):
    global balance
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text=f"Пополнить баланс",
        callback_data="add_balance")
    )
    builder.add(types.InlineKeyboardButton(
        text=f"Проверить баланс",
        callback_data="show_balance")
    )
    builder.adjust(1)
    await callback.message.edit_text(f"Итоговый баланс: {balance} RUB", reply_markup=builder.as_markup(resize_keyboard=True))

# обработчик кнопки "Пополнить баланс" - выводит инлайн-кнопку для пополнения баланса - здесь будут вводиться данные платежной карты
@dp.callback_query(F.data.startswith("add_balance"))
async def add_balance(callback: types.CallbackQuery):
    await callback.bot.send_invoice(
        chat_id=callback.from_user.id,
        title='Пополнение баланса',
        description='Перевод на сумму 100 RUB',
        provider_token=ukassa,  # ukassa - токен платежной системы следует добавить в файл "templates/token.py"
        payload='add_balance',
        currency='rub',  # валюта платежа
        prices=[
            types.LabeledPrice(
                label='Пополнить баланс на 100 руб.',
                amount=10000 # пополнение на 100.00 руб. - сумма указывается в копейках
            )
        ],
        start_parameter='SviatlanaYBot',
        provider_data=None,
        need_name=False,
        need_phone_number=False,
        need_email=False,
        need_shipping_address=False,
        is_flexible=False,
        disable_notification=False,
        protect_content=False,
        reply_to_message_id=None,
        reply_markup=None,
        request_timeout=60
    )

# ожидает отправки платежа
@dp.pre_checkout_query(lambda query: True)
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    print(pre_checkout_query)  # выводит данные о платеже в консоль

# вывод баланса в чат в случае успешного платежа
@dp.message(F.successful_payment)
async def success_payment(message: Message):
    global balance
    balance += message.successful_payment.total_amount // 100
    print(message.from_user.id, message.from_user.username)  # выводит в консоль айди и имя пользователя, совершившего платеж
    await message.answer(f"Tекущий баланс: {balance} RUB")


# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
