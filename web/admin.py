from django.contrib import admin
from django.utils.safestring import mark_safe
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from .models import (
    Category,
    Subcategory,
    Product,
    ProductImage,
    Promotion,
    UsedPromotion,
    Subscriber,
    Cart,
    CartItem,
    Discount,
)


@admin.register(Category)
class CategoryAdmin(UnfoldModelAdmin):
    list_display = ("name", "slug", "is_active", "order")
    list_filter = ("is_active",)
    search_fields = ("name",)
    ordering = ("order", "name")
    
    def get_list_display(self, request):
        return ("name", "slug", "is_active", "order")
    
    def get_list_filter(self, request):
        return ("is_active",)
    
    def get_search_fields(self, request):
        return ("name",)


@admin.register(Subcategory)
class SubcategoryAdmin(UnfoldModelAdmin):
    list_display = ("name", "category", "slug", "is_active", "order")
    list_filter = ("category", "is_active")
    search_fields = ("name", "category__name")
    ordering = ("category__order", "category__name", "order", "name")


class ProductImageInline(admin.TabularInline):
    """Inline para gestionar imágenes de productos"""
    model = ProductImage
    extra = 1
    fields = ('image', 'is_main', 'order')





@admin.register(Product)
class ProductAdmin(UnfoldModelAdmin):
    list_display = ("name", "price", "stock", "category", "subcategory", "is_active", "is_featured", "stock_status", "list_images")
    list_filter = ("category", "subcategory", "is_active", "is_featured", "created_at")
    search_fields = ("name", "description", "sku")
    readonly_fields = ("created_at", "updated_at", "stock_status", "list_images")
    ordering = ("-created_at",)
    inlines = [ProductImageInline]

    
    def list_images(self, obj):
        """Muestra las imágenes del producto en la lista del admin"""
        images = obj.images.all()[:3]  # Mostrar máximo 3 imágenes
        if not images:
            return "Sin imágenes"
        
        html = '<div style="display: flex; gap: 5px;">'
        for image in images:
            html += f'<img src="{image.image.url}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />'
        html += '</div>'
        return mark_safe(html)
    
    list_images.short_description = "Imágenes"


@admin.register(ProductImage)
class ProductImageAdmin(UnfoldModelAdmin):
    """Admin para gestionar imágenes de productos"""
    list_display = ("product", "image", "is_main", "order", "created_at")
    list_filter = ("is_main", "created_at", "product__category")
    search_fields = ("product__name",)
    ordering = ("product__name", "order")
    readonly_fields = ("created_at",)


@admin.register(Subscriber)
class SubscriberAdmin(UnfoldModelAdmin):
    list_display = ("phone", "email", "is_active", "discount")
    list_filter = ("is_active", "discount")
    search_fields = ("phone", "email")
    ordering = ("phone",)





@admin.register(Promotion)
class PromotionAdmin(UnfoldModelAdmin):
    list_display = ("name", "discount", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)





@admin.register(Cart)
class CartAdmin(UnfoldModelAdmin):
    list_display = ("session_id", "subscriber", "created_at", "is_active", "get_total", "get_items_count")
    list_filter = ("is_active", "created_at")
    search_fields = ("session_id", "subscriber__phone")
    readonly_fields = ("created_at", "get_total", "get_items_count")
    ordering = ("-created_at",)
    
    def get_total(self, obj):
        return obj.total()
    
    def get_items_count(self, obj):
        return obj.items.count()
    
    get_total.short_description = "Total"
    get_items_count.short_description = "Items"


@admin.register(Discount)
class DiscountAdmin(UnfoldModelAdmin):
    list_display = ("name", "percentage", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(CartItem)
class CartItemAdmin(UnfoldModelAdmin):
    list_display = ("cart", "product", "quantity", "get_subtotal")

    def get_subtotal(self, obj):
        return obj.subtotal()
    
    get_subtotal.short_description = "Subtotal"
