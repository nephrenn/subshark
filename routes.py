from models.models import db, User
from flask import render_template, session, Blueprint, redirect, url_for, make_response, request, jsonify
from functools import wraps
from models.subscription import Subscription
from datetime import datetime, timedelta
import requests
import os

routes = Blueprint('routes', __name__)

@routes.route("/my_subscriptions")
def my_subscriptions_route():
    if 'user' not in session or 'user_email' not in session['user']:
        return redirect(url_for('routes.landing_route'))
    
    user_email = session['user']['user_email']
    user = User.query.filter_by(email=user_email).first()
    
    # Get exchange rates for user's currency
    exchange_rates = get_exchange_rates(user.currency)
    
    # Currency Display Format
    currency_display = user.currency
    
    # Convert Subscriptions
    converted_subscriptions = []
    subscriptions = Subscription.query.filter_by(user_id=user.id).all()
    for sub in subscriptions:
        converted_sub = sub.__dict__.copy()
        
        # Calculate base cost based on billing cycle
        base_cost = float(sub.cost)
        if sub.billing_cycle == 'weekly':
            monthly_cost = base_cost * 4  # Weekly to monthly
        elif sub.billing_cycle == 'quarterly':
            monthly_cost = base_cost / 3  # Quarterly to monthly
        elif sub.billing_cycle == 'sixMonths':
            monthly_cost = base_cost / 6  # Six months to monthly
        elif sub.billing_cycle == 'yearly':
            monthly_cost = base_cost / 12  # Yearly to monthly
        else:  # monthly
            monthly_cost = base_cost
        
        # Only convert if currencies are different
        if (sub.original_currency or 'USD') != user.currency:
            converted_cost = monthly_cost * (float(exchange_rates.get(user.currency, 1)) / float(exchange_rates.get(sub.original_currency or 'USD', 1)))
            converted_sub['cost'] = round(converted_cost, 2)
            converted_sub['currency_display'] = currency_display
        else:
            # Use calculated monthly cost with original currency
            converted_sub['cost'] = round(monthly_cost, 2)
            converted_sub['currency_display'] = sub.original_currency or 'USD'
        
        converted_subscriptions.append(converted_sub)
    
    return render_template("my_subscriptions.html", 
                          with_sidebar=True, 
                          subscriptions=converted_subscriptions,
                          category_colors=category_colors)
    
    # Add subscription ID to upcoming payments
    upcoming_payments = []
    today = datetime.now().date()
    subscriptions = Subscription.query.filter_by(user_id=user.id).all()
    for sub in subscriptions:
        days_until_billing = (sub.billing_date - today).days
        
        if days_until_billing <= 0:
            urgency = 'overdue'
        elif days_until_billing <= 7:
            urgency = 'soon'
        else:
            urgency = 'upcoming'
        
        # Use original cost and currency if it matches user's currency
        if (sub.original_currency or 'USD') == user.currency:
            cost = float(sub.cost)
            currency = sub.original_currency or 'USD'
        else:
            # Convert only if currencies are different
            cost = round(float(sub.cost) * (float(exchange_rates.get(user.currency, 1)) / float(exchange_rates.get(sub.original_currency or 'USD', 1))), 2)
            currency = user.currency
        upcoming_payments.append({
            'id': sub.id,
            'name': sub.name,
            'billing_date': sub.billing_date,
            'days_until_billing': days_until_billing,
            'urgency': urgency,
            'cost': cost,
            'currency_display': currency,
            'auto_renew': sub.auto_renew
        })
        
    upcoming_payments.sort(key=lambda x: x['billing_date'])
    
    # Currency Symbols Mapping
    currency_symbols = {
        'USD': '$', 'EUR': '€', 'GBP': '£', 'JPY': '¥', 'CNY': '¥', 'AUD': 'A$', 'CAD': 'C$', 
        'CHF': 'CHF', 'HKD': 'HK$', 'SGD': 'S$', 'INR': '₹', 'BRL': 'R$', 'RUB': '₽', 'ZAR': 'R',
        'MXN': '$', 'AED': 'د.إ', 'THB': '฿', 'TRY': '₺', 'NZD': 'NZ$', 'PLN': 'zł', 'NOK': 'kr',
        'DKK': 'kr', 'ILS': '₪', 'MYR': 'RM', 'IDR': 'Rp', 'PHP': '₱', 'CZK': 'Kč', 'HUF': 'Ft', 'CLP': '$'
    }
    
    # Convert Subscriptions
    converted_subscriptions = []
    for sub in subscriptions:
        converted_sub = sub.__dict__.copy()
        
        # Calculate monthly equivalent based on billing cycle
        if (sub.original_currency or 'USD') == user.currency:
            # If currencies match, use original cost
            base_cost = float(sub.cost)
        else:
            # Convert cost to user's currency
            base_cost = float(sub.cost) * (float(exchange_rates.get(user.currency, 1)) / float(exchange_rates.get(sub.original_currency or 'USD', 1)))
        
        # Calculate monthly equivalent based on billing cycle
        if sub.billing_cycle == 'weekly':
            monthly_cost = base_cost * 4
        elif sub.billing_cycle == 'quarterly':
            monthly_cost = base_cost / 3
        elif sub.billing_cycle == 'sixMonths':
            monthly_cost = base_cost / 6
        elif sub.billing_cycle == 'yearly':
            monthly_cost = base_cost / 12
        else:  # monthly
            monthly_cost = base_cost
        
        converted_sub['cost'] = round(monthly_cost, 2)
        converted_sub['currency_display'] = user.currency if (sub.original_currency or 'USD') != user.currency else sub.original_currency
        converted_subscriptions.append(converted_sub)
    
    return render_template("my_subscriptions.html", 
                            with_sidebar=True, 
                            subscriptions=converted_subscriptions,
                            category_colors=category_colors)

@routes.route("/calendar")
def calendar_route():
    if 'user' not in session or 'user_email' not in session['user']:
        return redirect(url_for('routes.landing_route'))
    return render_template("calendar.html", with_sidebar=True)

@routes.route("/calendar/subscriptions/<int:year>/<int:month>")
def calendar_subscriptions(year, month):
    if 'user' not in session or 'user_email' not in session['user']:
        return jsonify([])
    
    user = User.query.filter_by(email=session['user']['user_email']).first()
    if not user:
        return jsonify([])
    
    subscriptions = Subscription.query.filter_by(user_id=user.id).all()
    return jsonify([{
        'id': sub.id,
        'name': sub.name,
        'billing_date': sub.billing_date.strftime('%Y-%m-%d')
    } for sub in subscriptions])

@routes.route("/analytics")
def analytics_route():
    if 'user' not in session or 'user_email' not in session['user']:
        return redirect(url_for('routes.landing_route'))
    return render_template("analytics.html", with_sidebar=True)

@routes.route("/discover")
def discover_route():
    if 'user' not in session or 'user_email' not in session['user']:
        return redirect(url_for('routes.landing_route'))
    return render_template("discover.html", with_sidebar=True)

category_colors = {
    'Streaming': 'primary',
    'Software': 'success',
    'Gaming': 'danger',
    'Music': 'info',
    'Utilities': 'warning',
    'Other': 'secondary'
}

def with_sidebar(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return render_template(f.__name__.replace('_route', '.html'), with_sidebar=True)
    return decorated_function

@routes.route("/")
def landing_route():
    return render_template("landing.html", with_sidebar=False)

@routes.route("/currency", methods=['GET', 'POST'])
def currency_route():
    user_email = session.get('user', {}).get('user_email')
    if not user_email:
        return redirect(url_for('routes.landing_route'))
    
    user = User.query.filter_by(email=user_email).first()
    if not user:
        return redirect(url_for('routes.landing_route'))
    
    if request.method == 'POST':
        new_currency = request.form.get('currency')
        if new_currency:
            user.currency = new_currency
            db.session.commit()
            return redirect(url_for('routes.home_logged_in_route'))
    
    return render_template("currency.html", with_sidebar=True, current_currency=user.currency)

@routes.route("/home_logged_in", methods=['GET', 'POST'])
def home_logged_in_route():
    if request.method == 'POST':
        return save_subscription()
    
    user_email = session.get('user', {}).get('user_email')
    if user_email:
        user = User.query.filter_by(email=user_email).first()
        if user:
            today = datetime.now().date()
            subscriptions = Subscription.query.filter_by(user_id=user.id).all()
            
            # Currency Conversion
            exchange_rates = get_exchange_rates(user.currency)
            
            # Currency Display Format
            currency_display = user.currency
            
            # Currency Symbols Mapping
            currency_symbols = {
                'USD': '$', 'EUR': '€', 'GBP': '£', 'JPY': '¥', 'CNY': '¥', 'AUD': 'A$', 'CAD': 'C$', 
                'CHF': 'CHF', 'HKD': 'HK$', 'SGD': 'S$', 'INR': '₹', 'BRL': 'R$', 'RUB': '₽', 'ZAR': 'R',
                'MXN': '$', 'AED': 'د.إ', 'THB': '฿', 'TRY': '₺', 'NZD': 'NZ$', 'PLN': 'zł', 'NOK': 'kr',
                'DKK': 'kr', 'ILS': '₪', 'MYR': 'RM', 'IDR': 'Rp', 'PHP': '₱', 'CZK': 'Kč', 'HUF': 'Ft', 'CLP': '$'
            }
            
            # Convert Subscriptions and Calculate Monthly Cost
            converted_subscriptions = []
            total_monthly_cost = 0
            annual_cost = 0
            category_annual_costs = {}
            
            
            
            for sub in subscriptions:
                converted_sub = sub.__dict__.copy()
                # Convert cost to user's currency based on original currency
                if (sub.original_currency or 'USD') == user.currency:
                    base_cost = float(sub.cost)
                else:
                    base_cost = float(sub.cost) * (float(exchange_rates.get(user.currency, 1)) / float(exchange_rates.get(sub.original_currency or 'USD', 1)))
                converted_cost = base_cost
                
                # Calculate monthly cost based on billing cycle
                if sub.billing_cycle == 'weekly':
                    monthly_cost = converted_cost * 4
                elif sub.billing_cycle == 'monthly':
                    monthly_cost = converted_cost
                elif sub.billing_cycle == 'quarterly':
                    monthly_cost = converted_cost / 3
                elif sub.billing_cycle == 'sixMonths':
                    monthly_cost = converted_cost / 6
                elif sub.billing_cycle == 'yearly':
                    monthly_cost = converted_cost / 12
                else:
                    monthly_cost = converted_cost
                sub_annual_cost = monthly_cost * 12
                # Update category annual costs
                if sub.category not in category_annual_costs:
                    category_annual_costs[sub.category] = 0
                category_annual_costs[sub.category] += sub_annual_cost
                
                # Update totals
                annual_cost += sub_annual_cost
                total_monthly_cost += monthly_cost
                
                # Store converted values
                converted_sub['cost'] = round(monthly_cost, 2)
                converted_sub['currency_display'] = currency_display
                converted_subscriptions.append(converted_sub)
            
            # Category Breakdown for monthly view
            category_breakdown = {}
            for sub in converted_subscriptions:
                category_breakdown[sub['category']] = category_breakdown.get(sub['category'], 0) + sub['cost']
            
            # Add currency display to category breakdown
            category_breakdown['currency_display'] = currency_display
            
            # Use pre-calculated annual costs per category
            category_annual_breakdown = {k: round(v, 2) for k, v in category_annual_costs.items()}
            
            
            # Upcoming Payments
            upcoming_payments = []
            for sub in subscriptions:
                days_until_billing = (sub.billing_date - today).days
                
                if days_until_billing <= 0:
                    urgency = 'overdue'
                elif days_until_billing <= 7:
                    urgency = 'soon'
                else:
                    urgency = 'upcoming'
                
                # Convert cost: if subscription's original currency matches user's default, use original cost; otherwise, convert
                if (sub.original_currency or 'USD') == user.currency:
                    converted_cost = float(sub.cost)
                else:
                    converted_cost = round(float(sub.cost) * (float(exchange_rates.get(user.currency, 1)) / float(exchange_rates.get(sub.original_currency or 'USD', 1))), 2)
                
                upcoming_payments.append({
                    'id': str(sub.id),
                    'name': sub.name,
                    'billing_date': sub.billing_date,
                    'days_until_billing': days_until_billing,
                    'urgency': urgency,
                    'cost': round(converted_cost, 2),
                    'currency_display': currency_display,
                    'auto_renew': sub.auto_renew
                })
            
            upcoming_payments.sort(key=lambda x: x['billing_date'])
            
        else:
            converted_subscriptions = []
            total_monthly_cost = 0
            category_breakdown = {}
            upcoming_payments = []
            annual_cost = 0
            category_annual_breakdown = {}
    else:
        converted_subscriptions = []
        total_monthly_cost = 0
        category_breakdown = {}
        upcoming_payments = []
        annual_cost = 0
        category_annual_breakdown = {}
    
    # Check if it's an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.headers.get('Accept') == 'application/json':
        return jsonify({
            'subscriptions': [
                {
                    'id': sub['id'],
                    'name': sub['name'],
                    'category': sub['category'],
                    'cost': sub['cost'],
                    'billing_date': sub['billing_date'].strftime('%Y-%m-%d') if isinstance(sub['billing_date'], datetime) else sub['billing_date']
                } for sub in converted_subscriptions
            ],
            'total_monthly_cost': total_monthly_cost,
            'category_breakdown': category_breakdown,
            'upcoming_payments': upcoming_payments,
            'annual_cost': annual_cost,
            'category_annual_breakdown': category_annual_breakdown
        })
    
    return render_template("home_logged_in.html", 
                          with_sidebar=True, 
                          subscriptions=converted_subscriptions,
                          category_colors=category_colors,
                          total_monthly_cost=total_monthly_cost,
                          category_breakdown=category_breakdown,
                          upcoming_payments=upcoming_payments,
                          annual_cost=annual_cost,
                          category_annual_breakdown=category_annual_breakdown)

def save_subscription():
    if 'user' not in session or 'user_email' not in session['user']:
        return jsonify({"error": "User not authenticated"}), 401

    data = request.form
    name = data.get('name')
    category = data.get('category')
    cost = data.get('cost')
    billing_date_str = data.get('billingDate')
    notes = data.get('notes', '')
    billing_cycle = data.get('billingCycle', 'monthly')
    selected_currency = data.get('currency', 'USD')
    auto_renew = data.get('autoRenew', 'yes')
    set_reminder = data.get('setReminder', 'yes')

    if not name or not category or not cost or not billing_date_str:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        cost = float(cost)
        if cost <= 0:
            return jsonify({"error": "Cost must be a positive number"}), 400

        billing_date = datetime.strptime(billing_date_str, '%Y-%m-%d').date()

        user_email = session['user']['user_email']
        user = User.query.filter_by(email=user_email).first()

        new_subscription = Subscription(
            user_id=user.id,
            name=name,
            category=category,
            cost=cost,  # Store original cost without conversion
            billing_date=billing_date,
            notes=notes,
            billing_cycle=billing_cycle,
            original_currency=selected_currency,  # Store original currency
            auto_renew=auto_renew,
            set_reminder=set_reminder
        )

        db.session.add(new_subscription)
        db.session.commit()

        return jsonify({"message": "Subscription added successfully"}), 201

    except ValueError as e:
        return jsonify({"error": "Invalid input format"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred while saving the subscription"}), 500

@routes.route("/subscription/<int:subscription_id>", methods=['GET', 'PUT', 'DELETE', 'POST'])
def subscription_route(subscription_id):
    if 'user' not in session or 'user_email' not in session['user']:
        return jsonify({"error": "User not authenticated"}), 401

    user_email = session['user']['user_email']
    user = User.query.filter_by(email=user_email).first()
    
    # Ensure the user owns the subscription
    subscription = Subscription.query.filter_by(id=subscription_id, user_id=user.id).first()

    if not subscription:
        return jsonify({"error": "Subscription not found"}), 404

    if request.method == 'POST':
        try:
            # Verify subscription exists
            if not subscription:
                return jsonify({"error": "Subscription not found"}), 404
            
            # Calculate new billing date based on billing cycle
            today = datetime.now().date()
            if subscription.billing_cycle == 'weekly':
                subscription.billing_date = today + timedelta(days=7)
            elif subscription.billing_cycle == 'monthly':
                # Add one month
                next_month = today.replace(day=1) + timedelta(days=32)
                subscription.billing_date = next_month.replace(day=min(today.day, (next_month.replace(day=1) - timedelta(days=1)).day))
            elif subscription.billing_cycle == 'quarterly':
                # Add three months
                next_quarter = today.replace(day=1)
                for _ in range(3):
                    next_quarter = (next_quarter + timedelta(days=32)).replace(day=1)
                subscription.billing_date = next_quarter.replace(day=min(today.day, (next_quarter.replace(day=1) - timedelta(days=1)).day))
            elif subscription.billing_cycle == 'sixMonths':
                # Add six months
                next_six_months = today.replace(day=1)
                for _ in range(6):
                    next_six_months = (next_six_months + timedelta(days=32)).replace(day=1)
                subscription.billing_date = next_six_months.replace(day=min(today.day, (next_six_months.replace(day=1) - timedelta(days=1)).day))
            elif subscription.billing_cycle == 'yearly':
                # Add one year
                subscription.billing_date = today.replace(year=today.year + 1)

            db.session.commit()
            return jsonify({"message": "Payment confirmed successfully", "new_billing_date": subscription.billing_date.strftime('%Y-%m-%d')}), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"An error occurred while confirming payment: {str(e)}"}), 500

    elif request.method == 'GET':
        # Get exchange rates for user's currency
        exchange_rates = get_exchange_rates(user.currency)
        
        # Convert cost to user's currency, but use original currency's cost
        converted_cost = round(float(subscription.cost) * float(exchange_rates.get(subscription.original_currency or 'USD', 1)), 2)
        
        return jsonify({
            'id': subscription.id,
            'name': subscription.name,
            'category': subscription.category,
            'cost': float(subscription.cost),  # Return original cost
            'billing_date': subscription.billing_date.strftime('%Y-%m-%d'),
            'notes': subscription.notes,
            'currency': subscription.original_currency or 'USD',
            'billing_cycle': subscription.billing_cycle,
            'auto_renew': subscription.auto_renew,
            'set_reminder': subscription.set_reminder
        })

    elif request.method == 'PUT':
        data = request.form
        name = data.get('name')
        category = data.get('category')
        cost = data.get('cost')
        billing_date_str = data.get('billingDate')
        notes = data.get('notes', '')
        currency = data.get('currency', 'USD')
        billing_cycle = data.get('billingCycle', 'monthly')
        auto_renew = data.get('autoRenew', 'yes')
        set_reminder = data.get('setReminder', 'yes')

        if not name or not category or not cost or not billing_date_str:
            return jsonify({"error": "Missing required fields"}), 400

        try:
            cost = float(cost)
            if cost <= 0:
                return jsonify({"error": "Cost must be a positive number"}), 400

            billing_date = datetime.strptime(billing_date_str, '%Y-%m-%d').date()

            subscription.name = name
            subscription.category = category
            subscription.cost = cost  # Store original cost without conversion
            subscription.billing_date = billing_date
            subscription.notes = notes
            subscription.original_currency = currency  # Store original currency
            subscription.billing_cycle = billing_cycle
            subscription.auto_renew = auto_renew
            subscription.set_reminder = set_reminder

            db.session.commit()
            return jsonify({
                "message": "Subscription updated successfully", 
                "subscription": {
                    "id": subscription.id,
                    "name": subscription.name,
                    "category": subscription.category,
                    "cost": float(cost),  # Return original cost
                    "billing_date": subscription.billing_date.strftime('%Y-%m-%d'),
                    "notes": subscription.notes,
                    "currency": subscription.original_currency or 'USD',
                    "billing_cycle": subscription.billing_cycle,
                    "auto_renew": subscription.auto_renew,
                    "set_reminder": subscription.set_reminder
                }
            }), 200

        except ValueError as e:
            return jsonify({"error": "Invalid input format"}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "An error occurred while updating the subscription"}), 500
    elif request.method == 'DELETE':
        try:
            db.session.delete(subscription)
            db.session.commit()
            return jsonify({"message": "Subscription deleted successfully"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "An error occurred while deleting the subscription"}), 500


def get_exchange_rates(target_currency):
    # Fallback exchange rates (updated periodically)
    fallback_rates = {
        'USD': 1.0, 'EUR': 0.92, 'GBP': 0.79, 'JPY': 149.50, 'CAD': 1.35, 
        'AUD': 1.52, 'CHF': 0.88, 'CNY': 7.23, 'HKD': 7.83, 'SGD': 1.35,
        'INR': 83.20, 'BRL': 4.95, 'RUB': 81.50, 'ZAR': 18.90, 'MXN': 17.20,
        'AED': 3.67, 'THB': 35.50, 'TRY': 30.50, 'NZD': 1.62, 'PLN': 4.20,
        'NOK': 10.70, 'DKK': 6.90, 'ILS': 3.70, 'MYR': 4.70, 'IDR': 15500,
        'PHP': 56.50, 'CZK': 22.50, 'HUF': 360, 'CLP': 870
    }
    
    try:
        # Attempt to fetch live rates from an API
        api_key = os.environ.get('EXCHANGE_RATE_API_KEY')
        if api_key:
            response = requests.get(f'https://openexchangerates.org/api/latest.json?app_id={api_key}&base=USD')
            if response.status_code == 200:
                rates = response.json()['rates']
                return {currency: rates.get(currency, fallback_rates.get(currency, 1)) for currency in fallback_rates}
    except Exception:
        pass
    
    # Return fallback rates if API call fails
    return fallback_rates