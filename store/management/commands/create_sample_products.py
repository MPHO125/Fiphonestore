from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from store.models import iPhoneModel, Color, iPhoneProduct
from io import BytesIO
from PIL import Image, ImageDraw
import random

class Command(BaseCommand):
    help = 'Create sample iPhone products with cover photos'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample iPhone products with cover photos...')
        
        # Get or create models and colors
        models = iPhoneModel.objects.all()
        colors = Color.objects.all()
        
        if not models or not colors:
            self.stdout.write('Please run "python manage.py populate_iphones" first to create models and colors.')
            return
        
        # Sample product data
        sample_products = [
            {
                'model_name': 'iPhone 15 Pro',
                'color_name': 'Titanium',
                'storage': '256GB',
                'condition': 'new',
                'price': 1199.99,
                'stock': 10
            },
            {
                'model_name': 'iPhone 15',
                'color_name': 'Blue',
                'storage': '128GB',
                'condition': 'new',
                'price': 999.99,
                'stock': 15
            },
            {
                'model_name': 'iPhone 14 Pro',
                'color_name': 'Space Black',
                'storage': '512GB',
                'condition': 'new',
                'price': 1099.99,
                'stock': 8
            }
        ]
        
        created_count = 0
        for product_data in sample_products:
            try:
                # Get model and color
                model = models.filter(name=product_data['model_name']).first()
                color = colors.filter(name=product_data['color_name']).first()
                
                if not model or not color:
                    continue
                
                # Check if product already exists
                existing = iPhoneProduct.objects.filter(
                    iphone_model=model,
                    color=color,
                    storage=product_data['storage'],
                    condition=product_data['condition']
                ).first()
                
                if existing:
                    self.stdout.write(f'Product {model.name} {color.name} {product_data["storage"]} already exists')
                    continue
                
                # Create product
                product = iPhoneProduct.objects.create(
                    iphone_model=model,
                    color=color,
                    storage=product_data['storage'],
                    condition=product_data['condition'],
                    price=product_data['price'],
                    stock_quantity=product_data['stock']
                )
                
                # Create a simple cover photo
                self.create_sample_cover_photo(product, model.name, color.name)
                
                created_count += 1
                self.stdout.write(f'Created: {model.name} {color.name} {product_data["storage"]}')
                
            except Exception as e:
                self.stdout.write(f'Error creating product: {e}')
        
        self.stdout.write(f'Successfully created {created_count} sample products with cover photos!')

    def create_sample_cover_photo(self, product, model_name, color_name):
        """Create a simple colored cover photo for the product"""
        try:
            # Create a simple image with the color
            img = Image.new('RGB', (800, 600), color=self.get_color_for_name(color_name))
            
            # Add some text to make it look like a product image
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(img)
            
            # Add model name
            try:
                font = ImageFont.truetype("arial.ttf", 40)
                text_bbox = draw.textbbox((0, 0), model_name, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_x = (800 - text_width) // 2
                
                draw.text((text_x, 200), model_name, fill='white', font=font)
            except:
                # Fallback if font not available
                draw.text((400, 200), model_name, fill='white')
            
            # Add iPhone silhouette (simple rectangle)
            draw.rectangle([300, 300, 500, 450], fill='white', outline='gray')
            
            # Save to BytesIO
            img_io = BytesIO()
            img.save(img_io, format='JPEG', quality=85)
            img_io.seek(0)
            
            # Save to product
            filename = f'{model_name}_{color_name}_cover.jpg'
            product.cover_photo.save(filename, ContentFile(img_io.read(), name=filename), save=True)
            
        except Exception as e:
            self.stdout.write(f'Could not create cover photo for {model_name}: {e}')
    
    def get_color_for_name(self, color_name):
        """Get RGB color for common color names"""
        color_map = {
            'Black': (0, 0, 0),
            'White': (255, 255, 255),
            'Blue': (0, 122, 255),
            'Red': (255, 0, 0),
            'Green': (0, 255, 0),
            'Yellow': (255, 255, 0),
            'Purple': (128, 0, 128),
            'Pink': (255, 192, 203),
            'Orange': (255, 165, 0),
            'Gray': (128, 128, 128),
            'Silver': (192, 192, 192),
            'Gold': (255, 215, 0),
            'Space Black': (10, 10, 10),
            'Titanium': (158, 158, 158),
            'Sierra Blue': (72, 61, 139),
            'Midnight Green': (0, 51, 25),
            'Starlight': (255, 255, 200),
        }
        return color_map.get(color_name, (100, 100, 100))
