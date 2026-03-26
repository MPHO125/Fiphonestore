from django.shortcuts import render, get_object_or_404, redirect

from django.db.models import Q

from django.views.generic import ListView, DetailView, View

from django.views import View

from django.contrib import messages

from django.http import JsonResponse

from django.utils.decorators import method_decorator

from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import login, authenticate, logout

from django.contrib.auth.decorators import login_required

from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth.models import User

from django.contrib.auth.forms import AuthenticationForm

from .models import iPhoneProduct, iPhoneModel, Color, Cart, CartItem, Order, OrderItem, ShippingTracking, ShippingUpdate

from .forms import CustomUserCreationForm

import json

import uuid

from datetime import datetime, timedelta



class ProductListView(ListView):

    model = iPhoneProduct

    template_name = 'store/product_list.html'

    context_object_name = 'products'

    paginate_by = 12

    

    def get_queryset(self):

        queryset = iPhoneProduct.objects.filter(is_active=True)

        

        # Search functionality

        search_query = self.request.GET.get('search', '')

        if search_query:

            queryset = queryset.filter(

                Q(iphone_model__name__icontains=search_query) |

                Q(color__name__icontains=search_query) |

                Q(storage__icontains=search_query)

            )

        

        # Filter by model

        model_filter = self.request.GET.get('model', '')

        if model_filter:

            queryset = queryset.filter(iphone_model__name=model_filter)

        

        # Filter by color

        color_filter = self.request.GET.get('color', '')

        if color_filter:

            queryset = queryset.filter(color__name=color_filter)

        

        # Filter by storage

        storage_filter = self.request.GET.get('storage', '')

        if storage_filter:

            queryset = queryset.filter(storage=storage_filter)

        

        # Filter by condition

        condition_filter = self.request.GET.get('condition', '')

        if condition_filter:

            queryset = queryset.filter(condition=condition_filter)

        

        # Sort by

        sort_by = self.request.GET.get('sort', 'newest')

        if sort_by == 'price_low':

            queryset = queryset.order_by('price')

        elif sort_by == 'price_high':

            queryset = queryset.order_by('-price')

        elif sort_by == 'name':

            queryset = queryset.order_by('iphone_model__name')

        else:  # newest

            queryset = queryset.order_by('-created_at')

        

        return queryset

    

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        

        # Add filter options

        context['models'] = iPhoneModel.objects.all()

        context['colors'] = Color.objects.all()

        context['storage_options'] = iPhoneProduct.STORAGE_CHOICES

        context['condition_options'] = iPhoneProduct.CONDITION_CHOICES

        

        # Add current filter values

        context['current_search'] = self.request.GET.get('search', '')

        context['current_model'] = self.request.GET.get('model', '')

        context['current_color'] = self.request.GET.get('color', '')

        context['current_storage'] = self.request.GET.get('storage', '')

        context['current_condition'] = self.request.GET.get('condition', '')

        context['current_sort'] = self.request.GET.get('sort', 'newest')

        

        return context



class ProductDetailView(DetailView):

    model = iPhoneProduct

    template_name = 'store/product_detail.html'

    context_object_name = 'product'

    

    def get_queryset(self):

        return iPhoneProduct.objects.filter(is_active=True)

    

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        product = self.get_object()

        

        # Get related products (same model, different colors or storage)

        related_products = iPhoneProduct.objects.filter(

            iphone_model=product.iphone_model,

            is_active=True

        ).exclude(pk=product.pk)[:4]

        

        # Get storage variants for the same model and color
        storage_variants = iPhoneProduct.objects.filter(
            iphone_model=product.iphone_model,
            color=product.color,
            is_active=True
        ).order_by('storage')

        # Get color variants for the same model
        color_variants = iPhoneProduct.objects.filter(
            iphone_model=product.iphone_model,
            storage=product.storage,
            is_active=True
        ).select_related('color').order_by('color__name')

        context['related_products'] = related_products
        context['storage_variants'] = storage_variants
        context['color_variants'] = color_variants

        return context



class CartView(View):

    def get(self, request):

        cart = self.get_or_create_cart()

        cart_items = cart.cartitem_set.all()

        

        context = {

            'cart': cart,

            'cart_items': cart_items,

        }

        return render(request, 'store/cart.html', context)

    

    def get_or_create_cart(self):

        session_key = self.request.session.session_key

        if not session_key:

            self.request.session.create()

            session_key = self.request.session.session_key

        

        cart, created = Cart.objects.get_or_create(session_key=session_key)

        return cart



class AddToCartView(View):

    def post(self, request, product_id):

        product = get_object_or_404(iPhoneProduct, id=product_id, is_active=True)

        quantity = int(request.POST.get('quantity', 1))

        

        if product.stock_quantity < quantity:

            messages.error(request, f'Sorry, only {product.stock_quantity} items available in stock.')

            return redirect('store:product_detail', pk=product_id)

        

        # Get or create cart for this session
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        cart, created = Cart.objects.get_or_create(session_key=session_key)

        

        cart_item, created = CartItem.objects.get_or_create(

            cart=cart,

            product=product,

            defaults={'quantity': quantity}

        )

        

        if not created:

            cart_item.quantity += quantity

            cart_item.save()

        

        messages.success(request, f'{product.iphone_model.name} added to cart!')

        return redirect('store:cart')



class UpdateCartView(View):

    def post(self, request, item_id):

        cart_item = get_object_or_404(CartItem, id=item_id)

        quantity = int(request.POST.get('quantity', 1))

        

        if quantity <= 0:

            cart_item.delete()

            messages.success(request, 'Item removed from cart.')

        elif quantity <= cart_item.product.stock_quantity:

            cart_item.quantity = quantity

            cart_item.save()

            messages.success(request, 'Cart updated successfully.')

        else:

            messages.error(request, f'Sorry, only {cart_item.product.stock_quantity} items available.')

        

        return redirect('store:cart')



class RemoveFromCartView(View):

    def post(self, request, item_id):

        cart_item = get_object_or_404(CartItem, id=item_id)

        cart_item.delete()

        messages.success(request, 'Item removed from cart.')

        return redirect('store:cart')



@method_decorator(csrf_exempt, name='dispatch')

class CartSummaryView(View):

    def get(self, request):
        # Get or create cart for this session
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        cart, created = Cart.objects.get_or_create(session_key=session_key)
        
        data = {
            'total_items': cart.get_total_items(),
            'total_price': float(cart.get_total_price()),
        }

        

        return JsonResponse(data)



def home(request):

    featured_products = iPhoneProduct.objects.filter(is_active=True).order_by('-created_at')[:8]

    latest_models = iPhoneModel.objects.all().order_by('-release_year')[:6]

    

    context = {

        'featured_products': featured_products,

        'latest_models': latest_models,

    }

    return render(request, 'store/home.html', context)



# Authentication Views

def register(request):

    if request.method == 'POST':

        form = CustomUserCreationForm(request.POST)

        if form.is_valid():

            user = form.save()

            username = form.cleaned_data.get('username')

            

            # Check if this is an AJAX request (from modal)

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':

                return JsonResponse({'success': True, 'message': f'Account created for {username}!'})

            

            messages.success(request, f'Account created for {username}! You can now log in.')

            return redirect('store:login')

        else:

            # Check if this is an AJAX request (from modal)

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':

                errors = dict(form.errors.items())

                return JsonResponse({'success': False, 'error': 'Registration failed', 'errors': errors})

    else:

        form = CustomUserCreationForm()

    

    # For regular page load, render the template

    return render(request, 'store/register.html', {'form': form})



def custom_login(request):

    if request.method == 'POST':

        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():

            username = form.cleaned_data.get('username')

            password = form.cleaned_data.get('password')

            user = authenticate(username=username, password=password)

            if user is not None:

                login(request, user)

                

                # Check if this is an AJAX request (from modal)

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':

                    return JsonResponse({'success': True, 'message': f'Welcome back, {username}!'})

                

                messages.success(request, f'Welcome back, {username}!')

                return redirect('store:home')

            else:

                error_message = 'Invalid username or password.'

                

                # Check if this is an AJAX request (from modal)

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':

                    return JsonResponse({'success': False, 'error': error_message})

                

                messages.error(request, error_message)

        else:

            error_message = 'Invalid username or password.'

            

            # Check if this is an AJAX request (from modal)

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':

                errors = dict(form.errors.items())

                return JsonResponse({'success': False, 'error': error_message, 'errors': errors})

            

            messages.error(request, error_message)

    else:

        form = AuthenticationForm()

    

    # For regular page load, render the template

    return render(request, 'store/login.html', {'form': form})



def custom_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('store:home')



@login_required

def profile(request):

    return render(request, 'store/profile.html')



@login_required

def update_profile(request):

    if request.method == 'POST':

        user = request.user

        user.first_name = request.POST.get('first_name', user.first_name)

        user.last_name = request.POST.get('last_name', user.last_name)

        user.email = request.POST.get('email', user.email)

        user.save()

        messages.success(request, 'Profile updated successfully!')

        return redirect('store:profile')

    

    return redirect('store:profile')



@login_required

def checkout(request):

    if request.method == 'POST':

        try:

            # Get cart directly

            cart = Cart.objects.get_or_create(session_key=request.session.session_key)[0]

            cart_items = cart.cartitem_set.all()

            

            if not cart_items:

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':

                    return JsonResponse({'success': False, 'error': 'Your cart is empty'})

                messages.error(request, 'Your cart is empty')

                return redirect('store:cart')

            

            # Create order

            total_amount = cart.get_total_price()

            order = Order.objects.create(

                user=request.user,

                total_amount=total_amount,

                shipping_address=request.POST.get('shipping_address'),

                billing_address=request.POST.get('billing_address'),

                email=request.POST.get('email'),

                phone=request.POST.get('phone', ''),

                notes=request.POST.get('notes', '')

            )

            

            # Create order items

            for cart_item in cart_items:

                OrderItem.objects.create(

                    order=order,

                    product=cart_item.product,

                    quantity=cart_item.quantity,

                    price=cart_item.product.price

                )

            

            # Create shipping tracking

            tracking_number = f"IP{order.order_number.upper()}{datetime.now().strftime('%m%d')}"

            tracking = ShippingTracking.objects.create(

                order=order,

                tracking_number=tracking_number,

                carrier='iPhone Store Shipping',

                shipped_date=datetime.now(),

                estimated_delivery=datetime.now() + timedelta(days=5),

                current_status='Order Confirmed'

            )

            

            # Add initial shipping update

            ShippingUpdate.objects.create(

                tracking=tracking,

                status='Order Confirmed',

                location='Processing Center',

                timestamp=datetime.now(),

                description='Your order has been confirmed and is being processed.'

            )

            

            # Clear cart

            cart_items.delete()

            

            # Check if this is an AJAX request

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':

                return JsonResponse({

                    'success': True, 

                    'order_number': order.order_number,

                    'message': 'Order placed successfully!'

                })

            

            messages.success(request, f'Order placed successfully! Order number: {order.order_number}')

            return redirect('store:order_detail', order_id=order.id)

            

        except Exception as e:

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':

                return JsonResponse({'success': False, 'error': str(e)})

            messages.error(request, 'An error occurred while placing your order. Please try again.')

            return redirect('store:cart')

    

    return redirect('store:cart')



@login_required

def order_list(request):

    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'store/order_list.html', {'orders': orders})



@login_required

def order_detail(request, order_id):

    order = get_object_or_404(Order, id=order_id, user=request.user)

    tracking = getattr(order, 'shippingtracking', None)

    updates = tracking.updates.all() if tracking else []

    return render(request, 'store/order_detail.html', {

        'order': order,

        'tracking': tracking,

        'updates': updates

    })



def track_order(request):

    tracking_number = request.GET.get('tracking_number', '').strip()

    if not tracking_number:

        return render(request, 'store/track_order.html', {'error': None})

    

    try:

        tracking = ShippingTracking.objects.get(tracking_number__iexact=tracking_number)

        updates = tracking.updates.all()

        return render(request, 'store/track_order.html', {

            'tracking': tracking,

            'updates': updates,

            'order': tracking.order

        })

    except ShippingTracking.DoesNotExist:

        return render(request, 'store/track_order.html', {

            'error': 'Tracking number not found. Please check and try again.'

        })

