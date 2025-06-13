from django.core.management.base import BaseCommand
from django.conf import settings
import telebot
from telebot import types
from bot.models import TelegramUser
from bot.keyboard import *

bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)

# Step tracking (simple in-memory)
user_steps = {}

class Command(BaseCommand):
    help = 'Run Telegram Bot'

    def handle(self, *args, **options):

        @bot.message_handler(commands=['start'])
        def start(message):
            chat_id = message.chat.id
            TelegramUser.objects.get_or_create(
                chat_id=chat_id,
                defaults={
                    'username': message.from_user.username,
                    'first_name': message.from_user.first_name,
                    'last_name': message.from_user.last_name
                }
            )
            bot.send_message(chat_id, "Tilni tanlang:", reply_markup=generate_language())
            user_steps[chat_id] = 'choose_language'

        @bot.message_handler(func=lambda message: user_steps.get(message.chat.id) == 'choose_language')
        def handle_language(message):
            chat_id = message.chat.id
            lang = message.text

            user = TelegramUser.objects.get(chat_id=chat_id)
            if lang == "🇺🇿Uz":
                user.language = "uz"
            elif lang == "🇷🇺Ru":
                user.language = "ru"
            else:
                bot.send_message(chat_id, "Iltimos, tugmalardan birini tanlang.")
                return

            user.save()
            bot.send_message(chat_id, "Ismingizni yuboring:")
            user_steps[chat_id] = 'enter_name'

        @bot.message_handler(func=lambda message: user_steps.get(message.chat.id) == 'enter_name')
        def handle_name(message):
            chat_id = message.chat.id
            user = TelegramUser.objects.get(chat_id=chat_id)
            user.full_name = message.text
            user.save()

            bot.send_message(chat_id, "Telefon raqamingizni yuboring (Tugma orqali yoki +998 bilan yozing):", reply_markup=generate_contact_button())
            user_steps[chat_id] = 'enter_phone'

        # 1. Contact tugmasi orqali yuborilgan raqam
        @bot.message_handler(content_types=['contact'])
        def handle_contact(message):
            chat_id = message.chat.id
            if user_steps.get(chat_id) != 'enter_phone':
                return

            phone = message.contact.phone_number
            if not phone.startswith('+998'):
                bot.send_message(chat_id, "Iltimos, faqat O'zbekiston raqamini yuboring (+998 bilan boshlang).")
                return

            user = TelegramUser.objects.get(chat_id=chat_id)
            user.phone_number = phone
            user.is_registered = True
            user.save()

            bot.send_message(chat_id, "Ro'yxatdan muvaffaqiyatli o'tdingiz! ✅", reply_markup=generate_main())
            user_steps.pop(chat_id, None)
            bot.register_next_step_handler(message, main_catalog)

        # 2. Oddiy yozilgan raqamni qabul qilish va tekshirish
        @bot.message_handler(func=lambda message: user_steps.get(message.chat.id) == 'enter_phone')
        def handle_phone_text(message):
            chat_id = message.chat.id
            phone = message.text.strip().replace(" ", "")

            if not (phone.startswith("+998") and len(phone) == 13 and phone[1:].isdigit()):
                bot.send_message(chat_id, "Telefon raqamingiz noto‘g‘ri! Iltimos, +998 bilan boshlanadigan to‘liq raqam yuboring.")
                return

            user = TelegramUser.objects.get(chat_id=chat_id)
            user.phone_number = phone
            user.is_registered = True
            user.save()

            bot.send_message(chat_id, "Ro'yxatdan muvaffaqiyatli o'tdingiz! ✅\nAsosiy sahifamizga xush kelibsiz!", reply_markup=generate_main())
            user_steps.pop(chat_id, None)
            bot.register_next_step_handler(message,main_catalog)

        def main_catalog(message):
            chat_id = message.chat.id

            if message.text == "💎 Mahsulotlar":
                bot.send_message(chat_id, "Kategoriyani tanlang:", reply_markup=generate_catalog_inline())


            if message.text == "📞 Bog'lanish":
                bot.send_message(chat_id, "<b>Aloqa ma’lumotlari ga bossa quyidagi ma’lumotlar</b>\n\n"
                                          "<b>Eelefon raqamlari:</b> +998991234567\n"
                                          "<b>Elektron pochta:</b> example@gmail.com\n"
                                          "<b>Manzillari:</b> Toshkent\n"
                                          "<b>Ofis vaqtlari:</b> 09:00 – 18:00", parse_mode='HTML',
                                 reply_markup=generate_connect())
                bot.register_next_step_handler(message, connect)

            elif message.text == "🔗 Tilni o'zgartirish":
                bot.send_message(chat_id, "Tilni tanlang!", reply_markup=generate_language())
                bot.register_next_step_handler(message, start)


        def catalog_items(message):
            chat_id = message.chat.id

            if message.text == "📺 Televizorlar":
                pass

            if message.text == "📲 Telefonlar":
                pass

            if message.text == "⌚️ Soatlar":
                pass

            if message.text == "🔙Orqaga":
                return back_to_main(message)

        def back_to_main(message):
            chat_id = message.chat.id
            bot.send_message(chat_id, 'Asosiy sahifamizga xush kelibsiz!',reply_markup=generate_main())
            bot.register_next_step_handler(message, main_catalog)

        def connect(message):
            chat_id = message.chat.id

            if message.text == "📍Geolokatsiya":
                bot.send_message(chat_id, 'Bizning geolokatsiya !')
                bot.send_location(chat_id, latitude=40.86091, longitude=69.58965, reply_markup=generate_back())
                bot.register_next_step_handler(message, back_to_main)

            elif message.text == "🔙Orqaga":
                return back_to_main(message)


        @bot.callback_query_handler(func=lambda call: call.data.startswith("category_"))
        def handle_category_callback(call):
            category_id = int(call.data.split("_")[1])
            markup = generate_product_list(category_id)
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="Mahsulotni tanlang:",
                reply_markup=markup
            )

        @bot.callback_query_handler(func=lambda call: call.data.startswith("product_"))
        def handle_product_callback(call):
            product_id = int(call.data.split("_")[1])
            markup = generate_color_list(product_id)
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="Rangni tanlang:",
                reply_markup=markup
            )

        @bot.callback_query_handler(func=lambda call: call.data.startswith("color_"))
        def handle_color_callback(call):
            from product.models import ProductColor  # ichkarida import qilamiz
            color_id = int(call.data.split("_")[1])
            color = ProductColor.objects.select_related('product').prefetch_related('images').get(id=color_id)
            product = color.product
            images = color.images.all()

            # Mahsulot rasmi
            if images.exists():
                image = images.first().image.path  # yoki .url agar s3 dan ishlatilsa
                with open(image, 'rb') as photo:
                    caption = f"{product.name}\n💰 Narxi: {color.price} so'm"
                    bot.send_photo(
                        call.message.chat.id,
                        photo=photo,
                        caption=caption,
                        reply_markup=generate_product_action_buttons(color_id)
                    )
            else:
                bot.send_message(call.message.chat.id, "Rasm topilmadi.")

        @bot.callback_query_handler(func=lambda call: call.data.startswith("back_to_categories"))
        def back_to_categories(call):
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="Kategoriyani tanlang:",
                reply_markup=generate_catalog_inline()
            )

        @bot.callback_query_handler(func=lambda call: call.data.startswith("back_to_products_"))
        def back_to_products(call):
            category_id = int(call.data.split("_")[-1])
            markup = generate_product_list(category_id)
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="Mahsulotni tanlang:",
                reply_markup=markup
            )

        bot.polling(non_stop=True)
