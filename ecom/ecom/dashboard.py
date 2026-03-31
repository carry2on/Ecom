import json
from django.db.models import Sum
from django.db.models.functions import TruncMonth # NEW: Imports the month grouper
from django.contrib.auth.models import User
from store.models import Product, Category
from payment.models import Order

def dashboard_callback(request, context):
    # 1. Calculate KPI Stats
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_users = User.objects.count()
    
    revenue_data = Order.objects.aggregate(total=Sum('amount_paid'))
    if revenue_data['total']:
        total_revenue = f"{revenue_data['total']:.2f}" 
    else:
        total_revenue = "0.00"
    
    shipped_orders = Order.objects.filter(shipped=True).count()
    pending_orders = Order.objects.filter(shipped=False).count()

    # 2. NEW: Calculate Monthly Revenue
    # This groups orders by month and sums up the amount_paid
    monthly_revenue = (
        Order.objects
        .annotate(month=TruncMonth('date_ordered'))
        .values('month')
        .annotate(total_revenue=Sum('amount_paid'))
        .order_by('month')
    )

    revenue_labels = []
    revenue_data_points = []
    
    for entry in monthly_revenue:
        if entry['month']:
            # Formats the date to look like "Mar 2026"
            revenue_labels.append(entry['month'].strftime("%b %Y"))
            revenue_data_points.append(float(entry['total_revenue']))

    # 3. Build Line Chart Data (Monthly Revenue)
    line_chart_data = {
        "labels": revenue_labels,
        "datasets": [
            {
                "label": "Monthly Revenue (₹)",
                "data": revenue_data_points,
                "borderColor": "#10b981", # Emerald Green for money!
                "backgroundColor": "rgba(16, 185, 129, 0.1)", # Slight green glow under the line
                "borderWidth": 2,
                "fill": True,
                "tension": 0.4 # Makes the line beautifully curved instead of jagged
            }
        ],
    }

    # 4. Build Bar Chart Data
    bar_chart_data = {
        "labels": ["Shipped Orders", "Pending Orders"],
        "datasets": [{
            "label": "Order Status",
            "data": [shipped_orders, pending_orders],
            "backgroundColor": ["#a855f7", "#3b82f6"], 
            "borderWidth": 0,
        }],
    }

    # 5. Build Pie Chart Data (Products per Category)
    categories = Category.objects.all()
    category_labels = []
    category_data = []
    
    for cat in categories:
        category_labels.append(cat.name)
        count = Product.objects.filter(category=cat).count()
        category_data.append(count)

    pie_colors = ["#3b82f6", "#a855f7", "#ec4899", "#10b981", "#f59e0b"]

    pie_chart_data = {
        "labels": category_labels,
        "datasets": [{
            "data": category_data,
            "backgroundColor": pie_colors[:len(category_labels)],
            "borderWidth": 1,
            "borderColor": "#1e293b" 
        }]
    }
    
    # 6. Send ALL data to the template
    context.update({
        "kpi": [
            {"title": "Total Revenue", "metric": f"₹{total_revenue}", "footer": "All-time store earnings"},
            {"title": "Total Orders", "metric": str(total_orders), "footer": "Total successful orders"},
            {"title": "Total Products", "metric": str(total_products), "footer": "Active catalog items"},
            {"title": "Total Users", "metric": str(total_users), "footer": "Registered accounts"},
        ],
        "line_chart": json.dumps(line_chart_data), # New Monthly Chart
        "chart": json.dumps(bar_chart_data),
        "pie_chart": json.dumps(pie_chart_data) 
    })
    
    return context