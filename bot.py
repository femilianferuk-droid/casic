import logging
import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Токен бота
BOT_TOKEN = "8331254765:AAGIzkKOSIekInIyUP-7rVVp3zLFkxIMtgQ"

# Минимальные значения
MIN_BET = 2
MIN_DEPOSIT = 10
MIN_WITHDRAWAL = 30

# ID администратора
ADMIN_CHAT_ID = 7973988177

# Хранение данных
user_balances = {}
admin_mode = {}
user_broadcast = {}
user_bets = {}  # Хранение текущих ставок пользователей

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user_id = update.effective_user.id
    
    # Проверка на администратора
    if user_id == ADMIN_CHAT_ID:
        await show_admin_panel(update, context)
        return
    
    if user_id not in user_balances:
        user_balances[user_id] = 0
    
    keyboard = [
        [InlineKeyboardButton("🎲 Кубик", callback_data="game_dice")],
        [InlineKeyboardButton("🏀 Баскетбол", callback_data="game_basketball")],
        [InlineKeyboardButton("⚽ Футбол", callback_data="game_football")],
        [InlineKeyboardButton("💰 Баланс", callback_data="balance")],
        [InlineKeyboardButton("📥 Пополнение", callback_data="deposit")],
        [InlineKeyboardButton("📤 Вывод", callback_data="withdraw")],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(
            f"🎰 Добро пожаловать в *Nezeex Casino*! 🎰\n\n"
            f"💰 Ваш баланс: *{user_balances[user_id]}₽*\n\n"
            f"*Доступные игры:*\n"
            f"🎲 Кубик - угадай число\n"
            f"🏀 Баскетбол - попади в кольцо\n"
            f"⚽ Футбол - забивай голы\n\n"
            f"*Минимальные суммы:*\n"
            f"• Ставка: *{MIN_BET}₽*\n"
            f"• Пополнение: *{MIN_DEPOSIT}₽*\n"
            f"• Вывод: *{MIN_WITHDRAWAL}₽*",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await update.callback_query.edit_message_text(
            f"🎰 Добро пожаловать в *Nezeex Casino*! 🎰\n\n"
            f"💰 Ваш баланс: *{user_balances[user_id]}₽*\n\n"
            f"*Доступные игры:*\n"
            f"🎲 Кубик - угадай число\n"
            f"🏀 Баскетбол - попади в кольцо\n"
            f"⚽ Футбол - забивай голы\n\n"
            f"*Минимальные суммы:*\n"
            f"• Ставка: *{MIN_BET}₽*\n"
            f"• Пополнение: *{MIN_DEPOSIT}₽*\n"
            f"• Вывод: *{MIN_WITHDRAWAL}₽*",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def show_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать админ-панель"""
    keyboard = [
        [InlineKeyboardButton("👤 Изменить баланс", callback_data="admin_balance")],
        [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton("📢 Рассылка", callback_data="admin_broadcast")],
        [InlineKeyboardButton("🔙 В главное меню", callback_data="main_menu")],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    total_users = len(user_balances)
    total_balance = sum(user_balances.values())
    
    if update.message:
        await update.message.reply_text(
            f"🛠️ *Панель администратора Nezeex Casino*\n\n"
            f"📊 Статистика:\n"
            f"• Всего пользователей: {total_users}\n"
            f"• Общий баланс: {total_balance}₽\n\n"
            f"Выберите действие:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await update.callback_query.edit_message_text(
            f"🛠️ *Панель администратора Nezeex Casino*\n\n"
            f"📊 Статистика:\n"
            f"• Всего пользователей: {total_users}\n"
            f"• Общий баланс: {total_balance}₽\n\n"
            f"Выберите действие:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def admin_balance_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик изменения баланса"""
    query = update.callback_query
    user_id = query.from_user.id
    
    if user_id != ADMIN_CHAT_ID:
        await query.answer("У вас нет прав администратора!")
        return
    
    admin_mode[user_id] = "waiting_balance_user"
    
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_panel")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "👤 *Изменение баланса*\n\n"
        "Введите ID пользователя и сумму через пробел:\n"
        "Пример: `123456789 100` - установит баланс 100₽ для пользователя 123456789\n\n"
        "Или введите ID пользователя для просмотра текущего баланса:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def admin_broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик рассылки"""
    query = update.callback_query
    user_id = query.from_user.id
    
    if user_id != ADMIN_CHAT_ID:
        await query.answer("У вас нет прав администратора!")
        return
    
    admin_mode[user_id] = "waiting_broadcast"
    
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_panel")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📢 *Рассылка сообщений*\n\n"
        "Введите сообщение для рассылки всем пользователям:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def admin_stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать статистику"""
    query = update.callback_query
    user_id = query.from_user.id
    
    if user_id != ADMIN_CHAT_ID:
        await query.answer("У вас нет прав администратора!")
        return
    
    total_users = len(user_balances)
    total_balance = sum(user_balances.values())
    active_users = len([uid for uid, balance in user_balances.items() if balance > 0])
    
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_panel")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"📊 *Статистика Nezeex Casino*\n\n"
        f"• Всего пользователей: {total_users}\n"
        f"• Активных пользователей: {active_users}\n"
        f"• Общий баланс: {total_balance}₽\n"
        f"• Средний баланс: {total_balance/max(total_users, 1):.2f}₽\n\n"
        f"*Топ пользователей по балансу:*\n" +
        "\n".join([f"👤 {uid}: {balance}₽" for uid, balance in 
                  sorted(user_balances.items(), key=lambda x: x[1], reverse=True)[:5]]),
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка сообщений администратора"""
    user_id = update.message.from_user.id
    
    if user_id != ADMIN_CHAT_ID:
        return
    
    if user_id not in admin_mode:
        return
    
    text = update.message.text
    
    if admin_mode[user_id] == "waiting_balance_user":
        # Обработка изменения баланса
        try:
            if ' ' in text:
                user_id_to_change, amount = text.split(' ', 1)
                user_id_to_change = int(user_id_to_change)
                amount = int(amount)
                
                user_balances[user_id_to_change] = amount
                
                await update.message.reply_text(
                    f"✅ Баланс пользователя {user_id_to_change} установлен: {amount}₽"
                )
                
                # Пытаемся уведомить пользователя
                try:
                    await context.bot.send_message(
                        user_id_to_change,
                        f"🎰 *Nezeex Casino*\n\n"
                        f"Ваш баланс был изменен администратором!\n"
                        f"💰 Новый баланс: *{amount}₽*",
                        parse_mode='Markdown'
                    )
                except:
                    pass
                    
            else:
                user_id_to_check = int(text)
                balance = user_balances.get(user_id_to_check, 0)
                await update.message.reply_text(
                    f"💰 Баланс пользователя {user_id_to_check}: {balance}₽"
                )
                
        except ValueError:
            await update.message.reply_text("❌ Неверный формат! Используйте: `ID_пользователя сумма`")
        
        admin_mode.pop(user_id, None)
        await show_admin_panel(update, context)
    
    elif admin_mode[user_id] == "waiting_broadcast":
        # Обработка рассылки
        user_broadcast[user_id] = text
        
        keyboard = [
            [
                InlineKeyboardButton("✅ Отправить", callback_data="confirm_broadcast"),
                InlineKeyboardButton("❌ Отменить", callback_data="admin_panel")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"📢 *Предпросмотр рассылки:*\n\n{text}\n\n"
            f"Получателей: {len(user_balances)} пользователей\n"
            f"Отправить сообщение?",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def confirm_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждение и отправка рассылки"""
    query = update.callback_query
    user_id = query.from_user.id
    
    if user_id != ADMIN_CHAT_ID:
        await query.answer("У вас нет прав администратора!")
        return
    
    message_text = user_broadcast.get(user_id, "")
    
    if not message_text:
        await query.answer("Сообщение для рассылки не найдено!")
        return
    
    # Отправка рассылки
    sent_count = 0
    failed_count = 0
    
    await query.edit_message_text("🔄 Начинаю рассылку...")
    
    for chat_id in user_balances.keys():
        try:
            await context.bot.send_message(
                chat_id,
                f"📢 *Сообщение от Nezeex Casino:*\n\n{message_text}",
                parse_mode='Markdown'
            )
            sent_count += 1
        except:
            failed_count += 1
    
    keyboard = [[InlineKeyboardButton("🔙 В админ-панель", callback_data="admin_panel")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"✅ *Рассылка завершена!*\n\n"
        f"• Успешно отправлено: {sent_count}\n"
        f"• Не удалось отправить: {failed_count}\n"
        f"• Всего получателей: {len(user_balances)}",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    user_broadcast.pop(user_id, None)
    admin_mode.pop(user_id, None)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # Проверка на администратора
    if user_id == ADMIN_CHAT_ID:
        if query.data == "admin_panel":
            await show_admin_panel(update, context)
            return
        elif query.data == "admin_balance":
            await admin_balance_handler(update, context)
            return
        elif query.data == "admin_stats":
            await admin_stats_handler(update, context)
            return
        elif query.data == "admin_broadcast":
            await admin_broadcast_handler(update, context)
            return
        elif query.data == "confirm_broadcast":
            await confirm_broadcast(update, context)
            return
    
    if user_id not in user_balances:
        user_balances[user_id] = 0
    
    if query.data == "balance":
        await show_balance(query, user_id)
    elif query.data == "deposit":
        await deposit(query)
    elif query.data == "withdraw":
        await withdraw(query)
    elif query.data.startswith("game_"):
        await select_game(query, user_id, query.data.split("_")[1])
    elif query.data.startswith("bet_"):
        await place_bet(query, user_id, query.data.split("_")[1], context)
    elif query.data.startswith("change_bet_"):
        await change_bet(query, user_id, query.data)
    elif query.data == "main_menu":
        await main_menu(query, user_id)

async def show_balance(query, user_id):
    """Показать баланс пользователя"""
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"💰 Ваш баланс: *{user_balances[user_id]}₽*",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def deposit(query):
    """Пополнение баланса"""
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📥 *Пополнение баланса*\n\n"
        "Для пополнения баланса, напишите @nezeexsupp, сразу укажите на какую сумму!\n\n"
        f"Минимальное пополнение: *{MIN_DEPOSIT}₽*",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def withdraw(query):
    """Вывод средств"""
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📤 *Вывод средств*\n\n"
        "Для вывода средств, напишите @nezeexsupp, сразу укажите на какую сумму!\n\n"
        f"Минимальный вывод: *{MIN_WITHDRAWAL}₽*",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def select_game(query, user_id, game_type):
    """Выбор игры"""
    if user_balances[user_id] < MIN_BET:
        keyboard = [[InlineKeyboardButton("📥 Пополнить баланс", callback_data="deposit")],
                   [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"❌ Недостаточно средств для игры!\n"
            f"Минимальная ставка: {MIN_BET}₽\n"
            f"Ваш баланс: {user_balances[user_id]}₽",
            reply_markup=reply_markup
        )
        return
    
    # Устанавливаем начальную ставку
    if user_id not in user_bets:
        user_bets[user_id] = MIN_BET
    
    if game_type == "dice":
        await start_dice_game(query, user_id)
    elif game_type == "basketball":
        await start_basketball_game(query, user_id)
    elif game_type == "football":
        await start_football_game(query, user_id)

async def start_dice_game(query, user_id):
    """Начало игры в кубик"""
    current_bet = user_bets.get(user_id, MIN_BET)
    
    keyboard = [
        [
            InlineKeyboardButton("➖", callback_data="change_bet_dice_down"),
            InlineKeyboardButton(f"💰 {current_bet}₽", callback_data="current_bet"),
            InlineKeyboardButton("➕", callback_data="change_bet_dice_up")
        ],
        [InlineKeyboardButton("1-3 (x2)", callback_data="bet_dice_low")],
        [InlineKeyboardButton("4-6 (x2)", callback_data="bet_dice_high")],
        [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🎲 *Игра в кубик*\n\n"
        "Выберите ставку и вариант:\n"
        "• 1-3 (x2) - выигрыш если выпадет 1, 2 или 3\n"
        "• 4-6 (x2) - выигрыш если выпадет 4, 5 или 6\n\n"
        f"💰 Ваш баланс: *{user_balances[user_id]}₽*\n"
        f"🎯 Текущая ставка: *{current_bet}₽*",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def start_basketball_game(query, user_id):
    """Начало игры в баскетбол"""
    current_bet = user_bets.get(user_id, MIN_BET)
    
    keyboard = [
        [
            InlineKeyboardButton("➖", callback_data="change_bet_basketball_down"),
            InlineKeyboardButton(f"💰 {current_bet}₽", callback_data="current_bet"),
            InlineKeyboardButton("➕", callback_data="change_bet_basketball_up")
        ],
        [InlineKeyboardButton("🏀 Бросок (x3)", callback_data="bet_basketball")],
        [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🏀 *Баскетбол*\n\n"
        "Сделайте бросок в кольцо!\n"
        "Шанс выигрыша: 30%\n"
        "Коэффициент: x3\n\n"
        f"💰 Ваш баланс: *{user_balances[user_id]}₽*\n"
        f"🎯 Текущая ставка: *{current_bet}₽*",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def start_football_game(query, user_id):
    """Начало игры в футбол"""
    current_bet = user_bets.get(user_id, MIN_BET)
    
    keyboard = [
        [
            InlineKeyboardButton("➖", callback_data="change_bet_football_down"),
            InlineKeyboardButton(f"💰 {current_bet}₽", callback_data="current_bet"),
            InlineKeyboardButton("➕", callback_data="change_bet_football_up")
        ],
        [InlineKeyboardButton("⚽ Удар по воротам (x2.5)", callback_data="bet_football")],
        [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "⚽ *Футбол*\n\n"
        "Забейте гол!\n"
        "Шанс выигрыша: 40%\n"
        "Коэффициент: x2.5\n\n"
        f"💰 Ваш баланс: *{user_balances[user_id]}₽*\n"
        f"🎯 Текущая ставка: *{current_bet}₽*",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def change_bet(query, user_id, action_data):
    """Изменение суммы ставки"""
    current_bet = user_bets.get(user_id, MIN_BET)
    
    # Парсим действие из callback_data
    parts = action_data.split('_')
    game_type = parts[2]  # dice, basketball, football
    direction = parts[3]  # up, down
    
    if direction == "up":
        new_bet = min(current_bet + 1, user_balances[user_id])
        if new_bet < MIN_BET:
            new_bet = MIN_BET
    else:
        new_bet = max(current_bet - 1, MIN_BET)
    
    user_bets[user_id] = new_bet
    
    # Возвращаемся в соответствующую игру
    if game_type == "dice":
        await start_dice_game(query, user_id)
    elif game_type == "basketball":
        await start_basketball_game(query, user_id)
    elif game_type == "football":
        await start_football_game(query, user_id)

async def place_bet(query, user_id, game_type, context: ContextTypes.DEFAULT_TYPE):
    """Размещение ставки с анимацией"""
    bet_amount = user_bets.get(user_id, MIN_BET)
    
    if user_balances[user_id] < bet_amount:
        await query.answer("Недостаточно средств!")
        return
    
    # Анимация перед результатом
    message = await query.edit_message_text(
        "🎰 *Nezeex Casino* 🎰\n\n"
        "🔄 *Идет обработка ставки...*",
        parse_mode='Markdown'
    )
    
    # Анимация для разных игр
    if "dice" in game_type:
        await animate_dice(query, bet_amount)
    elif "basketball" in game_type:
        await animate_basketball(query, bet_amount)
    elif "football" in game_type:
        await animate_football(query, bet_amount)
    
    # Спин анимация
    await asyncio.sleep(1)
    
    # Вычитаем ставку
    user_balances[user_id] -= bet_amount
    
    # Определяем результат
    win = False
    multiplier = 1
    result_text = ""
    
    if game_type == "dice_low":
        dice_roll = random.randint(1, 6)
        win = dice_roll <= 3
        multiplier = 2
        result_text = f"🎲 Выпало: *{dice_roll}*"
        
    elif game_type == "dice_high":
        dice_roll = random.randint(1, 6)
        win = dice_roll >= 4
        multiplier = 2
        result_text = f"🎲 Выпало: *{dice_roll}*"
        
    elif game_type == "basketball":
        win = random.random() <= 0.3
        multiplier = 3
        result_text = "🏀 " + ("*Мяч в корзине! 🎯*" if win else "*Промах... ❌*")
        
    elif game_type == "football":
        win = random.random() <= 0.4
        multiplier = 2.5
        result_text = "⚽ " + ("*ГОООЛ! ⚽*" if win else "*Мимо ворот... ❌*")
    
    # Обрабатываем выигрыш/проигрыш
    if win:
        win_amount = int(bet_amount * multiplier)
        user_balances[user_id] += win_amount
        
        # Создаем красивый ASCII арт для выигрыша
        win_art = """
🎉🎉🎉🎉🎉🎉🎉🎉🎉
🎉               🎉
🎉   ПОБЕДА!   🎉
🎉               🎉
🎉🎉🎉🎉🎉🎉🎉🎉🎉

💰 ВЫИГРЫШ: {win_amount}₽
🏆 УДАЧА НА ВАШЕЙ СТОРОНЕ!
        """
        
        # Отправляем сообщение о выигрыше
        try:
            await context.bot.send_message(
                user_id,
                f"🎰 *Nezeex Casino* 🎰\n\n"
                f"✨ *ПОЗДРАВЛЯЕМ С ПОБЕДОЙ!* ✨\n\n"
                f"{win_art.format(win_amount=win_amount)}\n\n"
                f"💎 Ваш выигрыш: *{win_amount}₽*\n"
                f"💰 Общий баланс: *{user_balances[user_id]}₽*\n\n"
                f"🎯 Продолжайте в том же духе!",
                parse_mode='Markdown'
            )
        except Exception as e:
            print(f"Ошибка отправки уведомления: {e}")
            
        message_text = (
            f"🎉 *УДАЧА!* 🎉\n\n"
            f"{result_text}\n\n"
            f"🏆 Вы выиграли: *{win_amount}₽*\n"
            f"💰 Ваш баланс: *{user_balances[user_id]}₽*"
        )
    else:
        # Создаем красивый ASCII арт для проигрыша
        lose_art = """
😔😔😔😔😔😔😔😔😔
😔               😔
😔   НЕ УДАЧА   😔
😔               😔
😔😔😔😔😔😔😔😔😔

💸 Проигрыш: {bet_amount}₽
🎰 Удача будет в следующий раз!
        """
        
        # Отправляем сообщение о проигрыше
        try:
            await context.bot.send_message(
                user_id,
                f"🎰 *Nezeex Casino* 🎰\n\n"
                f"😔 *НЕ УДАЧА* 😔\n\n"
                f"{lose_art.format(bet_amount=bet_amount)}\n\n"
                f"💸 Вы проиграли: *{bet_amount}₽*\n"
                f"💰 Ваш баланс: *{user_balances[user_id]}₽*\n\n"
                f"🎯 Попробуйте еще раз - удача ждет вас!",
                parse_mode='Markdown'
            )
        except Exception as e:
            print(f"Ошибка отправки уведомления: {e}")
            
        message_text = (
            f"😔 *НЕ УДАЧА* 😔\n\n"
            f"{result_text}\n\n"
            f"💸 Вы проиграли: *{bet_amount}₽*\n"
            f"💰 Ваш баланс: *{user_balances[user_id]}₽*"
        )
    
    keyboard = [
        [InlineKeyboardButton("🎮 Играть снова", callback_data=f"game_{game_type.split('_')[1]}")],
        [InlineKeyboardButton("💰 Баланс", callback_data="balance")],
        [InlineKeyboardButton("🔙 В меню", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def animate_dice(query, bet_amount):
    """Анимация для игры в кубик"""
    frames = [
        "🎲 Бросок кубика...\n\n⚀ ⚁ ⚂",
        "🎲 Кубик летит...\n\n⚃ ⚄ ⚅",
        "🎲 Кубик на столе...\n\n🎲 🎲 🎲"
    ]
    
    for frame in frames:
        await query.edit_message_text(
            f"🎰 *Nezeex Casino* 🎰\n\n"
            f"{frame}\n"
            f"💰 Ставка: *{bet_amount}₽*",
            parse_mode='Markdown'
        )
        await asyncio.sleep(0.8)

async def animate_basketball(query, bet_amount):
    """Анимация для игры в баскетбол"""
    frames = [
        "🏀 Подготовка к броску...\n\n👤 ⟶ 🏀",
        "🏀 Бросок! Мяч в воздухе...\n\n⬆️ 🏀 ⬆️",
        "🏀 Мяч летит к кольцу...\n\n🏀 ⟶ 🏀"
    ]
    
    for frame in frames:
        await query.edit_message_text(
            f"🎰 *Nezeex Casino* 🎰\n\n"
            f"{frame}\n"
            f"💰 Ставка: *{bet_amount}₽*",
            parse_mode='Markdown'
        )
        await asyncio.sleep(0.8)

async def animate_football(query, bet_amount):
    """Анимация для игры в футбол"""
    frames = [
        "⚽ Разбег перед ударом...\n\n👤 🏃‍♂️ ⚽",
        "⚽ Удар! Мяч летит...\n\n⚽ ⟶ 🥅",
        "⚽ Мяч приближается к воротам...\n\n🎯 ⚽ 🎯"
    ]
    
    for frame in frames:
        await query.edit_message_text(
            f"🎰 *Nezeex Casino* 🎰\n\n"
            f"{frame}\n"
            f"💰 Ставка: *{bet_amount}₽*",
            parse_mode='Markdown'
        )
        await asyncio.sleep(0.8)

async def main_menu(query, user_id):
    """Возврат в главное меню"""
    keyboard = [
        [InlineKeyboardButton("🎲 Кубик", callback_data="game_dice")],
        [InlineKeyboardButton("🏀 Баскетбол", callback_data="game_basketball")],
        [InlineKeyboardButton("⚽ Футбол", callback_data="game_football")],
        [InlineKeyboardButton("💰 Баланс", callback_data="balance")],
        [InlineKeyboardButton("📥 Пополнение", callback_data="deposit")],
        [InlineKeyboardButton("📤 Вывод", callback_data="withdraw")],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"🎰 *Nezeex Casino* 🎰\n\n"
        f"💰 Ваш баланс: *{user_balances[user_id]}₽*\n\n"
        f"Выберите игру:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

def main():
    """Запуск бота"""
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", show_admin_panel))
    
    # Обработчики кнопок
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Обработчики сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_message))
    
    # Запуск бота
    application.run_polling()
    print("Бот Nezeex Casino запущен!")

if __name__ == "__main__":
    main()
