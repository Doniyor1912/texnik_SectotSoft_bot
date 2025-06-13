from django.utils.html import format_html
from django.contrib import admin
from .models import *

class ColorImageInline(admin.TabularInline):
    model = ColorImage
    extra = 1


class ProductColorInline(admin.StackedInline):
    model = ProductColor
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'parent')
    search_fields = ('name',)
    list_filter = ('parent',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'get_categories', 'get_colors_and_prices', 'get_images')
    search_fields = ('name',)
    list_filter = ('categories',)
    inlines = [ProductColorInline]

    def get_categories(self, obj):
        return ", ".join([cat.name for cat in obj.categories.all()])
    get_categories.short_description = "Kategoriyalar"

    def get_colors_and_prices(self, obj):
        colors = ProductColor.objects.filter(product=obj)
        return format_html("<br>".join(
            [f"<b>{c.color_name}</b>: {c.price} so'm" for c in colors]
        ))
    get_colors_and_prices.short_description = "Rang va Narxlar"

    def get_images(self, obj):
        colors = ProductColor.objects.filter(product=obj)
        html = ""
        for c in colors:
            images = ColorImage.objects.filter(color=c)
            for img in images:
                html += f'<img src="{img.image.url}" width="50" style="margin:2px;">'
        return format_html(html)
    get_images.short_description = "Rasmlar"


@admin.register(ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'color_name', 'price')
    inlines = [ColorImageInline]
    search_fields = ('color_name',)
    list_filter = ('product',)


@admin.register(ColorImage)
class ColorImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'color', 'get_image')
    list_filter = ('color',)

    def get_image(self, obj):
        return format_html('<img src="{}" width="50"/>', obj.image.url)
    get_image.short_description = "Rasm"
