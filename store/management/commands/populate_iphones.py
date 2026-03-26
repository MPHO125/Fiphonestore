from django.core.management.base import BaseCommand
from django.db import transaction
from store.models import iPhoneModel, Color, iPhoneProduct
import random

class Command(BaseCommand):
    help = 'Populate the database with iPhone models and sample products'

    def handle(self, *args, **options):
        with transaction.atomic():
            self.stdout.write('Creating iPhone models...')
            self.create_iphone_models()
            
            self.stdout.write('Creating colors...')
            self.create_colors()
            
            self.stdout.write('Creating sample products...')
            self.create_sample_products()
            
            self.stdout.write(self.style.SUCCESS('Successfully populated iPhone data!'))

    def create_iphone_models(self):
        iphone_data = [
            # iPhone 6 series
            ('iPhone 6', 2014, '4.7 inches', '16GB, 32GB, 64GB, 128GB'),
            ('iPhone 6 Plus', 2014, '5.5 inches', '16GB, 32GB, 64GB, 128GB'),
            ('iPhone 6s', 2015, '4.7 inches', '16GB, 32GB, 64GB, 128GB'),
            ('iPhone 6s Plus', 2015, '5.5 inches', '16GB, 32GB, 64GB, 128GB'),
            ('iPhone SE (1st gen)', 2016, '4.0 inches', '16GB, 32GB, 64GB'),
            
            # iPhone 7 series
            ('iPhone 7', 2016, '4.7 inches', '32GB, 128GB, 256GB'),
            ('iPhone 7 Plus', 2016, '5.5 inches', '32GB, 128GB, 256GB'),
            
            # iPhone 8 series
            ('iPhone 8', 2017, '4.7 inches', '64GB, 256GB'),
            ('iPhone 8 Plus', 2017, '5.5 inches', '64GB, 256GB'),
            ('iPhone X', 2017, '5.8 inches', '64GB, 256GB'),
            
            # iPhone XR/XS series
            ('iPhone XR', 2018, '6.1 inches', '64GB, 128GB, 256GB'),
            ('iPhone XS', 2018, '5.8 inches', '64GB, 256GB, 512GB'),
            ('iPhone XS Max', 2018, '6.5 inches', '64GB, 256GB, 512GB'),
            
            # iPhone 11 series
            ('iPhone 11', 2019, '6.1 inches', '64GB, 128GB, 256GB'),
            ('iPhone 11 Pro', 2019, '5.8 inches', '64GB, 256GB, 512GB'),
            ('iPhone 11 Pro Max', 2019, '6.5 inches', '64GB, 256GB, 512GB'),
            ('iPhone SE (2nd gen)', 2020, '4.7 inches', '64GB, 128GB, 256GB'),
            
            # iPhone 12 series
            ('iPhone 12 mini', 2020, '5.4 inches', '64GB, 128GB, 256GB'),
            ('iPhone 12', 2020, '6.1 inches', '64GB, 128GB, 256GB'),
            ('iPhone 12 Pro', 2020, '6.1 inches', '128GB, 256GB, 512GB'),
            ('iPhone 12 Pro Max', 2020, '6.7 inches', '128GB, 256GB, 512GB'),
            
            # iPhone 13 series
            ('iPhone 13 mini', 2021, '5.4 inches', '128GB, 256GB, 512GB'),
            ('iPhone 13', 2021, '6.1 inches', '128GB, 256GB, 512GB'),
            ('iPhone 13 Pro', 2021, '6.1 inches', '128GB, 256GB, 512GB, 1TB'),
            ('iPhone 13 Pro Max', 2021, '6.7 inches', '128GB, 256GB, 512GB, 1TB'),
            ('iPhone SE (3rd gen)', 2022, '4.7 inches', '64GB, 128GB, 256GB'),
            
            # iPhone 14 series
            ('iPhone 14', 2022, '6.1 inches', '128GB, 256GB, 512GB'),
            ('iPhone 14 Plus', 2022, '6.7 inches', '128GB, 256GB, 512GB'),
            ('iPhone 14 Pro', 2022, '6.1 inches', '128GB, 256GB, 512GB, 1TB'),
            ('iPhone 14 Pro Max', 2022, '6.7 inches', '128GB, 256GB, 512GB, 1TB'),
            
            # iPhone 15 series
            ('iPhone 15', 2023, '6.1 inches', '128GB, 256GB, 512GB'),
            ('iPhone 15 Plus', 2023, '6.7 inches', '128GB, 256GB, 512GB'),
            ('iPhone 15 Pro', 2023, '6.1 inches', '128GB, 256GB, 512GB, 1TB'),
            ('iPhone 15 Pro Max', 2023, '6.7 inches', '256GB, 512GB, 1TB'),
            
            # iPhone 16 series (2024)
            ('iPhone 16', 2024, '6.1 inches', '128GB, 256GB, 512GB, 1TB'),
            ('iPhone 16 Plus', 2024, '6.7 inches', '128GB, 256GB, 512GB, 1TB'),
            ('iPhone 16 Pro', 2024, '6.3 inches', '256GB, 512GB, 1TB, 2TB'),
            ('iPhone 16 Pro Max', 2024, '6.9 inches', '256GB, 512GB, 1TB, 2TB'),
            
            # iPhone 17 series (2025 - future)
            ('iPhone 17', 2025, '6.2 inches', '256GB, 512GB, 1TB, 2TB'),
            ('iPhone 17 Plus', 2025, '6.8 inches', '256GB, 512GB, 1TB, 2TB'),
            ('iPhone 17 Pro', 2025, '6.3 inches', '512GB, 1TB, 2TB'),
            ('iPhone 17 Pro Max', 2025, '6.9 inches', '512GB, 1TB, 2TB'),
        ]
        
        for name, year, display, storage in iphone_data:
            model, created = iPhoneModel.objects.get_or_create(
                name=name,
                defaults={
                    'release_year': year,
                    'display_size': display,
                    'storage_options': storage,
                    'description': f'The {name} features a {display} display and was released in {year}.'
                }
            )
            if created:
                self.stdout.write(f'Created iPhone model: {name}')

    def create_colors(self):
        colors_data = [
            ('Black', '#000000'),
            ('White', '#FFFFFF'),
            ('Silver', '#C0C0C0'),
            ('Space Gray', '#434343'),
            ('Gold', '#FFD700'),
            ('Rose Gold', '#B76E79'),
            ('Red', '#FF0000'),
            ('Blue', '#0000FF'),
            ('Purple', '#800080'),
            ('Green', '#008000'),
            ('Yellow', '#FFFF00'),
            ('Orange', '#FFA500'),
            ('Pacific Blue', '#0077BE'),
            ('Graphite', '#36454F'),
            ('Sierra Blue', '#4A90E2'),
            ('Alpine Green', '#4A7C59'),
            ('Deep Purple', '#301934'),
            ('Starlight', '#F8E7D2'),
            ('Midnight', '#1C1C1C'),
            ('Pink', '#FFC0CB'),
            ('Light Blue', '#ADD8E6'),
            ('Dark Cherry', '#4B0D0D'),
            ('Titanium', '#878681'),
            ('Natural Titanium', '#8B7D6B'),
            ('Blue Titanium', '#5F9EA0'),
            ('White Titanium', '#F5F5F5'),
            ('Black Titanium', '#2F4F4F'),
            ('Desert Titanium', '#C19A6B'),
        ]
        
        for name, hex_code in colors_data:
            color, created = Color.objects.get_or_create(
                name=name,
                defaults={'hex_code': hex_code}
            )
            if created:
                self.stdout.write(f'Created color: {name}')

    def create_sample_products(self):
        models = iPhoneModel.objects.all()
        colors = Color.objects.all()
        
        # Define which colors are available for which models (simplified)
        model_colors = {
            'iPhone 6': ['Black', 'White', 'Gold', 'Space Gray'],
            'iPhone 6 Plus': ['Black', 'White', 'Gold', 'Space Gray'],
            'iPhone 6s': ['Black', 'White', 'Gold', 'Rose Gold', 'Space Gray'],
            'iPhone 6s Plus': ['Black', 'White', 'Gold', 'Rose Gold', 'Space Gray'],
            'iPhone SE (1st gen)': ['Black', 'White', 'Rose Gold'],
            'iPhone 7': ['Black', 'White', 'Gold', 'Rose Gold', 'Red', 'Jet Black'],
            'iPhone 7 Plus': ['Black', 'White', 'Gold', 'Rose Gold', 'Red', 'Jet Black'],
            'iPhone 8': ['Black', 'White', 'Gold', 'Red'],
            'iPhone 8 Plus': ['Black', 'White', 'Gold', 'Red'],
            'iPhone X': ['Black', 'White', 'Gold', 'Space Gray'],
            'iPhone XR': ['Black', 'White', 'Blue', 'Yellow', 'Coral', 'Red'],
            'iPhone XS': ['Black', 'White', 'Gold', 'Space Gray'],
            'iPhone XS Max': ['Black', 'White', 'Gold', 'Space Gray'],
            'iPhone 11': ['Black', 'White', 'Green', 'Yellow', 'Purple', 'Red'],
            'iPhone 11 Pro': ['Black', 'White', 'Gold', 'Space Gray', 'Midnight Green'],
            'iPhone 11 Pro Max': ['Black', 'White', 'Gold', 'Space Gray', 'Midnight Green'],
            'iPhone SE (2nd gen)': ['Black', 'White', 'Red'],
            'iPhone 12 mini': ['Black', 'White', 'Blue', 'Green', 'Red', 'Purple'],
            'iPhone 12': ['Black', 'White', 'Blue', 'Green', 'Red', 'Purple'],
            'iPhone 12 Pro': ['Black', 'White', 'Blue', 'Gold', 'Pacific Blue'],
            'iPhone 12 Pro Max': ['Black', 'White', 'Blue', 'Gold', 'Pacific Blue'],
            'iPhone 13 mini': ['Black', 'White', 'Blue', 'Pink', 'Green', 'Red', 'Starlight'],
            'iPhone 13': ['Black', 'White', 'Blue', 'Pink', 'Green', 'Red', 'Starlight'],
            'iPhone 13 Pro': ['Black', 'White', 'Blue', 'Gold', 'Graphite', 'Sierra Blue'],
            'iPhone 13 Pro Max': ['Black', 'White', 'Blue', 'Gold', 'Graphite', 'Sierra Blue'],
            'iPhone SE (3rd gen)': ['Black', 'White', 'Red', 'Starlight'],
            'iPhone 14': ['Black', 'White', 'Blue', 'Purple', 'Red', 'Starlight'],
            'iPhone 14 Plus': ['Black', 'White', 'Blue', 'Purple', 'Red', 'Starlight'],
            'iPhone 14 Pro': ['Black', 'White', 'Blue', 'Purple', 'Gold', 'Deep Purple'],
            'iPhone 14 Pro Max': ['Black', 'White', 'Blue', 'Purple', 'Gold', 'Deep Purple'],
            'iPhone 15': ['Black', 'White', 'Blue', 'Pink', 'Green', 'Yellow'],
            'iPhone 15 Plus': ['Black', 'White', 'Blue', 'Pink', 'Green', 'Yellow'],
            'iPhone 15 Pro': ['Black', 'White', 'Blue', 'Natural Titanium'],
            'iPhone 15 Pro Max': ['Black', 'White', 'Blue', 'Natural Titanium'],
            'iPhone 16': ['Black', 'White', 'Blue', 'Pink', 'Green', 'Yellow'],
            'iPhone 16 Plus': ['Black', 'White', 'Blue', 'Pink', 'Green', 'Yellow'],
            'iPhone 16 Pro': ['Black', 'White', 'Blue', 'Natural Titanium', 'Desert Titanium'],
            'iPhone 16 Pro Max': ['Black', 'White', 'Blue', 'Natural Titanium', 'Desert Titanium'],
            'iPhone 17': ['Black', 'White', 'Blue', 'Pink', 'Green', 'Purple'],
            'iPhone 17 Plus': ['Black', 'White', 'Blue', 'Pink', 'Green', 'Purple'],
            'iPhone 17 Pro': ['Black', 'White', 'Blue', 'Natural Titanium', 'Desert Titanium'],
            'iPhone 17 Pro Max': ['Black', 'White', 'Blue', 'Natural Titanium', 'Desert Titanium'],
        }
        
        products_created = 0
        for model in models:
            available_colors = model_colors.get(model.name, ['Black', 'White', 'Blue'])
            storage_options = model.storage_options.split(', ')
            
            for color_name in available_colors:
                try:
                    color = Color.objects.get(name=color_name)
                except Color.DoesNotExist:
                    continue
                
                for storage in storage_options:
                    # Create products for different conditions
                    for condition in ['new', 'refurbished', 'used']:
                        # Generate realistic pricing based on model year and condition
                        base_price = self.calculate_price(model.release_year, storage, condition)
                        
                        # Random stock quantity
                        stock = random.randint(0, 50) if condition == 'new' else random.randint(0, 20)
                        
                        product, created = iPhoneProduct.objects.get_or_create(
                            iphone_model=model,
                            color=color,
                            storage=storage,
                            condition=condition,
                            defaults={
                                'price': base_price,
                                'stock_quantity': stock,
                                'is_active': stock > 0
                            }
                        )
                        
                        if created:
                            products_created += 1
                            self.stdout.write(f'Created product: {model.name} - {color.name} - {storage} - {condition} - ${base_price}')
        
        self.stdout.write(f'Total products created: {products_created}')

    def calculate_price(self, release_year, storage, condition):
        # Base pricing logic
        base_prices = {
            2014: 150,  # iPhone 6
            2015: 180,  # iPhone 6s
            2016: 200,  # iPhone 7/SE 1st gen
            2017: 250,  # iPhone 8/X
            2018: 350,  # iPhone XR/XS
            2019: 450,  # iPhone 11
            2020: 550,  # iPhone 12/SE 2nd gen
            2021: 650,  # iPhone 13/SE 3rd gen
            2022: 750,  # iPhone 14
            2023: 850,  # iPhone 15
            2024: 950,  # iPhone 16
            2025: 1050, # iPhone 17 (future)
        }
        
        base_price = base_prices.get(release_year, 500)
        
        # Storage adjustment
        storage_multipliers = {
            '16GB': 0.8, '32GB': 0.9, '64GB': 1.0, '128GB': 1.2,
            '256GB': 1.4, '512GB': 1.8, '1TB': 2.2, '2TB': 2.8
        }
        
        storage_multiplier = storage_multipliers.get(storage, 1.0)
        
        # Condition adjustment
        condition_multipliers = {
            'new': 1.0,
            'refurbished': 0.8,
            'used': 0.6
        }
        
        condition_multiplier = condition_multipliers.get(condition, 1.0)
        
        # Calculate final price
        final_price = base_price * storage_multiplier * condition_multiplier
        
        # Round to nearest 10
        return round(final_price / 10) * 10
