from src.models.user import db

class ClientConfig(db.Model):
    __tablename__ = 'client_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(255), nullable=False, unique=True)
    client_email = db.Column(db.String(255), nullable=True)
    
    # Taxas para cartão de crédito (1x a 18x)
    credit_1x = db.Column(db.Float, default=3.5)
    credit_2x = db.Column(db.Float, default=4.0)
    credit_3x = db.Column(db.Float, default=4.5)
    credit_4x = db.Column(db.Float, default=5.0)
    credit_5x = db.Column(db.Float, default=5.5)
    credit_6x = db.Column(db.Float, default=6.0)
    credit_7x = db.Column(db.Float, default=6.5)
    credit_8x = db.Column(db.Float, default=7.0)
    credit_9x = db.Column(db.Float, default=7.5)
    credit_10x = db.Column(db.Float, default=8.0)
    credit_11x = db.Column(db.Float, default=8.5)
    credit_12x = db.Column(db.Float, default=9.0)
    credit_13x = db.Column(db.Float, default=9.5)
    credit_14x = db.Column(db.Float, default=10.0)
    credit_15x = db.Column(db.Float, default=10.5)
    credit_16x = db.Column(db.Float, default=11.0)
    credit_17x = db.Column(db.Float, default=11.5)
    credit_18x = db.Column(db.Float, default=12.0)
    
    # Taxa para cartão de débito
    debit_rate = db.Column(db.Float, default=2.5)
    
    # Taxa para PIX
    pix_rate = db.Column(db.Float, default=1.0)
    
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    def to_dict(self):
        return {
            'id': self.id,
            'client_name': self.client_name,
            'client_email': self.client_email,
            'credit_rates': {
                '1x': self.credit_1x,
                '2x': self.credit_2x,
                '3x': self.credit_3x,
                '4x': self.credit_4x,
                '5x': self.credit_5x,
                '6x': self.credit_6x,
                '7x': self.credit_7x,
                '8x': self.credit_8x,
                '9x': self.credit_9x,
                '10x': self.credit_10x,
                '11x': self.credit_11x,
                '12x': self.credit_12x,
                '13x': self.credit_13x,
                '14x': self.credit_14x,
                '15x': self.credit_15x,
                '16x': self.credit_16x,
                '17x': self.credit_17x,
                '18x': self.credit_18x,
            },
            'debit_rate': self.debit_rate,
            'pix_rate': self.pix_rate,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_rate_for_payment(self, payment_type, installments=1):
        """Retorna a taxa configurada para um tipo de pagamento específico"""
        if payment_type.lower() == 'pix':
            return self.pix_rate
        elif payment_type.lower() == 'débito':
            return self.debit_rate
        elif payment_type.lower() == 'crédito':
            # Mapear número de parcelas para o atributo correto
            rate_attr = f'credit_{installments}x'
            return getattr(self, rate_attr, self.credit_1x)
        else:
            return 0.0

