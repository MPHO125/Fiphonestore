from django.contrib import admin

from .models import iPhoneModel, Color, iPhoneProduct, Cart, CartItem



@admin.register(iPhoneModel)

class iPhoneModelAdmin(admin.ModelAdmin):

    list_display = ['name', 'release_year', 'display_size', 'storage_options']

    list_filter = ['release_year']

    search_fields = ['name', 'description']

    ordering = ['-release_year', 'name']



@admin.register(Color)

class ColorAdmin(admin.ModelAdmin):

    list_display = ['name', 'hex_code']

    search_fields = ['name']

    ordering = ['name']



@admin.register(iPhoneProduct)

class iPhoneProductAdmin(admin.ModelAdmin):

    list_display = ['iphone_model', 'color', 'storage', 'condition', 'grade', 'price', 'stock_quantity', 'is_active', 'cover_photo_thumbnail']

    list_filter = ['iphone_model', 'color', 'storage', 'condition', 'grade', 'is_active']

    search_fields = ['iphone_model__name', 'color__name']

    list_editable = ['price', 'stock_quantity', 'is_active']

    ordering = ['-created_at']

    

    # Add JavaScript for auto price calculation
    class Media:
        js = ('admin/js/iphone_price.js',)

    

    fieldsets = (

        ('Product Information', {

            'fields': ('iphone_model', 'color', 'storage', 'condition', 'grade')

        }),

        ('Pricing & Inventory', {

            'fields': ('price', 'stock_quantity', 'is_active')

        }),

        ('Product Images', {

            'fields': ('image', 'cover_photo'),

            'description': 'Upload product images. Cover photo will be used as the main image in product listings.'

        }),

    )

    

    def cover_photo_thumbnail(self, obj):

        if obj.cover_photo:

            return f'<img src="{obj.cover_photo.url}" width="50" height="50" style="object-fit: cover;" />'

        elif obj.image:

            return f'<img src="{obj.image.url}" width="50" height="50" style="object-fit: cover;" />'

        return "No Image"

    cover_photo_thumbnail.short_description = 'Cover Photo'

    cover_photo_thumbnail.allow_tags = True



@admin.register(Cart)

class CartAdmin(admin.ModelAdmin):

    list_display = ['session_key', 'created_at', 'updated_at']

    readonly_fields = ['session_key', 'created_at', 'updated_at']

    ordering = ['-created_at']



@admin.register(CartItem)

class CartItemAdmin(admin.ModelAdmin):

    list_display = ['cart', 'product', 'quantity', 'added_at']

    list_filter = ['added_at', 'product__iphone_model']

    search_fields = ['product__iphone_model__name', 'cart__session_key']

    ordering = ['-added_at']

