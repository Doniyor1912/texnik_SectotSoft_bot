from telebot import types

from product.models import Category


def generate_language():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn_uz = types.KeyboardButton(text="🇺🇿Uz")
    btn_ru = types.KeyboardButton(text="🇷🇺Ru")
    keyboard.row(btn_uz, btn_ru)
    return keyboard


def generate_main():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn_television = types.KeyboardButton(text="💎 Mahsulotlar")
    btn_phone = types.KeyboardButton(text="📞 Bog'lanish")
    btn_back = types.KeyboardButton(text="🔗 Tilni o'zgartirish")
    keyboard.row(btn_television, btn_phone)
    keyboard.row(btn_back)
    return keyboard

# def generate_catalog():
#     keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
#     btn_television = types.KeyboardButton(text="📺 Televizorlar")
#     btn_phone = types.KeyboardButton(text="📲 Telefonlar")
#     btn_watch = types.KeyboardButton(text="⌚️ Soatlar")
#     btn_back = types.KeyboardButton(text="🔙Orqaga")
#     keyboard.row(btn_television, btn_phone)
#     keyboard.row(btn_watch)
#     keyboard.row(btn_back)
#     return keyboard


def generate_catalog():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    buttons = []
    for category in Category.objects.filter(parent=None):  # faqat root kategoriyalar
        buttons.append(types.KeyboardButton(category.name))  # yoki .name_ru agar til ru bo‘lsa

    # Orqaga tugmasi
    buttons.append(types.KeyboardButton("🔙Orqaga"))

    markup.add(*buttons)
    return markup



def generate_contact_button():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    contact_btn = types.KeyboardButton("📱 Raqamni yuborish", request_contact=True)
    keyboard.row(contact_btn)
    return keyboard


def generate_commit():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    btn_yes = types.KeyboardButton(text='Ha')
    btn_no = types.KeyboardButton(text='Yoq')
    keyboard.row(btn_yes, btn_no)
    return keyboard


def generate_back():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn = types.KeyboardButton(text="🔙Orqaga")
    keyboard.row(btn)
    return keyboard

def generate_connect():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn_location = types.KeyboardButton(text="📍Geolokatsiya")
    btn_back = types.KeyboardButton(text="🔙Orqaga")
    keyboard.row(btn_location, btn_back)
    return keyboard



from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from product.models import Category, Product, ProductColor


def generate_catalog_inline():
    markup = InlineKeyboardMarkup()
    categories = Category.objects.filter(parent=None)
    for cat in categories:
        markup.add(InlineKeyboardButton(text=cat.name, callback_data=f"category_{cat.id}"))
    return markup


def generate_product_list(category_id):
    markup = InlineKeyboardMarkup()
    products = Product.objects.filter(categories__id=category_id).distinct()
    for product in products:
        markup.add(InlineKeyboardButton(text=product.name, callback_data=f"product_{product.id}"))
    markup.add(InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_categories"))
    return markup


def generate_color_list(product_id):
    markup = InlineKeyboardMarkup()
    colors = ProductColor.objects.filter(product_id=product_id)
    for color in colors:
        markup.add(InlineKeyboardButton(text=color.color_name, callback_data=f"color_{color.id}"))
    markup.add(InlineKeyboardButton(text="🔙 Orqaga", callback_data=f"back_to_products_{product_id}"))
    return markup


def generate_product_action_buttons(product_color_id):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(text="🔎 Batafsil", url="https://example.com/product-detail"),
        InlineKeyboardButton(text="🛒 Savatcha", callback_data=f"add_to_cart_{product_color_id}")
    )
    return markup

