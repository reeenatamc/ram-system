from rest_framework import serializers
from web.models import (
    Category, Subcategory, Product, ProductImage, Promotion, UsedPromotion, 
    Subscriber, Cart, CartItem, Discount
)
from django.utils import timezone


class SubcategorySerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Subcategory
        fields = ['id', 'name', 'slug', 'category', 'is_active', 'order', 'products_count']
    
    def get_products_count(self, obj):
        return obj.products.count()


class CategorySerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()
    subcategories = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'is_active', 'order', 'products_count', 'subcategories']
    
    def get_products_count(self, obj):
        return obj.products.count()
    
    def get_subcategories(self, obj):
        subcategories = obj.subcategories.filter(is_active=True).order_by('order', 'name')
        return SubcategorySerializer(subcategories, many=True).data


class CategoryTreeSerializer(serializers.ModelSerializer):
    """Serializer para mostrar el árbol de categorías con subcategorías"""
    subcategories = serializers.SerializerMethodField()
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'subcategories', 'products_count']
    
    def get_subcategories(self, obj):
        subcategories = obj.subcategories.filter(is_active=True).order_by('order', 'name')
        return SubcategorySerializer(subcategories, many=True).data
    
    def get_products_count(self, obj):
        return obj.products.count()




class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer para imágenes de productos"""
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'image_url', 'is_main', 'order', 'created_at']
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    subcategory = SubcategorySerializer(read_only=True)
    subcategory_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    current_price = serializers.SerializerMethodField()
    has_promotion = serializers.SerializerMethodField()
    images = ProductImageSerializer(many=True, read_only=True)
    main_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'price', 'stock', 'sku', 'category', 'category_id',
            'subcategory', 'subcategory_id', 'is_active', 'is_featured', 'current_price', 'has_promotion',
            'is_in_stock', 'stock_status', 'images', 'main_image', 'created_at', 'updated_at'
        ]
    
    def get_current_price(self, obj):
        # Por ahora retorna el precio normal, se puede implementar promociones por producto después
        return obj.price
    
    def get_has_promotion(self, obj):
        # Por ahora retorna False, se puede implementar promociones por producto después
        return False
    
    def get_main_image(self, obj):
        """Retorna la imagen principal del producto"""
        main_image = obj.main_image
        if main_image:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(main_image.image.url)
            return main_image.image.url
        return None


class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = ['id', 'name', 'slug', 'discount', 'is_active']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['discount_formatted'] = f"{instance.discount}%"
        return data





class SubscriberSerializer(serializers.ModelSerializer):
    total_carts = serializers.SerializerMethodField()
    active_cart = serializers.SerializerMethodField()
    subscription_status = serializers.SerializerMethodField()
    whatsapp_link = serializers.SerializerMethodField()
    discount_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Subscriber
        fields = ['id', 'phone', 'email', 'is_active', 'discount_info', 'total_carts', 'active_cart', 'subscription_status', 'whatsapp_link']
    
    def get_total_carts(self, obj):
        return obj.total_carts
    
    def get_active_cart(self, obj):
        # Obtener el carrito activo del suscriptor sin crear referencia circular
        active_cart = obj.carts.filter(is_active=True).first()
        if active_cart:
            # Retornar solo datos básicos del carrito, no el serializer completo
            return {
                'id': active_cart.id,
                'session_id': active_cart.session_id,
                'created_at': active_cart.created_at,
                'is_active': active_cart.is_active,
                'total': active_cart.total(),
                'items_count': active_cart.items.count()
            }
        return None
    
    def get_subscription_status(self, obj):
        return obj.subscription_status
    
    def get_whatsapp_link(self, obj):
        return f"https://wa.me/{obj.phone.replace('+', '')}"
    
    def get_discount_info(self, obj):
        if obj.discount:
            return {
                'id': obj.discount.id,
                'name': obj.discount.name,
                'percentage': obj.discount.percentage
            }
        return None


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    subtotal = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'subtotal']
    
    def get_subtotal(self, obj):
        return obj.subtotal()


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    subscriber = serializers.SerializerMethodField()
    subscriber_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    total = serializers.SerializerMethodField()
    items_count = serializers.SerializerMethodField()
    session_id = serializers.ReadOnlyField()
    
    class Meta:
        model = Cart
        fields = [
            'id', 'session_id', 'subscriber', 'subscriber_id', 'created_at', 'is_active',
            'items', 'total', 'items_count'
        ]
    
    def get_subscriber(self, obj):
        # Retornar solo datos básicos del subscriber para evitar referencia circular
        if obj.subscriber:
            return {
                'id': obj.subscriber.id,
                'phone': obj.subscriber.phone,
                'email': obj.subscriber.email,
                'is_active': obj.subscriber.is_active
            }
        return None
    
    def get_total(self, obj):
        return obj.total()
    
    def get_items_count(self, obj):
        return obj.items.count()





# Serializers para operaciones específicas
class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)


class SubscribeSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    email = serializers.EmailField()

class SubscriberResponseSerializer(serializers.ModelSerializer):
    """Serializer simplificado para respuestas de suscripción"""
    subscription_status = serializers.SerializerMethodField()
    whatsapp_link = serializers.SerializerMethodField()
    
    class Meta:
        model = Subscriber
        fields = ['id', 'phone', 'email', 'is_active', 'subscription_status', 'whatsapp_link']
    
    def get_subscription_status(self, obj):
        return obj.subscription_status
    
    def get_whatsapp_link(self, obj):
        return f"https://wa.me/{obj.phone.replace('+', '')}"


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)
    session_id = serializers.CharField(required=False, allow_blank=True)





class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = ['id', 'name', 'percentage', 'is_active']
