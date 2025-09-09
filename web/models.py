from django.db import models
from django.template.defaultfilters import slugify
from django.core.exceptions import ValidationError


# --- Modelos de Categorías y Productos ---


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    slug = models.SlugField(max_length=100, unique=True, blank=True, verbose_name="Slug")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    order = models.PositiveIntegerField(default=0, verbose_name="Orden")
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        indexes = [
            models.Index(fields=['is_active', 'order']),
            models.Index(fields=['slug']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'


class Subcategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre")
    slug = models.SlugField(max_length=100, blank=True, verbose_name="Slug")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories', verbose_name="Categoría")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    order = models.PositiveIntegerField(default=0, verbose_name="Orden")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.category.name} > {self.name}"

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Subcategoría'
        verbose_name_plural = 'Subcategorías'
        indexes = [
            models.Index(fields=['category', 'is_active', 'order']),
            models.Index(fields=['slug']),
        ]


class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre")
    slug = models.SlugField(max_length=100, unique=True, blank=True, verbose_name="Slug")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock")
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name="SKU")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products", verbose_name="Categoría")
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, related_name="products", null=True, blank=True, verbose_name="Subcategoría")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    is_featured = models.BooleanField(default=False, verbose_name="Destacado")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    @property
    def is_in_stock(self):
        """Verifica si el producto tiene stock disponible"""
        return self.stock > 0
    
    @property
    def stock_status(self):
        """Retorna el estado del stock"""
        if self.stock == 0:
            return "Sin stock"
        elif self.stock <= 5:
            return "Stock bajo"
        else:
            return "En stock"
    
    @property
    def main_image(self):
        """Retorna la imagen principal del producto"""
        # Cache local para evitar múltiples queries
        if not hasattr(self, '_main_image_cache'):
            main_image = self.images.filter(is_main=True).first()
            if not main_image:
                # Si no hay imagen principal, tomar la primera disponible
                main_image = self.images.first()
            self._main_image_cache = main_image
        return self._main_image_cache
    
    def clear_cache(self):
        """Limpia el cache local del producto"""
        if hasattr(self, '_main_image_cache'):
            delattr(self, '_main_image_cache')

    class Meta:
        ordering = ['name']
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        indexes = [
            models.Index(fields=['is_active', 'is_featured']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['subcategory', 'is_active']),
            models.Index(fields=['slug']),
            models.Index(fields=['sku']),
        ]


class ProductImage(models.Model):
    """Modelo para imágenes de productos"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name="Producto")
    image = models.ImageField(upload_to='products/', verbose_name="Imagen")
    is_main = models.BooleanField(default=False, verbose_name="Imagen principal")
    order = models.PositiveIntegerField(default=0, verbose_name="Orden")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")

    def save(self, *args, **kwargs):
        # Si esta imagen es principal, desactivar otras principales del mismo producto
        if self.is_main:
            ProductImage.objects.filter(product=self.product, is_main=True).update(is_main=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Imagen de {self.product.name}"

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = 'Imagen de producto'
        verbose_name_plural = 'Imágenes de productos'
        indexes = [
            models.Index(fields=['product', 'is_main']),
            models.Index(fields=['product', 'order']),
        ]


# --- Modelo de Promociones y control de uso ---
class Promotion(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre de la promoción")
    slug = models.SlugField(max_length=100, unique=True, blank=True, verbose_name="Slug")
    discount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Descuento (%)")  # Descuento en porcentaje
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    class Meta:
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['slug']),
        ]


class UsedPromotion(models.Model):
    subscriber = models.ForeignKey('Subscriber', on_delete=models.CASCADE, related_name="used_promotions")
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, verbose_name="Promoción")
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE, verbose_name="Carrito")
    applied_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de uso")

    def __str__(self):
        return f"Promoción {self.promotion.name} usada por {self.subscriber.phone} en el carrito {self.cart.session_id}"

    class Meta:
        unique_together = ['subscriber', 'promotion']  # Garantiza que la misma promoción no se use más de una vez
        indexes = [
            models.Index(fields=['subscriber', 'promotion']),
            models.Index(fields=['cart']),
        ]


# --- Modelo de Suscriptores ---
class Subscriber(models.Model):
    phone = models.CharField(max_length=20, unique=True, verbose_name="Teléfono")  # Teléfono de WhatsApp
    email = models.EmailField(verbose_name="Correo electrónico")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    discount = models.ForeignKey('Discount', null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Descuento aplicable")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    def __str__(self):
        return f"Suscriptor {self.phone}"

    def has_used_promotion(self, promotion):
        """Verifica si el suscriptor ya usó esta promoción"""
        return UsedPromotion.objects.filter(subscriber=self, promotion=promotion).exists()
    
    @property
    def total_carts(self):
        """Retorna el total de carritos del suscriptor"""
        return self.carts.count()
    
    @property
    def subscription_status(self):
        """Retorna el estado de la suscripción"""
        if self.discount:
            return "Activa"
        return "Inactiva"
    
    class Meta:
        indexes = [
            models.Index(fields=['phone']),
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
        ]


# --- Modelo de Carrito y Carrito de Productos ---
class Cart(models.Model):
    session_id = models.CharField(max_length=100, unique=True, verbose_name="ID de Sesión")  # Identificador único para carritos anónimos
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE, related_name="carts", null=True, blank=True, verbose_name="Suscriptor")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    
    def __str__(self):
        return f"Carrito {self.session_id}"

    def total(self):
        """Calcula el total del carrito"""
        # Cache local para evitar múltiples cálculos
        if not hasattr(self, '_total_cache'):
            self._total_cache = sum(item.subtotal() for item in self.items.all())
        return self._total_cache

    def is_empty(self):
        """Verifica si el carrito está vacío"""
        # Cache local para evitar múltiples queries
        if not hasattr(self, '_is_empty_cache'):
            self._is_empty_cache = self.items.count() == 0
        return self._is_empty_cache
    
    def clear_cache(self):
        """Limpia el cache local del carrito"""
        if hasattr(self, '_total_cache'):
            delattr(self, '_total_cache')
        if hasattr(self, '_is_empty_cache'):
            delattr(self, '_is_empty_cache')
    
    class Meta:
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['subscriber', 'is_active']),
            models.Index(fields=['is_active', 'created_at']),
        ]


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items", verbose_name="Carrito")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Producto")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Cantidad")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")

    def subtotal(self):
        return self.product.price * self.quantity
    
    def clean(self):
        """Validar que no se exceda el stock disponible"""
        if self.quantity > self.product.stock:
            raise ValidationError(f'No hay suficiente stock. Disponible: {self.product.stock}')
    
    def save(self, *args, **kwargs):
        self.clean()
        # Limpiar cache del carrito cuando se modifica un item
        if self.pk:  # Si ya existe
            old_instance = CartItem.objects.get(pk=self.pk)
            if old_instance.cart:
                old_instance.cart.clear_cache()
        
        super().save(*args, **kwargs)
        
        # Limpiar cache del carrito actual
        if self.cart:
            self.cart.clear_cache()
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name}"
    
    def delete(self, *args, **kwargs):
        # Limpiar cache del carrito antes de eliminar
        if self.cart:
            self.cart.clear_cache()
        super().delete(*args, **kwargs)
    
    class Meta:
        unique_together = ['cart', 'product']  # Un producto por carrito
        indexes = [
            models.Index(fields=['cart', 'product']),
        ]


# --- Función para aplicar el descuento de la promoción ---
def apply_discount_to_cart(subscriber, cart, promotion):
    # Verificar si el suscriptor ya utilizó esta promoción
    if UsedPromotion.objects.filter(subscriber=subscriber, promotion=promotion).exists():
        raise ValidationError(f"Ya has utilizado esta promoción anteriormente.")
    
    # Calcular el descuento
    discount_percentage = promotion.discount
    cart_total = cart.total()
    discounted_total = cart_total - (cart_total * (discount_percentage / 100))

    # Registrar que la promoción fue utilizada
    UsedPromotion.objects.create(subscriber=subscriber, promotion=promotion, cart=cart)

    # Actualizar el carrito con el nuevo precio (esto se puede usar para aplicar cambios en la base de datos)
    return discounted_total


# --- Modelo para descuentos de suscripción (si deseas aplicar un descuento global) ---
class Discount(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre del descuento")
    percentage = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Porcentaje de descuento")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    
    def __str__(self):
        return self.name
