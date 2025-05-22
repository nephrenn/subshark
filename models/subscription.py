from models.models import db

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    cost = db.Column(db.Numeric(10,2), nullable=False)
    billing_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text)
    billing_cycle = db.Column(db.String(20), default='monthly')
    original_currency = db.Column(db.String(3), nullable=True)
    auto_renew = db.Column(db.String(3), default='yes')
    set_reminder = db.Column(db.String(3), default='yes')

    user = db.relationship('User', backref=db.backref('subscriptions', lazy=True))