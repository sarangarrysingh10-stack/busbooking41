BusGo Advanced Booking + PayPal Payment Update

Replace the included main folder into your project root where manage.py is located.

Updated files:
- main/models.py
- main/admin.py
- main/views.py
- main/urls.py
- main/migrations/0005_booking_payment_fields.py
- main/templates/index.html
- main/templates/index (5).html
- main/templates/booking_form.html
- main/templates/booking_success.html
- main/templates/booking_lookup.html

What it adds:
1. Book Tickets button in navbar.
2. My Bookings button in navbar.
3. Payment Options button and section on home page.
4. Payment methods during booking: Cash / Pay Later, PayPal, Debit/Credit Card, Net Banking.
5. PayPal asks for payer name, PayPal email/account ID, and transaction/reference ID.
6. Card and Net Banking ask for payer name and transaction/reference ID only.
7. Payment method/status appears on booking success page, booking lookup page, and Django Admin.
8. Admin Bookings button is removed from user-facing success page.

Important: This is a demo payment verification flow. It does not connect to a real PayPal/Razorpay/Stripe payment gateway and does not store card number, CVV, bank password, or real payment credentials. Admin verifies the transaction/reference ID manually and changes Payment Status in Django Admin.

After replacing files run:
python manage.py migrate
python manage.py runserver

Then push to GitHub for Railway deployment.
