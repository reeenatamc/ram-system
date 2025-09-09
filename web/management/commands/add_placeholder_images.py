from django.core.management.base import BaseCommand
from web.models import Product, ProductImage
from django.core.files.base import ContentFile
import requests
from io import BytesIO


class Command(BaseCommand):
    help = 'Add placeholder images to products'

    def handle(self, *args, **options):
        self.stdout.write('Adding placeholder images to products...')
        
        # Placeholder image URLs for different categories
        placeholder_images = {
            'electronicos': [
                'https://via.placeholder.com/400x400/007AFF/FFFFFF?text=Smartphone',
                'https://via.placeholder.com/400x400/34C759/FFFFFF?text=Laptop',
                'https://via.placeholder.com/400x400/FF9500/FFFFFF?text=Tablet',
            ],
            'ropa': [
                'https://via.placeholder.com/400x400/FF2D92/FFFFFF?text=Camiseta',
                'https://via.placeholder.com/400x400/5856D6/FFFFFF?text=Pantalones',
                'https://via.placeholder.com/400x400/FF3B30/FFFFFF?text=Zapatos',
            ],
            'hogar': [
                'https://via.placeholder.com/400x400/8E8E93/FFFFFF?text=Muebles',
                'https://via.placeholder.com/400x400/FF9500/FFFFFF?text=Cocina',
            ],
            'deportes': [
                'https://via.placeholder.com/400x400/34C759/FFFFFF?text=Fitness',
                'https://via.placeholder.com/400x400/007AFF/FFFFFF?text=Aire+Libre',
            ]
        }
        
        products = Product.objects.all()
        
        for i, product in enumerate(products):
            # Skip if product already has images
            if product.images.exists():
                continue
                
            category_slug = product.category.slug
            image_urls = placeholder_images.get(category_slug, placeholder_images['electronicos'])
            
            # Use different image based on product index
            image_url = image_urls[i % len(image_urls)]
            
            try:
                # Download placeholder image
                response = requests.get(image_url)
                if response.status_code == 200:
                    # Create ProductImage
                    image_file = ContentFile(response.content, name=f'{product.slug}_placeholder.jpg')
                    ProductImage.objects.create(
                        product=product,
                        image=image_file,
                        is_main=True,
                        order=0
                    )
                    self.stdout.write(f'Added image to {product.name}')
                else:
                    self.stdout.write(f'Failed to download image for {product.name}')
                    
            except Exception as e:
                self.stdout.write(f'Error adding image to {product.name}: {str(e)}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully added placeholder images!')
        )
        
        # Print summary
        products_with_images = Product.objects.filter(images__isnull=False).distinct().count()
        total_products = Product.objects.count()
        
        self.stdout.write(f'\nProducts with images: {products_with_images}/{total_products}')
