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

from .payfast import PayFastPayment, verify_payfast_signature

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
            # Ensure session exists
            if not request.session.session_key:
                request.session.create()
            
            # Get cart directly
            cart = Cart.objects.get_or_create(session_key=request.session.session_key)[0]
            cart_items = cart.cartitem_set.all()
            
            if not cart_items:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'Your cart is empty'})
                messages.error(request, 'Your cart is empty')
                return redirect('store:cart')
            
            # Validate required fields
            shipping_address = request.POST.get('shipping_address', '').strip()
            billing_address = request.POST.get('billing_address', '').strip()
            email = request.POST.get('email', '').strip()
            
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            
            if not shipping_address:
                if is_ajax:
                    return JsonResponse({'success': False, 'error': 'Shipping address is required'})
                messages.error(request, 'Shipping address is required')
                return redirect('store:cart')
            if not billing_address:
                if is_ajax:
                    return JsonResponse({'success': False, 'error': 'Billing address is required'})
                messages.error(request, 'Billing address is required')
                return redirect('store:cart')
            if not email:
                if is_ajax:
                    return JsonResponse({'success': False, 'error': 'Email is required'})
                messages.error(request, 'Email is required')
                return redirect('store:cart')
            
            # Create order with pending payment status
            total_amount = cart.get_total_price()
            order = Order.objects.create(
                user=request.user,
                total_amount=total_amount,
                shipping_address=shipping_address,
                billing_address=billing_address,
                email=email,
                phone=request.POST.get('phone', ''),
                notes=request.POST.get('notes', ''),
                status='pending_payment',
                payment_status='pending'
            )
            
            # Create order items
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
                # Update stock
                cart_item.product.stock_quantity -= cart_item.quantity
                cart_item.product.save()
            
            # Store order ID in session for payment processing
            request.session['pending_order_id'] = str(order.id)
            
            # Generate PayFast payment form
            payfast_payment = PayFastPayment(order, request)
            payment_form = payfast_payment.get_payment_form()
            
            # Return payment form data for AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'order_number': order.order_number,
                    'payment_required': True,
                    'payment_form': payment_form
                })
            
            # For regular form submission, render payment redirect page
            return render(request, 'store/payment_redirect.html', {
                'order': order,
                'payment_form': payment_form
            })
            
        except Exception as e:
            import traceback
            error_msg = str(e)
            tb = traceback.format_exc()
            print(f"CHECKOUT ERROR: {error_msg}")
            print(tb)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': f'Error: {error_msg}'})
            # Show error page with details instead of redirecting
            return render(request, 'store/checkout_error.html', {
                'error_message': error_msg,
                'traceback': tb
            })
    
    return redirect('store:cart')


@login_required
def checkout_debug(request):
    """Debug view to check checkout configuration"""
    from django.conf import settings
    import traceback
    
    debug_info = {
        'session_key': request.session.session_key,
        'user': str(request.user),
        'cart_exists': False,
        'cart_items_count': 0,
        'payfast_config': {
            'mode': getattr(settings, 'PAYFAST_MODE', 'NOT SET'),
            'merchant_id': getattr(settings, 'PAYFAST_MERCHANT_ID', 'NOT SET'),
            'merchant_key': getattr(settings, 'PAYFAST_MERCHANT_KEY', 'NOT SET')[:5] + '...' if getattr(settings, 'PAYFAST_MERCHANT_KEY', '') else 'NOT SET',
        },
        'errors': []
    }
    
    # Check cart
    try:
        if not request.session.session_key:
            request.session.create()
        cart = Cart.objects.get_or_create(session_key=request.session.session_key)[0]
        cart_items = cart.cartitem_set.all()
        debug_info['cart_exists'] = True
        debug_info['cart_items_count'] = cart_items.count()
        debug_info['cart_total'] = str(cart.get_total_price())
    except Exception as e:
        debug_info['errors'].append(f'Cart error: {str(e)}')
        debug_info['errors'].append(traceback.format_exc())
    
    # Check PayFast config
    try:
        from .payfast import PayFastConfig
        config = PayFastConfig()
        debug_info['payfast_config']['process_url'] = config.get_process_url()
        debug_info['payfast_config']['merchant_id'] = config.get_merchant_id()
    except Exception as e:
        debug_info['errors'].append(f'PayFast config error: {str(e)}')
        debug_info['errors'].append(traceback.format_exc())
    
    return JsonResponse(debug_info, json_dumps_params={'indent': 2})


@login_required
def payment_redirect(request):
    """Display payment redirect page with auto-submitting form"""
    order_id = request.session.get('pending_order_id')
    if not order_id:
        messages.error(request, 'No pending order found.')
        return redirect('store:cart')
    
    order = get_object_or_404(Order, id=order_id, user=request.user)
    payfast_payment = PayFastPayment(order, request)
    payment_form = payfast_payment.get_payment_form()
    
    return render(request, 'store/payment_redirect.html', {
        'order': order,
        'payment_form': payment_form
    })


@csrf_exempt
def payment_notify(request):
    """
    PayFast ITN (Instant Transaction Notification) handler
    This is called by PayFast server-to-server when payment is complete
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
    
    try:
        # Get POST data
        data = request.POST.dict()
        
        # Verify signature
        signature = data.pop('signature', None)
        if not signature:
            return JsonResponse({'status': 'error', 'message': 'Missing signature'})
        
        if not verify_payfast_signature(data, signature):
            return JsonResponse({'status': 'error', 'message': 'Invalid signature'})
        
        # Get order from m_payment_id
        order_id = data.get('m_payment_id')
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Order not found'})
        
        # Update order with PayFast data
        order.pf_payment_id = data.get('pf_payment_id')
        order.pf_transaction_id = data.get('pf_transaction_id')
        order.pf_payment_status = data.get('payment_status')
        
        # Handle payment status
        payment_status = data.get('payment_status', '').lower()
        
        if payment_status == 'complete':
            order.payment_status = 'completed'
            order.status = 'paid'
            order.pf_amount_gross = data.get('amount_gross')
            order.pf_amount_fee = data.get('amount_fee')
            order.pf_amount_net = data.get('amount_net')
            
            # Create shipping tracking after successful payment
            if not hasattr(order, 'shippingtracking'):
                tracking_number = f"IP{order.order_number.upper()}{datetime.now().strftime('%m%d')}"
                tracking = ShippingTracking.objects.create(
                    order=order,
                    tracking_number=tracking_number,
                    carrier='iPhone Store Shipping',
                    shipped_date=None,  # Will be set when actually shipped
                    estimated_delivery=datetime.now() + timedelta(days=5),
                    current_status='Payment Confirmed'
                )
                ShippingUpdate.objects.create(
                    tracking=tracking,
                    status='Payment Confirmed',
                    location='Processing Center',
                    timestamp=datetime.now(),
                    description='Your payment has been received and order is being processed.'
                )
        elif payment_status == 'failed':
            order.payment_status = 'failed'
        elif payment_status == 'cancelled':
            order.payment_status = 'cancelled'
        
        order.save()
        
        return JsonResponse({'status': 'ok'})
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@login_required
def payment_success(request):
    """Customer is redirected here after successful payment"""
    order_id = request.session.get('pending_order_id')
    
    if order_id:
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            # Clear pending order from session
            del request.session['pending_order_id']
            request.session.modified = True
            
            messages.success(request, f'Payment successful! Order number: {order.order_number}')
            return redirect('store:order_detail', order_id=order.id)
        except Order.DoesNotExist:
            pass
    
    messages.success(request, 'Payment completed successfully!')
    return redirect('store:order_list')


@login_required
def payment_cancel(request):
    """Customer is redirected here if they cancel payment"""
    order_id = request.session.get('pending_order_id')
    
    if order_id:
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            order.payment_status = 'cancelled'
            order.save()
            
            # Restore stock
            for item in order.get_items():
                item.product.stock_quantity += item.quantity
                item.product.save()
            
            messages.warning(request, 'Payment was cancelled. Your order has been saved but not processed.')
        except Order.DoesNotExist:
            messages.warning(request, 'Payment was cancelled.')
    else:
        messages.warning(request, 'Payment was cancelled.')
    
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

