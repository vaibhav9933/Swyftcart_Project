from django.shortcuts import redirect, render
from django.http import JsonResponse, HttpResponse
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from carts.models import CartItem
from orders.forms import OrderForm
from .models import Order, OrderProduct, Payment
from store.models import Product

import datetime
import json

# ReportLab imports for PDF generation
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from .models import Order, OrderProduct
import os


# ============================= PAYMENTS ============================= #
def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])
    
    # Store transaction details inside the Payment model
    payment = Payment(
        user=request.user,
        payment_id=body['transID'],
        payment_method=body['payment_method'],
        amount_paid=order.order_total,
        status=body['status'],
    )
    payment.save()

    # Update the Order model
    order.payment = payment
    order.is_ordered = True
    order.save()

    # Move the cart items to OrderProduct model
    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        # Handle product variations
        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variation.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variation.set(product_variation)
        orderproduct.save()

        # Reduce the stock
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    # Clear the cart
    CartItem.objects.filter(user=request.user).delete()

    # Send order confirmation email to customer
    mail_subject = "Thank You for your order!"
    message = render_to_string("orders/order_recieved_email.html", {
        "user": request.user,
        "order": order,
    }) 
    to_email = request.user.email
    email_message = EmailMessage(mail_subject, message, to=[to_email])
    email_message.content_subtype = "html"  # Ensures HTML email
    email_message.send()
    
    # ✅ Final JSON response back to frontend
    response = {
        'status': 'success',
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }
    return JsonResponse(response)


# ============================= PLACE ORDER ============================= #
def place_order(request, total=0, quantity=0):
    current_user = request.user

    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')
    
    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total) / 100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Store all billing info in order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            }
            return render(request, 'orders/payments.html', context)
    else:
        return redirect("checkout")


# ============================= ORDER COMPLETE ============================= #
def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id) 

        subtotal = 0
        for i in ordered_products:
            subtotal += (i.product_price * i.quantity)

        payments = Payment.objects.get(payment_id=transID)
         
        context = {
            'order':order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payments.payment_id,
            'payment': payments,
            'subtotal': subtotal,
        }
        return render(request, "orders/order_complete.html",context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')
    

# ============================= DOWNLOAD INVOICE ============================= #

def download_invoice(request, order_id):
    order = Order.objects.get(id=order_id)
    ordered_products = OrderProduct.objects.filter(order=order)

    # Response setup
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="invoice_{order.order_number}.pdf"'

    # PDF document
    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=60, bottomMargin=40)
    elements = []

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="CenterTitle", alignment=1, fontSize=16, spaceAfter=20))
    styles.add(ParagraphStyle(name="NormalSmall", fontSize=10, leading=12))

    # ✅ Logo only (keeps aspect ratio)
    logo_path = os.path.join("static", "images", "logo.png")  # adjust if needed
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=80, height=40)  # adjust size if too big/small
        elements.append(logo)
        elements.append(Spacer(1, 20))

    # Title
    elements.append(Paragraph("<b>INVOICE</b>", styles["CenterTitle"]))
    elements.append(Spacer(1, 12))

    # Order Info
    order_info = f"""
        <b>Order Number:</b> {order.order_number}<br/>
        <b>Transaction ID:</b> {order.payment.payment_id}<br/>
        <b>Date:</b> {order.created_at.strftime('%Y-%m-%d')}<br/>
        <b>Status:</b> {order.payment.status}<br/>
    """
    elements.append(Paragraph(order_info, styles["Normal"]))
    elements.append(Spacer(1, 10))

    # Customer Info
    customer_info = f"""
        <b>Customer:</b> {order.full_name()}<br/>
        <b>Address:</b> {order.full_address()}, {order.city}, {order.state}, {order.country}
    """
    elements.append(Paragraph(customer_info, styles["Normal"]))
    elements.append(Spacer(1, 20))

    # Product Table
    data = [["Product", "Qty", "Price"]]
    for item in ordered_products:
        variations = ""
        if item.variation.all():
            variations = "<br/>".join([
                f"{v.variation_category.capitalize()}: {v.variation_value.capitalize()}"
                for v in item.variation.all()
            ])
        product_text = f"{item.product.product_name}<br/><font size=8 color=grey>{variations}</font>" if variations else item.product.product_name
        data.append([Paragraph(product_text, styles["NormalSmall"]), str(item.quantity), f"{item.product_price:.2f}"])

    # Totals
    data.append(["", "Sub Total:", f"{order.order_total - order.tax:.2f}"])
    data.append(["", "Tax:", f"{order.tax:.2f}"])
    data.append(["", "Grand Total:", f"{order.order_total:.2f}"])

    table = Table(data, colWidths=[250, 80, 100])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f2f2f2")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND", (0, -3), (-1, -1), colors.HexColor("#fafafa")),
        ("FONTNAME", (1, -1), (-1, -1), "Helvetica-Bold"),
        ("TEXTCOLOR", (1, -1), (-1, -1), colors.HexColor("#28a745")),
    ]))
    elements.append(table)

    elements.append(Spacer(1, 20))
    elements.append(Paragraph("<b>Thank you for shopping with us 💙</b>", styles["NormalSmall"]))

    # Build PDF
    doc.build(elements)
    return response

