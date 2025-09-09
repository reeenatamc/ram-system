from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Crear router para ViewSets
router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'subcategories', views.SubcategoryViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'product-images', views.ProductImageViewSet)
router.register(r'promotions', views.PromotionViewSet)
router.register(r'subscribers', views.SubscriberViewSet)
router.register(r'carts', views.CartViewSet)
router.register(r'cart-items', views.CartItemViewSet)
router.register(r'discounts', views.DiscountViewSet)

# URLs de la API
urlpatterns = [
    # Dashboard y estadísticas
    path('dashboard/', views.DashboardView.as_view(), name='api-dashboard'),
    
    # URLs adicionales para funcionalidades específicas
    path('products/featured/', views.ProductViewSet.as_view({'get': 'featured'}), name='featured-products'),
    path('products/on-sale/', views.ProductViewSet.as_view({'get': 'on_sale'}), name='on-sale-products'),
    path('products/new-arrivals/', views.ProductViewSet.as_view({'get': 'new_arrivals'}), name='new-arrivals'),
    
    # URLs para categorías
    path('categories/tree/', views.CategoryViewSet.as_view({'get': 'tree'}), name='category-tree'),
    
    # URLs para carrito
    path('carts/add-item/', views.CartViewSet.as_view({'post': 'add_item'}), name='add-to-cart'),
    path('carts/update-item/', views.CartViewSet.as_view({'post': 'update_item_by_session'}), name='update-cart-item'),
    path('carts/remove-item/', views.CartViewSet.as_view({'post': 'remove_item_by_session'}), name='remove-cart-item'),
    path('carts/clear/', views.CartViewSet.as_view({'post': 'clear_by_session'}), name='clear-cart'),
    path('carts/link-to-subscriber/', views.CartViewSet.as_view({'post': 'link_to_subscriber'}), name='link-cart-to-subscriber'),
    
    # URLs para suscriptores
    path('subscribers/subscribe/', views.SubscriberViewSet.as_view({'post': 'subscribe'}), name='subscriber-subscribe'),
    
    # URLs para imágenes de productos
    path('product-images/upload-multiple/', views.ProductImageViewSet.as_view({'post': 'upload_multiple'}), name='upload-multiple-images'),
    
    # Incluir URLs del router (al final para evitar conflictos)
    path('', include(router.urls)),
]
