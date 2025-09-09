from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from web.models import (
    Category, Subcategory, Product, ProductImage, Promotion, UsedPromotion, 
    Subscriber, Cart, CartItem, Discount
)
from .serializers import (
    CategorySerializer, CategoryTreeSerializer, SubcategorySerializer, ProductImageSerializer, ProductSerializer, PromotionSerializer,
    SubscriberSerializer, CartSerializer, CartItemSerializer, DiscountSerializer,
    SubscribeSerializer, AddToCartSerializer, UpdateCartItemSerializer
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para categorías - solo lectura
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    
    def get_queryset(self):
        queryset = Category.objects.filter(is_active=True)
        return queryset.order_by('order', 'name')
    
    @action(detail=True, methods=['get'])
    def products(self, request, slug=None):
        """Obtener productos de una categoría específica"""
        category = self.get_object()
        products = Product.objects.filter(category=category, is_active=True)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def subcategories(self, request, slug=None):
        """Obtener subcategorías de una categoría"""
        category = self.get_object()
        subcategories = category.subcategories.filter(is_active=True).order_by('order', 'name')
        serializer = SubcategorySerializer(subcategories, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Obtener árbol completo de categorías con subcategorías"""
        categories = Category.objects.filter(is_active=True).select_related().prefetch_related(
            'subcategories'
        ).order_by('order', 'name')
        serializer = CategoryTreeSerializer(categories, many=True)
        return Response(serializer.data)


class SubcategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para subcategorías - solo lectura
    """
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer
    lookup_field = 'slug'
    
    def get_queryset(self):
        queryset = Subcategory.objects.filter(is_active=True).select_related('category')
        
        # Filtrar por categoría
        category_slug = self.request.query_params.get('category', None)
        if category_slug:
            try:
                category = Category.objects.get(slug=category_slug, is_active=True)
                queryset = queryset.filter(category=category)
            except Category.DoesNotExist:
                queryset = Subcategory.objects.none()
        
        return queryset.order_by('order', 'name')
    
    @action(detail=True, methods=['get'])
    def products(self, request, slug=None):
        """Obtener productos de una subcategoría específica"""
        subcategory = self.get_object()
        products = Product.objects.filter(subcategory=subcategory, is_active=True)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class ProductImageViewSet(viewsets.ModelViewSet):
    """
    ViewSet para imágenes de productos
    """
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    
    def get_queryset(self):
        queryset = ProductImage.objects.all().select_related('product')
        
        # Filtrar por producto
        product_id = self.request.query_params.get('product', None)
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        # Filtrar solo imágenes principales
        main_only = self.request.query_params.get('main_only', None)
        if main_only == 'true':
            queryset = queryset.filter(is_main=True)
        
        return queryset.order_by('order', 'created_at')
    
    @action(detail=False, methods=['post'])
    def upload_multiple(self, request):
        """Subir múltiples imágenes para un producto"""
        product_id = request.data.get('product_id')
        images = request.FILES.getlist('images')
        
        if not product_id or not images:
            return Response(
                {'error': 'product_id and images are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            product = Product.objects.get(id=product_id)
            uploaded_images = []
            
            for i, image in enumerate(images):
                is_main = i == 0  # La primera imagen será la principal
                product_image = ProductImage.objects.create(
                    product=product,
                    image=image,
                    is_main=is_main,
                    order=i
                )
                uploaded_images.append(product_image)
            
            serializer = self.get_serializer(uploaded_images, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para productos - solo lectura
    """
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    lookup_field = 'slug'
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related(
            'category', 'subcategory'
        ).prefetch_related('images')
        
        # Filtros
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category__slug=category)
        
        subcategory = self.request.query_params.get('subcategory', None)
        if subcategory:
            queryset = queryset.filter(subcategory__slug=subcategory)
        
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        # Filtro por precio
        min_price = self.request.query_params.get('min_price', None)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        
        max_price = self.request.query_params.get('max_price', None)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Filtro por productos en oferta (por ahora filtramos por destacados)
        on_sale = self.request.query_params.get('on_sale', None)
        if on_sale == 'true':
            queryset = queryset.filter(is_featured=True)
        
        # Ordenamiento
        ordering = self.request.query_params.get('ordering', 'name')
        if ordering in ['name', 'price', '-name', '-price', 'created_at', '-created_at']:
            queryset = queryset.order_by(ordering)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Obtener productos destacados"""
        featured_products = Product.objects.filter(
            is_active=True,
            is_featured=True
        )
        serializer = self.get_serializer(featured_products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def on_sale(self, request):
        """Obtener productos en oferta (por ahora retorna productos destacados)"""
        # Por ahora retornamos productos destacados ya que no tenemos sistema de promociones por producto
        on_sale_products = Product.objects.filter(
            is_active=True,
            is_featured=True
        )
        serializer = self.get_serializer(on_sale_products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def new_arrivals(self, request):
        """Obtener productos nuevos (últimos 30 días)"""
        from datetime import timedelta
        thirty_days_ago = timezone.now() - timedelta(days=30)
        new_products = Product.objects.filter(
            is_active=True,
            created_at__gte=thirty_days_ago
        ).order_by('-created_at')
        serializer = self.get_serializer(new_products, many=True)
        return Response(serializer.data)





class PromotionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para promociones - solo lectura
    """
    queryset = Promotion.objects.filter(is_active=True)
    serializer_class = PromotionSerializer
    lookup_field = 'slug'





class SubscriberViewSet(viewsets.ModelViewSet):
    """
    ViewSet para suscriptores
    """
    queryset = Subscriber.objects.all()
    serializer_class = SubscriberSerializer
    
    def get_queryset(self):
        queryset = Subscriber.objects.filter(is_active=True).select_related('discount').prefetch_related(
            'carts__items__product__category',
            'carts__items__product__images'
        )
        
        # Filtrar por descuento
        discount_id = self.request.query_params.get('discount', None)
        if discount_id:
            queryset = queryset.filter(discount_id=discount_id)
        
        return queryset.order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def subscribe(self, request):
        """Suscripción con descuento del 5%"""
        phone = request.data.get('phone')
        email = request.data.get('email')
        
        if not phone or not email:
            return Response(
                {'error': 'Phone and email are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            subscriber, created = Subscriber.objects.get_or_create(
                phone=phone,
                defaults={
                    'email': email,
                    'is_active': True
                }
            )
            
            if not created:
                # Actualizar suscriptor si ya existe
                subscriber.email = email
                subscriber.save()
            
            # Crear descuento del 5% si no existe
            discount, _ = Discount.objects.get_or_create(
                name="Descuento Suscriptor",
                defaults={
                    'percentage': Decimal('5.00'),
                    'is_active': True
                }
            )
            
            # Asignar descuento al suscriptor
            subscriber.discount = discount
            subscriber.save()
            
            # Usar serializer simplificado para evitar referencias circulares
            from .serializers import SubscriberResponseSerializer
            subscriber_data = SubscriberResponseSerializer(subscriber).data
            return Response({
                'subscriber': subscriber_data,
                'subscription_active': True,
                'discount_percentage': 5,
                'message': '¡Felicidades! Tienes 5% de descuento en todos tus productos'
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class CartViewSet(viewsets.ModelViewSet):
    """
    ViewSet para carritos
    """
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    
    def get_queryset(self):
        queryset = Cart.objects.filter(is_active=True).select_related('subscriber').prefetch_related(
            'items__product__category',
            'items__product__images'
        )
        
        # Filtrar por suscriptor
        subscriber_id = self.request.query_params.get('subscriber', None)
        if subscriber_id:
            queryset = queryset.filter(subscriber_id=subscriber_id)
        
        # Filtrar por fecha
        date_from = self.request.query_params.get('date_from', None)
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        
        date_to = self.request.query_params.get('date_to', None)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        
        return queryset.order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Agregar producto al carrito (con o sin suscripción)"""
        serializer = AddToCartSerializer(data=request.data)
        if serializer.is_valid():
            product_id = serializer.validated_data['product_id']
            quantity = serializer.validated_data['quantity']
            session_id = serializer.validated_data.get('session_id')
            
            try:
                # Obtener producto
                product = get_object_or_404(Product, id=product_id, is_active=True)
                
                # Generar session_id si no existe
                if not session_id:
                    import uuid
                    session_id = str(uuid.uuid4())
                
                # Obtener o crear carrito
                cart, created = Cart.objects.get_or_create(
                    session_id=session_id,
                    is_active=True,
                    defaults={'is_active': True}
                )
                
                # Verificar si ya existe el item en el carrito
                cart_item, item_created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=product,
                    defaults={'quantity': quantity}
                )
                
                if not item_created:
                    cart_item.quantity += quantity
                    cart_item.save()
                
                # Serializar carrito actualizado
                cart_serializer = CartSerializer(cart)
                return Response({
                    'cart': cart_serializer.data,
                    'session_id': session_id,
                    'message': 'Producto agregado al carrito'
                })
                    
            except Exception as e:
                return Response(
                    {'error': str(e)}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def update_item(self, request, pk=None):
        """Actualizar cantidad de un item en el carrito (con ID del carrito)"""
        cart = self.get_object()
        serializer = UpdateCartItemSerializer(data=request.data)
        
        if serializer.is_valid():
            item_id = request.data.get('item_id')
            quantity = serializer.validated_data['quantity']
            
            try:
                cart_item = CartItem.objects.get(id=item_id, cart=cart)
                cart_item.quantity = quantity
                cart_item.save()
                
                # Eliminar item si cantidad es 0
                if quantity <= 0:
                    cart_item.delete()
                
                cart_serializer = CartSerializer(cart)
                return Response(cart_serializer.data)
                
            except CartItem.DoesNotExist:
                return Response(
                    {'error': 'Item not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def update_item_by_session(self, request):
        """Actualizar cantidad de un item en el carrito (por session_id)"""
        serializer = UpdateCartItemSerializer(data=request.data)
        
        if serializer.is_valid():
            session_id = request.data.get('session_id')
            item_id = request.data.get('item_id')
            quantity = serializer.validated_data['quantity']
            
            if not session_id:
                return Response(
                    {'error': 'session_id is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                cart = Cart.objects.get(session_id=session_id, is_active=True)
                cart_item = CartItem.objects.get(id=item_id, cart=cart)
                cart_item.quantity = quantity
                cart_item.save()
                
                # Eliminar item si cantidad es 0
                if quantity <= 0:
                    cart_item.delete()
                
                cart_serializer = CartSerializer(cart)
                return Response(cart_serializer.data)
                
            except Cart.DoesNotExist:
                return Response(
                    {'error': 'Cart not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            except CartItem.DoesNotExist:
                return Response(
                    {'error': 'Item not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def remove_item_by_session(self, request):
        """Remover item del carrito (por session_id)"""
        session_id = request.data.get('session_id')
        item_id = request.data.get('item_id')
        
        if not session_id:
            return Response(
                {'error': 'session_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            cart = Cart.objects.get(session_id=session_id, is_active=True)
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            cart_item.delete()
            
            cart_serializer = CartSerializer(cart)
            return Response(cart_serializer.data)
            
        except Cart.DoesNotExist:
            return Response(
                {'error': 'Cart not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Item not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def remove_item(self, request, pk=None):
        """Remover item del carrito"""
        cart = self.get_object()
        item_id = request.data.get('item_id')
        
        try:
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            cart_item.delete()
            
            cart_serializer = CartSerializer(cart)
            return Response(cart_serializer.data)
            
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Item not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def clear(self, request, pk=None):
        """Vaciar carrito (con ID del carrito)"""
        cart = self.get_object()
        cart.items.all().delete()
        
        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data)
    
    @action(detail=False, methods=['post'])
    def clear_by_session(self, request):
        """Vaciar carrito (por session_id)"""
        session_id = request.data.get('session_id')
        
        if not session_id:
            return Response(
                {'error': 'session_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            cart = Cart.objects.get(session_id=session_id, is_active=True)
            cart.items.all().delete()
            
            cart_serializer = CartSerializer(cart)
            return Response(cart_serializer.data)
            
        except Cart.DoesNotExist:
            return Response(
                {'error': 'Cart not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def link_to_subscriber(self, request):
        """Vincular carrito a un suscriptor"""
        session_id = request.data.get('session_id')
        phone = request.data.get('phone')
        
        if not session_id or not phone:
            return Response(
                {'error': 'session_id and phone are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            cart = get_object_or_404(Cart, session_id=session_id, is_active=True)
            subscriber = get_object_or_404(Subscriber, phone=phone, is_active=True)
            
            # Vincular carrito al suscriptor
            cart.subscriber = subscriber
            cart.save()
            
            # Aplicar descuento si el suscriptor tiene uno
            if subscriber.discount:
                discount_amount = cart.get_discount_amount(subscriber.discount.percentage / 100)
                cart_serializer = CartSerializer(cart)
                return Response({
                    'cart': cart_serializer.data,
                    'discount_applied': True,
                    'discount_percentage': subscriber.discount.percentage,
                    'discount_amount': discount_amount,
                    'total_with_discount': cart.apply_subscriber_discount(subscriber.discount.percentage / 100),
                    'message': f'Carrito vinculado y descuento del {subscriber.discount.percentage}% aplicado'
                })
            
            cart_serializer = CartSerializer(cart)
            return Response({
                'cart': cart_serializer.data,
                'discount_applied': False,
                'message': 'Carrito vinculado al suscriptor'
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )


# OrderViewSet ya no es necesario porque no manejamos órdenes
# Todo se maneja a través del carrito y WhatsApp


class CartItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet para items del carrito
    """
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    
    def get_queryset(self):
        queryset = CartItem.objects.all().select_related(
            'cart', 'product__category', 'product__subcategory'
        ).prefetch_related('product__images')
        
        # Filtrar por carrito
        cart_id = self.request.query_params.get('cart', None)
        if cart_id:
            queryset = queryset.filter(cart_id=cart_id)
        
        # Filtrar por producto
        product_id = self.request.query_params.get('product', None)
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        return queryset.order_by('-created_at')


class DiscountViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para descuentos - solo lectura
    """
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    
    def get_queryset(self):
        return Discount.objects.filter(is_active=True)


# Vista para obtener estadísticas generales
class DashboardView(APIView):
    """
    Vista para obtener estadísticas del dashboard
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        today = timezone.now().date()
        
        # Usar anotaciones para evitar múltiples queries
        from django.db.models import Count, Q
        
        stats = {
            'total_products': Product.objects.filter(is_active=True).count(),
            'total_categories': Category.objects.count(),
            'active_promotions': Promotion.objects.filter(is_active=True).count(),
            'total_subscribers': Subscriber.objects.filter(is_active=True).count(),
            'active_carts': Cart.objects.filter(is_active=True).count(),
            'carts_today': Cart.objects.filter(
                created_at__date=today
            ).count(),
            'products_by_category': Category.objects.filter(is_active=True).annotate(
                products_count=Count('products', filter=Q(products__is_active=True))
            ).values('name', 'products_count')[:5],
        }
        
        return Response(stats)
