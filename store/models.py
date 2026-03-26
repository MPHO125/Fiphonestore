from django.db import models

from django.urls import reverse

from django.contrib.auth.models import User

import uuid

from datetime import datetime, timedelta



class iPhoneModel(models.Model):

    """iPhone model information (iPhone 6 to iPhone 17)"""

    MODEL_CHOICES = [

        ('iPhone 6', 'iPhone 6'),

        ('iPhone 6 Plus', 'iPhone 6 Plus'),

        ('iPhone 6s', 'iPhone 6s'),

        ('iPhone 6s Plus', 'iPhone 6s Plus'),

        ('iPhone SE (1st gen)', 'iPhone SE (1st gen)'),

        ('iPhone 7', 'iPhone 7'),

        ('iPhone 7 Plus', 'iPhone 7 Plus'),

        ('iPhone 8', 'iPhone 8'),

        ('iPhone 8 Plus', 'iPhone 8 Plus'),

        ('iPhone X', 'iPhone X'),

        ('iPhone XR', 'iPhone XR'),

        ('iPhone XS', 'iPhone XS'),

        ('iPhone XS Max', 'iPhone XS Max'),

        ('iPhone 11', 'iPhone 11'),

        ('iPhone 11 Pro', 'iPhone 11 Pro'),

        ('iPhone 11 Pro Max', 'iPhone 11 Pro Max'),

        ('iPhone SE (2nd gen)', 'iPhone SE (2nd gen)'),

        ('iPhone 12 mini', 'iPhone 12 mini'),

        ('iPhone 12', 'iPhone 12'),

        ('iPhone 12 Pro', 'iPhone 12 Pro'),

        ('iPhone 12 Pro Max', 'iPhone 12 Pro Max'),

        ('iPhone 13 mini', 'iPhone 13 mini'),

        ('iPhone 13', 'iPhone 13'),

        ('iPhone 13 Pro', 'iPhone 13 Pro'),

        ('iPhone 13 Pro Max', 'iPhone 13 Pro Max'),

        ('iPhone SE (3rd gen)', 'iPhone SE (3rd gen)'),

        ('iPhone 14', 'iPhone 14'),

        ('iPhone 14 Plus', 'iPhone 14 Plus'),

        ('iPhone 14 Pro', 'iPhone 14 Pro'),

        ('iPhone 14 Pro Max', 'iPhone 14 Pro Max'),

        ('iPhone 15', 'iPhone 15'),

        ('iPhone 15 Plus', 'iPhone 15 Plus'),

        ('iPhone 15 Pro', 'iPhone 15 Pro'),

        ('iPhone 15 Pro Max', 'iPhone 15 Pro Max'),

        ('iPhone 16', 'iPhone 16'),

        ('iPhone 16 Plus', 'iPhone 16 Plus'),

        ('iPhone 16 Pro', 'iPhone 16 Pro'),

        ('iPhone 16 Pro Max', 'iPhone 16 Pro Max'),

        ('iPhone 17', 'iPhone 17'),

        ('iPhone 17 Plus', 'iPhone 17 Plus'),

        ('iPhone 17 Pro', 'iPhone 17 Pro'),

        ('iPhone 17 Pro Max', 'iPhone 17 Pro Max'),

    ]

    

    name = models.CharField(max_length=50, choices=MODEL_CHOICES, unique=True)

    release_year = models.IntegerField()

    display_size = models.CharField(max_length=20)  # e.g., "6.1 inches"

    storage_options = models.CharField(max_length=100)  # e.g., "64GB, 128GB, 256GB"

    description = models.TextField(blank=True)

    

    def __str__(self):

        return self.name

    

    class Meta:

        ordering = ['-release_year', 'name']



class Color(models.Model):

    """Available colors for iPhones"""

    COLOR_CHOICES = [

        ('Black', 'Black'),

        ('White', 'White'),

        ('Silver', 'Silver'),

        ('Space Gray', 'Space Gray'),

        ('Gold', 'Gold'),

        ('Rose Gold', 'Rose Gold'),

        ('Red', 'Red (Product RED)'),

        ('Blue', 'Blue'),

        ('Purple', 'Purple'),

        ('Green', 'Green'),

        ('Yellow', 'Yellow'),

        ('Orange', 'Orange'),

        ('Pacific Blue', 'Pacific Blue'),

        ('Graphite', 'Graphite'),

        ('Sierra Blue', 'Sierra Blue'),

        ('Alpine Green', 'Alpine Green'),

        ('Deep Purple', 'Deep Purple'),

        ('Starlight', 'Starlight'),

        ('Midnight', 'Midnight'),

        ('Pink', 'Pink'),

        ('Light Blue', 'Light Blue'),

        ('Dark Cherry', 'Dark Cherry'),

        ('Titanium', 'Titanium'),

        ('Natural Titanium', 'Natural Titanium'),

        ('Blue Titanium', 'Blue Titanium'),

        ('White Titanium', 'White Titanium'),

        ('Black Titanium', 'Black Titanium'),

        ('Desert Titanium', 'Desert Titanium'),

    ]

    

    name = models.CharField(max_length=50, choices=COLOR_CHOICES, unique=True)

    hex_code = models.CharField(max_length=7, default="#000000")  # For UI display

    

    def __str__(self):

        return self.name



class iPhoneProduct(models.Model):

    """Individual iPhone product with specific model, color, and storage"""

    STORAGE_CHOICES = [

        ('32GB', '32GB'),

        ('64GB', '64GB'),

        ('128GB', '128GB'),

        ('256GB', '256GB'),

        ('512GB', '512GB'),

        ('1TB', '1TB'),

        ('2TB', '2TB'),

    ]

    

    CONDITION_CHOICES = [

        ('new', 'New'),

        ('refurbished', 'Refurbished'),

        ('used', 'Used'),

    ]

    GRADE_CHOICES = [

        ('A', 'Grade A - Best'),

        ('B', 'Grade B - Good'),

        ('C', 'Grade C - Better'),

    ]

    

    iphone_model = models.ForeignKey(iPhoneModel, on_delete=models.CASCADE)

    color = models.ForeignKey(Color, on_delete=models.CASCADE)

    storage = models.CharField(max_length=10, choices=STORAGE_CHOICES)

    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='new')

    grade = models.CharField(max_length=20, choices=GRADE_CHOICES, default='A', blank=True, null=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)

    stock_quantity = models.PositiveIntegerField(default=0)

    image = models.ImageField(upload_to='iphone_images/', blank=True, null=True)

    cover_photo = models.ImageField(upload_to='iphone_covers/', blank=True, null=True, help_text="Main cover photo for product listing")

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    

    def __str__(self):

        return f"{self.iphone_model.name} - {self.color.name} - {self.storage} - ${self.price}"

    

    def get_absolute_url(self):

        return reverse('store:product_detail', kwargs={'pk': self.pk})

    

    class Meta:

        unique_together = ['iphone_model', 'color', 'storage', 'condition']

        ordering = ['-created_at']



class Cart(models.Model):

    """Shopping cart for users"""

    session_key = models.CharField(max_length=40, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    

    def __str__(self):

        return f"Cart {self.session_key}"

    

    def get_total_price(self):

        return sum(item.get_total_price() for item in self.cartitem_set.all())

    

    def get_total_items(self):

        return sum(item.quantity for item in self.cartitem_set.all())



class CartItem(models.Model):

    """Individual item in shopping cart"""

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)

    product = models.ForeignKey(iPhoneProduct, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField(default=1)

    added_at = models.DateTimeField(auto_now_add=True)

    

    def __str__(self):

        return f"{self.quantity} x {self.product.iphone_model.name}"

    

    def get_total_price(self):

        return self.product.price * self.quantity

    

    class Meta:

        unique_together = ['cart', 'product']



class Order(models.Model):

    """Order model for customer purchases"""

    STATUS_CHOICES = [

        ('pending', 'Pending'),

        ('processing', 'Processing'),

        ('shipped', 'Shipped'),

        ('delivered', 'Delivered'),

        ('cancelled', 'Cancelled'),

    ]

    

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    session_key = models.CharField(max_length=40, null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    shipping_address = models.TextField()

    billing_address = models.TextField()

    email = models.EmailField()

    phone = models.CharField(max_length=20, blank=True)

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    

    def __str__(self):

        return f"Order {self.id}"

    

    def get_absolute_url(self):

        return reverse('store:order_detail', kwargs={'order_id': self.id})

    

    @property

    def order_number(self):

        return str(self.id).upper()[:8]

    

    def get_items(self):

        return self.orderitem_set.all()

    

    def get_item_count(self):

        return sum(item.quantity for item in self.get_items())



class OrderItem(models.Model):

    """Individual items in an order"""

    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    product = models.ForeignKey(iPhoneProduct, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField(default=1)

    price = models.DecimalField(max_digits=10, decimal_places=2)

    

    def __str__(self):

        return f"{self.quantity} x {self.product.iphone_model.name}"

    

    def get_total_price(self):

        return self.price * self.quantity

    

    class Meta:

        unique_together = ['order', 'product']



class ShippingTracking(models.Model):

    """Shipping tracking information"""

    order = models.OneToOneField(Order, on_delete=models.CASCADE)

    tracking_number = models.CharField(max_length=100, unique=True)

    carrier = models.CharField(max_length=100)

    shipped_date = models.DateTimeField(null=True, blank=True)

    estimated_delivery = models.DateTimeField(null=True, blank=True)

    delivered_date = models.DateTimeField(null=True, blank=True)

    current_status = models.CharField(max_length=100, default='In Transit')

    tracking_url = models.URLField(blank=True)

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    

    def __str__(self):

        return f"Tracking for {self.order.order_number}"

    

    def get_tracking_link(self):

        if self.tracking_url:

            return self.tracking_url

        # Generate generic tracking links based on carrier

        carrier_links = {

            'FedEx': f'https://www.fedex.com/fedextrack/?trknbr={self.tracking_number}',

            'UPS': f'https://www.ups.com/track?tracknum={self.tracking_number}',

            'USPS': f'https://tools.usps.com/go/TrackConfirmAction_input?qtc_tLabels1={self.tracking_number}',

            'DHL': f'https://www.dhl.com/en/express/tracking.html?AWB={self.tracking_number}',

        }

        return carrier_links.get(self.carrier, f'https://www.google.com/search?q={self.tracking_number}+tracking')



class ShippingUpdate(models.Model):

    """Individual shipping updates"""

    tracking = models.ForeignKey(ShippingTracking, on_delete=models.CASCADE, related_name='updates')

    status = models.CharField(max_length=200)

    location = models.CharField(max_length=200, blank=True)

    timestamp = models.DateTimeField()

    description = models.TextField(blank=True)

    

    def __str__(self):

        return f"Update for {self.tracking.order.order_number}: {self.status}"

    

    class Meta:

        ordering = ['-timestamp']

