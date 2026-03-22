from __future__ import annotations

from typing import Any


DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = ("en", "ru", "uz")

LANGUAGE_LABELS: dict[str, str] = {
    "en": "English",
    "ru": "Русский",
    "uz": "O'zbek",
}

STYLE_KEYS: dict[str, str] = {
    "realistic": "style.realistic",
    "anime": "style.anime",
    "digital_art": "style.digital_art",
    "oil_painting": "style.oil_painting",
    "watercolor": "style.watercolor",
    "3d_render": "style.3d_render",
    "pixel_art": "style.pixel_art",
    "none": "style.none",
}

RATIO_KEYS: dict[str, str] = {
    "1:1": "ratio.square",
    "9:16": "ratio.portrait",
    "16:9": "ratio.landscape",
}

TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        "app.language_prompt": "Choose your language:",
        "app.language_updated": "Language saved.",
        "app.start_title": "<b>AI Creator Bot</b>",
        "app.start_intro": "Generate AI images in seconds.",
        "app.start_plan": "Plan: <b>{plan}</b>",
        "app.start_remaining": "Remaining images: <b>{remaining}</b>",
        "app.start_menu_prompt": "Choose an action:",
        "app.plan_free": "FREE",
        "app.plan_basic": "BASIC",
        "app.plan_pro": "PRO",
        "button.generate_image": "Generate Image",
        "button.profile": "Profile",
        "button.buy_plan": "Buy Plan",
        "button.change_language": "Language",
        "button.buy_basic": "Buy Basic ({price} USDT)",
        "button.buy_pro": "Buy Pro ({price} USDT)",
        "button.i_paid": "I Paid",
        "button.prev": "Prev",
        "button.next": "Next",
        "button.approve_basic": "Approve BASIC",
        "button.approve_pro": "Approve PRO",
        "generation.choose_style": "Choose an art style:",
        "generation.choose_ratio": "Choose aspect ratio:",
        "generation.send_prompt": "Send your prompt (max 350 chars, text only).",
        "generation.invalid_prompt": "Invalid prompt. Remove links/HTML/blocked words and keep it short.",
        "generation.invalid_prompt_type": "Please send text only.",
        "generation.progress": "<b>Generating image...</b>\n\nStyle: {style}\nRatio: {ratio}\nPrompt: <i>{prompt}</i>",
        "generation.caption": "<b>Image generated</b> ({queue} priority)\n\nPlan: <b>{plan}</b>\nStyle: {style}\nRatio: {ratio}\nRemaining: <b>{remaining}</b> images",
        "queue.low": "low",
        "queue.medium": "medium",
        "queue.high": "high",
        "style.realistic": "Realistic",
        "style.anime": "Anime",
        "style.digital_art": "Digital Art",
        "style.oil_painting": "Oil Painting",
        "style.watercolor": "Watercolor",
        "style.3d_render": "3D Render",
        "style.pixel_art": "Pixel Art",
        "style.none": "No Style",
        "ratio.square": "1:1 Square",
        "ratio.portrait": "9:16 Portrait",
        "ratio.landscape": "16:9 Landscape",
        "profile.title": "<b>Your Profile</b>",
        "profile.plan": "Plan:",
        "profile.remaining": "Remaining:",
        "profile.usage": "Usage:",
        "profile.expiry": "Expiry:",
        "profile.not_available": "N/A",
        "history.title": "<b>Generation History</b>",
        "history.empty": "No images generated yet. Use /generate_image to create your first image.",
        "history.page": "{start}-{end} of {total}",
        "history.entry": "<b>{index}.</b> {date}\nPrompt: <i>{prompt}</i>\nStyle: {style} | Ratio: {ratio} | {plan}",
        "payment.choose_plan": "Choose a plan:",
        "payment.instructions": (
            "<b>{plan} plan</b>\n"
            "Limit: <b>{limit}</b> images/month\n"
            "Amount: <b>{amount} USDT (TRC20)</b>\n"
            "Wallet: <code>{wallet}</code>\n\n"
            "After transfer, tap <b>I Paid</b>."
        ),
        "payment.request_sent": "Your payment request was sent to admin. Activation happens after manual review.",
        "payment.no_admins": "No admin is configured. Contact support.",
        "payment.wallet_missing": "Payments are unavailable now. Wallet is not configured.",
        "payment.admin_request": (
            "New crypto payment request\n\n"
            "User ID: <code>{user_id}</code>\n"
            "Username: @{username}\n"
            "Plan: <b>{plan}</b>\n"
            "Amount: <b>{amount} USDT</b>"
        ),
        "payment.admin_approved": "Subscription approved: {plan} for user {user_id}.",
        "payment.user_approved": "Your {plan} plan is activated. Enjoy.",
        "referral.text": (
            "<b>Referral Program</b>\n\n"
            "Share your link and earn <b>{bonus}</b> free images for each friend.\n\n"
            "Your link:\n<code>{link}</code>\n\n"
            "Friends referred: <b>{count}</b>\n"
            "Bonus images earned: <b>{earned}</b>"
        ),
        "help.text": (
            "<b>Help</b>\n\n"
            "/start - open menu\n"
            "/generate_image - create image\n"
            "/profile - view limits\n"
            "/history - view history\n"
            "/buy - buy a plan\n"
            "/referral - referral program\n"
            "/help - this message"
        ),
        "admin.access_denied": "Access denied.",
        "admin.panel": (
            "<b>Admin Panel</b>\n\n"
            "Total users: <b>{total_users}</b>\n"
            "Paid users: <b>{paid_users}</b>\n"
            "Today's generations: <b>{today_generations}</b>\n\n"
            "<b>Commands:</b>\n"
            "<code>/admin stats</code>\n"
            "<code>/admin user &lt;id&gt;</code>\n"
            "<code>/admin grant &lt;id&gt; &lt;N&gt;</code>\n"
            "<code>/admin plan &lt;id&gt; &lt;BASIC|PRO&gt;</code>\n"
            "<code>/admin broadcast &lt;message&gt;</code>"
        ),
        "admin.stats": (
            "<b>Bot Statistics</b>\n\n"
            "Total users: <b>{total_users}</b>\n"
            "Paid users: <b>{paid_users}</b>\n"
            "Generations today: <b>{today_generations}</b>"
        ),
        "admin.user_details": (
            "<b>User {user_id}</b>\n\n"
            "{profile}\n"
            "Referrals: <b>{referrals}</b>\n"
            "Referral bonus: <b>{bonus}</b>"
        ),
        "admin.usage_user": "Usage: <code>/admin user &lt;telegram_id&gt;</code>",
        "admin.usage_grant": "Usage: <code>/admin grant &lt;telegram_id&gt; &lt;count&gt;</code>",
        "admin.usage_plan": "Usage: <code>/admin plan &lt;telegram_id&gt; &lt;BASIC|PRO&gt;</code>",
        "admin.usage_broadcast": "Usage: <code>/admin broadcast &lt;message&gt;</code>",
        "admin.invalid_telegram_id": "Invalid telegram_id.",
        "admin.invalid_arguments": "Invalid arguments.",
        "admin.invalid_count": "Count must be 1-1000.",
        "admin.user_not_found": "User not found.",
        "admin.granted": "Granted <b>{count}</b> bonus images to user {user_id}.",
        "admin.plan_activated": "Plan <b>{plan}</b> activated for user {user_id}.",
        "admin.broadcast_start": "Broadcasting to <b>{count}</b> users...",
        "admin.broadcast_done": "<b>Broadcast complete</b>\n\nSent: {sent}\nFailed: {failed}",
        "admin.unknown_command": "Unknown command. Use <code>/admin</code>.",
        "error.access_denied": "Access denied.",
        "error.free_limit_reached": "Free image limit reached. Upgrade your plan.",
        "error.monthly_limit_reached": "{plan} monthly image limit reached.",
        "error.request_rate_limited": "Too many requests. Try again in {seconds} seconds.",
        "error.cooldown_wait": "Please wait {seconds} seconds before the next request.",
        "error.global_rate_limit": "Global rate limit reached. Please retry in a few seconds.",
        "error.daily_generation_cap": "Daily generation cap reached. Try again tomorrow.",
        "error.unsupported_plan": "Unsupported plan.",
        "error.invalid_payment_payload": "Invalid payment payload.",
        "error.admin_only": "Admin access required.",
        "error.language_not_supported": "Unsupported language.",
        "error.provider_rate_limited": "Provider is rate-limited. Please wait and retry.",
        "error.provider_cost_guard": "Blocked by cost guard. Contact support.",
        "error.provider_billing": "Provider billing is not configured. Contact support.",
        "error.provider_timeout": "Generation timed out. Please try again.",
        "error.provider_unavailable": "Image generation is temporarily unavailable.",
        "error.unexpected": "Unexpected error. Please try again later.",
    },
    "ru": {
        "app.language_prompt": "Выберите язык:",
        "app.language_updated": "Язык сохранен.",
        "app.start_title": "<b>AI Creator Bot</b>",
        "app.start_intro": "Создавайте AI-изображения за секунды.",
        "app.start_plan": "Тариф: <b>{plan}</b>",
        "app.start_remaining": "Осталось изображений: <b>{remaining}</b>",
        "app.start_menu_prompt": "Выберите действие:",
        "app.plan_free": "FREE",
        "app.plan_basic": "BASIC",
        "app.plan_pro": "PRO",
        "button.generate_image": "Создать изображение",
        "button.profile": "Профиль",
        "button.buy_plan": "Купить тариф",
        "button.change_language": "Язык",
        "button.buy_basic": "Купить Basic ({price} USDT)",
        "button.buy_pro": "Купить Pro ({price} USDT)",
        "button.i_paid": "Я оплатил",
        "button.prev": "Назад",
        "button.next": "Вперед",
        "button.approve_basic": "Одобрить BASIC",
        "button.approve_pro": "Одобрить PRO",
        "generation.choose_style": "Выберите стиль:",
        "generation.choose_ratio": "Выберите соотношение сторон:",
        "generation.send_prompt": "Отправьте промпт (до 350 символов, только текст).",
        "generation.invalid_prompt": "Некорректный промпт. Уберите ссылки/HTML/запрещенные слова.",
        "generation.invalid_prompt_type": "Отправьте только текст.",
        "generation.progress": "<b>Генерирую изображение...</b>\n\nСтиль: {style}\nФормат: {ratio}\nПромпт: <i>{prompt}</i>",
        "generation.caption": "<b>Изображение готово</b> ({queue} очередь)\n\nТариф: <b>{plan}</b>\nСтиль: {style}\nФормат: {ratio}\nОсталось: <b>{remaining}</b>",
        "queue.low": "низкая",
        "queue.medium": "средняя",
        "queue.high": "высокая",
        "style.realistic": "Реализм",
        "style.anime": "Аниме",
        "style.digital_art": "Digital Art",
        "style.oil_painting": "Масло",
        "style.watercolor": "Акварель",
        "style.3d_render": "3D Render",
        "style.pixel_art": "Пиксель-арт",
        "style.none": "Без стиля",
        "ratio.square": "1:1 Квадрат",
        "ratio.portrait": "9:16 Портрет",
        "ratio.landscape": "16:9 Альбом",
        "profile.title": "<b>Ваш профиль</b>",
        "profile.plan": "Тариф:",
        "profile.remaining": "Осталось:",
        "profile.usage": "Использовано:",
        "profile.expiry": "Срок действия:",
        "profile.not_available": "Нет",
        "history.title": "<b>История генераций</b>",
        "history.empty": "Пока нет изображений. Используйте /generate_image.",
        "history.page": "{start}-{end} из {total}",
        "history.entry": "<b>{index}.</b> {date}\nПромпт: <i>{prompt}</i>\nСтиль: {style} | Формат: {ratio} | {plan}",
        "payment.choose_plan": "Выберите тариф:",
        "payment.instructions": (
            "<b>Тариф {plan}</b>\n"
            "Лимит: <b>{limit}</b> изображений/мес\n"
            "Сумма: <b>{amount} USDT (TRC20)</b>\n"
            "Кошелек: <code>{wallet}</code>\n\n"
            "После перевода нажмите <b>Я оплатил</b>."
        ),
        "payment.request_sent": "Запрос на оплату отправлен администратору. Активация после ручной проверки.",
        "payment.no_admins": "Администратор не настроен. Свяжитесь с поддержкой.",
        "payment.wallet_missing": "Платежи временно недоступны. Кошелек не настроен.",
        "payment.admin_request": (
            "Новый запрос на крипто-оплату\n\n"
            "User ID: <code>{user_id}</code>\n"
            "Username: @{username}\n"
            "Тариф: <b>{plan}</b>\n"
            "Сумма: <b>{amount} USDT</b>"
        ),
        "payment.admin_approved": "Подписка одобрена: {plan} для пользователя {user_id}.",
        "payment.user_approved": "Ваш тариф {plan} активирован.",
        "referral.text": (
            "<b>Реферальная программа</b>\n\n"
            "Делитесь ссылкой и получайте <b>{bonus}</b> бесплатных изображений за каждого друга.\n\n"
            "Ваша ссылка:\n<code>{link}</code>\n\n"
            "Приглашено друзей: <b>{count}</b>\n"
            "Заработано бонусов: <b>{earned}</b>"
        ),
        "help.text": (
            "<b>Помощь</b>\n\n"
            "/start - меню\n"
            "/generate_image - создать изображение\n"
            "/profile - лимиты\n"
            "/history - история\n"
            "/buy - купить тариф\n"
            "/referral - рефералы\n"
            "/help - это сообщение"
        ),
        "admin.access_denied": "Доступ запрещен.",
        "admin.panel": (
            "<b>Панель администратора</b>\n\n"
            "Всего пользователей: <b>{total_users}</b>\n"
            "Платных пользователей: <b>{paid_users}</b>\n"
            "Генераций сегодня: <b>{today_generations}</b>\n\n"
            "<b>Команды:</b>\n"
            "<code>/admin stats</code>\n"
            "<code>/admin user &lt;id&gt;</code>\n"
            "<code>/admin grant &lt;id&gt; &lt;N&gt;</code>\n"
            "<code>/admin plan &lt;id&gt; &lt;BASIC|PRO&gt;</code>\n"
            "<code>/admin broadcast &lt;message&gt;</code>"
        ),
        "admin.stats": (
            "<b>Статистика</b>\n\n"
            "Всего пользователей: <b>{total_users}</b>\n"
            "Платных пользователей: <b>{paid_users}</b>\n"
            "Генераций сегодня: <b>{today_generations}</b>"
        ),
        "admin.user_details": (
            "<b>Пользователь {user_id}</b>\n\n"
            "{profile}\n"
            "Рефералов: <b>{referrals}</b>\n"
            "Реферальный бонус: <b>{bonus}</b>"
        ),
        "admin.usage_user": "Использование: <code>/admin user &lt;telegram_id&gt;</code>",
        "admin.usage_grant": "Использование: <code>/admin grant &lt;telegram_id&gt; &lt;count&gt;</code>",
        "admin.usage_plan": "Использование: <code>/admin plan &lt;telegram_id&gt; &lt;BASIC|PRO&gt;</code>",
        "admin.usage_broadcast": "Использование: <code>/admin broadcast &lt;message&gt;</code>",
        "admin.invalid_telegram_id": "Неверный telegram_id.",
        "admin.invalid_arguments": "Неверные аргументы.",
        "admin.invalid_count": "Количество должно быть от 1 до 1000.",
        "admin.user_not_found": "Пользователь не найден.",
        "admin.granted": "Пользователю {user_id} начислено <b>{count}</b> бонусных изображений.",
        "admin.plan_activated": "Тариф <b>{plan}</b> активирован для пользователя {user_id}.",
        "admin.broadcast_start": "Рассылка для <b>{count}</b> пользователей...",
        "admin.broadcast_done": "<b>Рассылка завершена</b>\n\nОтправлено: {sent}\nОшибок: {failed}",
        "admin.unknown_command": "Неизвестная команда. Используйте <code>/admin</code>.",
        "error.access_denied": "Доступ запрещен.",
        "error.free_limit_reached": "Лимит FREE исчерпан. Обновите тариф.",
        "error.monthly_limit_reached": "Месячный лимит тарифа {plan} исчерпан.",
        "error.request_rate_limited": "Слишком много запросов. Повторите через {seconds} сек.",
        "error.cooldown_wait": "Подождите {seconds} сек. перед следующим запросом.",
        "error.global_rate_limit": "Глобальный лимит запросов превышен. Повторите позже.",
        "error.daily_generation_cap": "Дневной лимит генераций исчерпан. Попробуйте завтра.",
        "error.unsupported_plan": "Неподдерживаемый тариф.",
        "error.invalid_payment_payload": "Некорректные данные оплаты.",
        "error.admin_only": "Только для админа.",
        "error.language_not_supported": "Язык не поддерживается.",
        "error.provider_rate_limited": "Провайдер временно ограничил запросы. Повторите позже.",
        "error.provider_cost_guard": "Запрос заблокирован защитой стоимости. Обратитесь в поддержку.",
        "error.provider_billing": "Биллинг провайдера не настроен. Обратитесь в поддержку.",
        "error.provider_timeout": "Время генерации истекло. Повторите попытку.",
        "error.provider_unavailable": "Генерация временно недоступна.",
        "error.unexpected": "Непредвиденная ошибка. Повторите позже.",
    },
    "uz": {
        "app.language_prompt": "Tilni tanlang:",
        "app.language_updated": "Til saqlandi.",
        "app.start_title": "<b>AI Creator Bot</b>",
        "app.start_intro": "Sun'iy intellekt rasmlarini bir necha soniyada yarating.",
        "app.start_plan": "Tarif: <b>{plan}</b>",
        "app.start_remaining": "Qolgan rasmlar: <b>{remaining}</b>",
        "app.start_menu_prompt": "Amalni tanlang:",
        "app.plan_free": "FREE",
        "app.plan_basic": "BASIC",
        "app.plan_pro": "PRO",
        "button.generate_image": "Rasm yaratish",
        "button.profile": "Profil",
        "button.buy_plan": "Tarif sotib olish",
        "button.change_language": "Til",
        "button.buy_basic": "Basic olish ({price} USDT)",
        "button.buy_pro": "Pro olish ({price} USDT)",
        "button.i_paid": "To'lov qildim",
        "button.prev": "Oldingi",
        "button.next": "Keyingi",
        "button.approve_basic": "BASIC tasdiqlash",
        "button.approve_pro": "PRO tasdiqlash",
        "generation.choose_style": "Uslubni tanlang:",
        "generation.choose_ratio": "Nisbatni tanlang:",
        "generation.send_prompt": "Prompt yuboring (350 belgigacha, faqat matn).",
        "generation.invalid_prompt": "Noto'g'ri prompt. Havola/HTML/taqiqlangan so'zlarni olib tashlang.",
        "generation.invalid_prompt_type": "Faqat matn yuboring.",
        "generation.progress": "<b>Rasm yaratilmoqda...</b>\n\nUslub: {style}\nNisbat: {ratio}\nPrompt: <i>{prompt}</i>",
        "generation.caption": "<b>Rasm tayyor</b> ({queue} ustuvorlik)\n\nTarif: <b>{plan}</b>\nUslub: {style}\nNisbat: {ratio}\nQoldi: <b>{remaining}</b> ta",
        "queue.low": "past",
        "queue.medium": "o'rta",
        "queue.high": "yuqori",
        "style.realistic": "Realistik",
        "style.anime": "Anime",
        "style.digital_art": "Digital Art",
        "style.oil_painting": "Moybo'yoq",
        "style.watercolor": "Akvarel",
        "style.3d_render": "3D Render",
        "style.pixel_art": "Piksel Art",
        "style.none": "Uslubsiz",
        "ratio.square": "1:1 Kvadrat",
        "ratio.portrait": "9:16 Portret",
        "ratio.landscape": "16:9 Landshaft",
        "profile.title": "<b>Sizning profilingiz</b>",
        "profile.plan": "Tarif:",
        "profile.remaining": "Qoldi:",
        "profile.usage": "Ishlatilgan:",
        "profile.expiry": "Amal qilish muddati:",
        "profile.not_available": "Yo'q",
        "history.title": "<b>Yaratish tarixi</b>",
        "history.empty": "Hali rasm yaratilmagan. /generate_image buyrug'idan foydalaning.",
        "history.page": "{start}-{end} / {total}",
        "history.entry": "<b>{index}.</b> {date}\nPrompt: <i>{prompt}</i>\nUslub: {style} | Nisbat: {ratio} | {plan}",
        "payment.choose_plan": "Tarifni tanlang:",
        "payment.instructions": (
            "<b>{plan} tarifi</b>\n"
            "Limit: <b>{limit}</b> rasm/oy\n"
            "Summa: <b>{amount} USDT (TRC20)</b>\n"
            "Hamyon: <code>{wallet}</code>\n\n"
            "To'lovdan keyin <b>To'lov qildim</b> tugmasini bosing."
        ),
        "payment.request_sent": "To'lov so'rovi adminga yuborildi. Tekshiruvdan keyin tarif yoqiladi.",
        "payment.no_admins": "Admin sozlanmagan. Qo'llab-quvvatlashga murojaat qiling.",
        "payment.wallet_missing": "To'lovlar vaqtincha mavjud emas. Hamyon sozlanmagan.",
        "payment.admin_request": (
            "Yangi kripto to'lov so'rovi\n\n"
            "User ID: <code>{user_id}</code>\n"
            "Username: @{username}\n"
            "Tarif: <b>{plan}</b>\n"
            "Summa: <b>{amount} USDT</b>"
        ),
        "payment.admin_approved": "Obuna tasdiqlandi: {plan}, foydalanuvchi {user_id}.",
        "payment.user_approved": "Sizning {plan} tarifingiz faollashtirildi.",
        "referral.text": (
            "<b>Referral dasturi</b>\n\n"
            "Havolangizni ulashing va har bir do'st uchun <b>{bonus}</b> bepul rasm oling.\n\n"
            "Sizning havolangiz:\n<code>{link}</code>\n\n"
            "Taklif qilingan do'stlar: <b>{count}</b>\n"
            "Bonus rasmlar: <b>{earned}</b>"
        ),
        "help.text": (
            "<b>Yordam</b>\n\n"
            "/start - menyu\n"
            "/generate_image - rasm yaratish\n"
            "/profile - limitlarni ko'rish\n"
            "/history - tarix\n"
            "/buy - tarif sotib olish\n"
            "/referral - referral dasturi\n"
            "/help - shu xabar"
        ),
        "admin.access_denied": "Kirish taqiqlangan.",
        "admin.panel": (
            "<b>Admin paneli</b>\n\n"
            "Jami foydalanuvchi: <b>{total_users}</b>\n"
            "Pullik foydalanuvchi: <b>{paid_users}</b>\n"
            "Bugungi generatsiyalar: <b>{today_generations}</b>\n\n"
            "<b>Buyruqlar:</b>\n"
            "<code>/admin stats</code>\n"
            "<code>/admin user &lt;id&gt;</code>\n"
            "<code>/admin grant &lt;id&gt; &lt;N&gt;</code>\n"
            "<code>/admin plan &lt;id&gt; &lt;BASIC|PRO&gt;</code>\n"
            "<code>/admin broadcast &lt;message&gt;</code>"
        ),
        "admin.stats": (
            "<b>Bot statistikasi</b>\n\n"
            "Jami foydalanuvchi: <b>{total_users}</b>\n"
            "Pullik foydalanuvchi: <b>{paid_users}</b>\n"
            "Bugun generatsiya: <b>{today_generations}</b>"
        ),
        "admin.user_details": (
            "<b>Foydalanuvchi {user_id}</b>\n\n"
            "{profile}\n"
            "Referral soni: <b>{referrals}</b>\n"
            "Referral bonusi: <b>{bonus}</b>"
        ),
        "admin.usage_user": "Foydalanish: <code>/admin user &lt;telegram_id&gt;</code>",
        "admin.usage_grant": "Foydalanish: <code>/admin grant &lt;telegram_id&gt; &lt;count&gt;</code>",
        "admin.usage_plan": "Foydalanish: <code>/admin plan &lt;telegram_id&gt; &lt;BASIC|PRO&gt;</code>",
        "admin.usage_broadcast": "Foydalanish: <code>/admin broadcast &lt;message&gt;</code>",
        "admin.invalid_telegram_id": "Noto'g'ri telegram_id.",
        "admin.invalid_arguments": "Noto'g'ri argumentlar.",
        "admin.invalid_count": "Soni 1 dan 1000 gacha bo'lishi kerak.",
        "admin.user_not_found": "Foydalanuvchi topilmadi.",
        "admin.granted": "{user_id} foydalanuvchiga <b>{count}</b> bonus rasm berildi.",
        "admin.plan_activated": "{user_id} foydalanuvchiga <b>{plan}</b> tarifi yoqildi.",
        "admin.broadcast_start": "<b>{count}</b> foydalanuvchiga xabar yuborilmoqda...",
        "admin.broadcast_done": "<b>Yuborish yakunlandi</b>\n\nYuborildi: {sent}\nXatolar: {failed}",
        "admin.unknown_command": "Noma'lum buyruq. <code>/admin</code> dan foydalaning.",
        "error.access_denied": "Kirish taqiqlangan.",
        "error.free_limit_reached": "FREE limiti tugadi. Tarifni yangilang.",
        "error.monthly_limit_reached": "{plan} oylik limiti tugadi.",
        "error.request_rate_limited": "Juda ko'p so'rov. {seconds} soniyadan keyin urinib ko'ring.",
        "error.cooldown_wait": "Keyingi so'rov uchun {seconds} soniya kuting.",
        "error.global_rate_limit": "Global limitga yetildi. Birozdan keyin qayta urinib ko'ring.",
        "error.daily_generation_cap": "Kunlik limit tugadi. Ertaga urinib ko'ring.",
        "error.unsupported_plan": "Bunday tarif mavjud emas.",
        "error.invalid_payment_payload": "To'lov ma'lumotlari noto'g'ri.",
        "error.admin_only": "Faqat admin uchun.",
        "error.language_not_supported": "Til qo'llab-quvvatlanmaydi.",
        "error.provider_rate_limited": "Provayder vaqtincha chekladi. Keyinroq urinib ko'ring.",
        "error.provider_cost_guard": "Narx himoyasi sabab bloklandi. Qo'llab-quvvatlashga murojaat qiling.",
        "error.provider_billing": "Provayder billing sozlanmagan. Qo'llab-quvvatlashga murojaat qiling.",
        "error.provider_timeout": "Generatsiya vaqti tugadi. Qayta urinib ko'ring.",
        "error.provider_unavailable": "Rasm generatsiyasi vaqtincha mavjud emas.",
        "error.unexpected": "Kutilmagan xatolik. Keyinroq urinib ko'ring.",
    },
}


def normalize_language(language: str | None) -> str:
    if not language:
        return DEFAULT_LANGUAGE
    normalized = language.lower().strip().replace("_", "-")
    short = normalized.split("-", maxsplit=1)[0]
    if short in SUPPORTED_LANGUAGES:
        return short
    return DEFAULT_LANGUAGE


def is_supported_language(language: str | None) -> bool:
    if not language:
        return False
    normalized = language.lower().strip().replace("_", "-")
    short = normalized.split("-", maxsplit=1)[0]
    return short in SUPPORTED_LANGUAGES


def t(language: str | None, key: str, **kwargs: Any) -> str:
    lang = normalize_language(language)
    template = TRANSLATIONS.get(lang, {}).get(key) or TRANSLATIONS[DEFAULT_LANGUAGE].get(key)
    if not template:
        return key
    try:
        return template.format(**kwargs)
    except Exception:
        return template


def plan_label(language: str | None, plan: str) -> str:
    return t(language, f"app.plan_{plan.lower()}")


def style_label(language: str | None, style: str) -> str:
    key = STYLE_KEYS.get(style, "")
    if not key:
        return style
    return t(language, key)


def ratio_label(language: str | None, ratio: str) -> str:
    key = RATIO_KEYS.get(ratio, "")
    if not key:
        return ratio
    return t(language, key)
