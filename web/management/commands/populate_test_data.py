from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from web.models import Category, Subcategory, Product, ProductImage, Promotion, Subscriber, Cart, CartItem, Discount
from django.core.files.base import ContentFile
import os


class Command(BaseCommand):
    help = 'Populate database with test data for ecommerce'

    def handle(self, *args, **options):
        self.stdout.write('Creating test data...')
        
        # Clear existing data
        self.stdout.write('Clearing existing data...')
        CartItem.objects.all().delete()
        Cart.objects.all().delete()
        Subscriber.objects.all().delete()
        ProductImage.objects.all().delete()
        Product.objects.all().delete()
        Promotion.objects.all().delete()
        Subcategory.objects.all().delete()
        Category.objects.all().delete()
        Discount.objects.all().delete()
        
        # Create Categories
        self.stdout.write('Creating categories...')
        electronics = Category.objects.create(
            name="Electrónicos",
            slug="electronicos",
            is_active=True,
            order=1
        )
        
        clothing = Category.objects.create(
            name="Ropa",
            slug="ropa",
            is_active=True,
            order=2
        )
        
        home = Category.objects.create(
            name="Hogar",
            slug="hogar",
            is_active=True,
            order=3
        )
        
        sports = Category.objects.create(
            name="Deportes",
            slug="deportes",
            is_active=True,
            order=4
        )
        
        # Create Subcategories
        self.stdout.write('Creating subcategories...')
        
        # Electronics subcategories
        smartphones = Subcategory.objects.create(
            name="Smartphones",
            slug="smartphones",
            category=electronics,
            is_active=True,
            order=1
        )
        
        laptops = Subcategory.objects.create(
            name="Laptops",
            slug="laptops",
            category=electronics,
            is_active=True,
            order=2
        )
        
        tablets = Subcategory.objects.create(
            name="Tablets",
            slug="tablets",
            category=electronics,
            is_active=True,
            order=3
        )
        
        # Clothing subcategories
        shirts = Subcategory.objects.create(
            name="Camisetas",
            slug="camisetas",
            category=clothing,
            is_active=True,
            order=1
        )
        
        pants = Subcategory.objects.create(
            name="Pantalones",
            slug="pantalones",
            category=clothing,
            is_active=True,
            order=2
        )
        
        shoes = Subcategory.objects.create(
            name="Zapatos",
            slug="zapatos",
            category=clothing,
            is_active=True,
            order=3
        )
        
        # Home subcategories
        furniture = Subcategory.objects.create(
            name="Muebles",
            slug="muebles",
            category=home,
            is_active=True,
            order=1
        )
        
        kitchen = Subcategory.objects.create(
            name="Cocina",
            slug="cocina",
            category=home,
            is_active=True,
            order=2
        )
        
        # Sports subcategories
        fitness = Subcategory.objects.create(
            name="Fitness",
            slug="fitness",
            category=sports,
            is_active=True,
            order=1
        )
        
        outdoor = Subcategory.objects.create(
            name="Aire Libre",
            slug="aire-libre",
            category=sports,
            is_active=True,
            order=2
        )
        
        # Create Products
        self.stdout.write('Creating products...')
        
        # Smartphones
        iphone = Product.objects.create(
            name="iPhone 15 Pro",
            slug="iphone-15-pro",
            description="El último iPhone con características avanzadas, cámara profesional y rendimiento excepcional.",
            price=Decimal("1299.99"),
            stock=15,
            sku="IPH15PRO-128",
            category=electronics,
            subcategory=smartphones,
            is_active=True,
            is_featured=True
        )
        
        samsung = Product.objects.create(
            name="Samsung Galaxy S24",
            slug="samsung-galaxy-s24",
            description="Smartphone Android de última generación con IA integrada y cámara versátil.",
            price=Decimal("999.99"),
            stock=12,
            sku="SAMS24-256",
            category=electronics,
            subcategory=smartphones,
            is_active=True,
            is_featured=False
        )
        
        # Laptops
        macbook = Product.objects.create(
            name="MacBook Pro M3",
            slug="macbook-pro-m3",
            description="Laptop profesional con chip M3, perfecta para desarrollo y diseño.",
            price=Decimal("2499.99"),
            stock=8,
            sku="MBP-M3-512",
            category=electronics,
            subcategory=laptops,
            is_active=True,
            is_featured=True
        )
        
        dell = Product.objects.create(
            name="Dell XPS 13",
            slug="dell-xps-13",
            description="Laptop ultrabook con pantalla InfinityEdge y rendimiento excepcional.",
            price=Decimal("1299.99"),
            stock=10,
            sku="DELL-XPS13-512",
            category=electronics,
            subcategory=laptops,
            is_active=True,
            is_featured=False
        )
        
        # Tablets
        ipad = Product.objects.create(
            name="iPad Pro 12.9",
            slug="ipad-pro-12-9",
            description="Tablet profesional con pantalla Liquid Retina XDR y chip M2.",
            price=Decimal("1099.99"),
            stock=6,
            sku="IPAD-PRO-256",
            category=electronics,
            subcategory=tablets,
            is_active=True,
            is_featured=False
        )
        
        # Clothing
        tshirt = Product.objects.create(
            name="Camiseta Básica",
            slug="camiseta-basica",
            description="Camiseta 100% algodón, cómoda y versátil para cualquier ocasión.",
            price=Decimal("19.99"),
            stock=50,
            sku="TSHIRT-BASIC-M",
            category=clothing,
            subcategory=shirts,
            is_active=True,
            is_featured=False
        )
        
        jeans = Product.objects.create(
            name="Jeans Clásicos",
            slug="jeans-clasicos",
            description="Jeans de alta calidad con ajuste perfecto y durabilidad excepcional.",
            price=Decimal("79.99"),
            stock=30,
            sku="JEANS-CLASSIC-32",
            category=clothing,
            subcategory=pants,
            is_active=True,
            is_featured=False
        )
        
        sneakers = Product.objects.create(
            name="Sneakers Deportivos",
            slug="sneakers-deportivos",
            description="Zapatos deportivos cómodos y elegantes para uso diario.",
            price=Decimal("89.99"),
            stock=25,
            sku="SNEAKERS-SPORT-42",
            category=clothing,
            subcategory=shoes,
            is_active=True,
            is_featured=False
        )
        
        # Home
        sofa = Product.objects.create(
            name="Sofá Moderno",
            slug="sofa-moderno",
            description="Sofá elegante y cómodo, perfecto para tu sala de estar.",
            price=Decimal("599.99"),
            stock=5,
            sku="SOFA-MODERN-3S",
            category=home,
            subcategory=furniture,
            is_active=True,
            is_featured=False
        )
        
        blender = Product.objects.create(
            name="Licuadora Profesional",
            slug="licuadora-profesional",
            description="Licuadora de alta potencia para preparar batidos y jugos saludables.",
            price=Decimal("129.99"),
            stock=15,
            sku="BLENDER-PRO-1000W",
            category=home,
            subcategory=kitchen,
            is_active=True,
            is_featured=False
        )
        
        # Sports
        dumbbells = Product.objects.create(
            name="Set de Mancuernas",
            slug="set-mancuernas",
            description="Set completo de mancuernas para entrenamiento en casa.",
            price=Decimal("149.99"),
            stock=20,
            sku="DUMBBELLS-SET-20KG",
            category=sports,
            subcategory=fitness,
            is_active=True,
            is_featured=False
        )
        
        tent = Product.objects.create(
            name="Tienda de Campaña",
            slug="tienda-campana",
            description="Tienda de campaña resistente para 4 personas, perfecta para aventuras.",
            price=Decimal("199.99"),
            stock=8,
            sku="TENT-4P-CAMPING",
            category=sports,
            subcategory=outdoor,
            is_active=True,
            is_featured=False
        )
        
        # Create Promotions
        self.stdout.write('Creating promotions...')
        
        black_friday = Promotion.objects.create(
            name="Black Friday",
            slug="black-friday",
            discount=Decimal("100.00"),
            is_active=True
        )
        
        summer_sale = Promotion.objects.create(
            name="Oferta de Verano",
            slug="oferta-verano",
            discount=Decimal("50.00"),
            is_active=True
        )
        
        # Create UsedPromotions (for tracking promotions used by subscribers)
        from datetime import date, timedelta
        
        # Black Friday promotion tracking
        black_friday_start = date.today()
        black_friday_end = date.today() + timedelta(days=30)
        
        # Summer sale promotion tracking
        summer_sale_start = date.today()
        summer_sale_end = date.today() + timedelta(days=60)
        
        # Create Discount
        self.stdout.write('Creating discount...')
        
        discount = Discount.objects.create(
            name="Suscripción Premium",
            percentage=Decimal("5.0"),
            is_active=True
        )
        
        # Create Subscribers
        self.stdout.write('Creating subscribers...')
        
        subscriber1 = Subscriber.objects.create(
            phone="+525512345678",
            email="juan.perez@email.com",
            is_active=True,
            discount=discount
        )
        
        subscriber2 = Subscriber.objects.create(
            phone="+525598765432",
            email="maria.garcia@email.com",
            is_active=True,
            discount=discount
        )
        
        # Create Carts
        self.stdout.write('Creating carts...')
        
        cart1 = Cart.objects.create(
            session_id="session_123",
            subscriber=subscriber1,
            is_active=True
        )
        
        cart2 = Cart.objects.create(
            session_id="session_456",
            subscriber=subscriber2,
            is_active=True
        )
        
        # Create Cart Items
        CartItem.objects.create(
            cart=cart1,
            product=iphone,
            quantity=1
        )
        
        CartItem.objects.create(
            cart=cart1,
            product=tshirt,
            quantity=2
        )
        
        CartItem.objects.create(
            cart=cart2,
            product=macbook,
            quantity=1
        )
        
        CartItem.objects.create(
            cart=cart2,
            product=jeans,
            quantity=1
        )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created test data!')
        )
        
        # Print summary
        self.stdout.write('\n=== SUMMARY ===')
        self.stdout.write(f'Categories: {Category.objects.count()}')
        self.stdout.write(f'Subcategories: {Subcategory.objects.count()}')
        self.stdout.write(f'Products: {Product.objects.count()}')
        self.stdout.write(f'Promotions: {Promotion.objects.count()}')
        self.stdout.write(f'Discounts: {Discount.objects.count()}')
        self.stdout.write(f'Subscribers: {Subscriber.objects.count()}')
        self.stdout.write(f'Active Carts: {Cart.objects.filter(is_active=True).count()}')
        
        self.stdout.write('\n=== API ENDPOINTS TO TEST ===')
        self.stdout.write('GET /api/categories/')
        self.stdout.write('GET /api/products/')
        self.stdout.write('GET /api/products/featured/')
        self.stdout.write('GET /api/products/on-sale/')
        self.stdout.write('GET /api/customers/')
        self.stdout.write('GET /api/orders/')
