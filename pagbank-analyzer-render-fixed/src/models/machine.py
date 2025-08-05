from src.models.user import db
from datetime import datetime

class Machine(db.Model):
    __tablename__ = 'machines'
    
    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    client_name = db.Column(db.String(200), nullable=False)
    client_email = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    transactions = db.relationship('Transaction', backref='machine', lazy=True, cascade='all, delete-orphan')
    config = db.relationship('MachineConfig', backref='machine', uselist=False, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'machine_id': self.machine_id,
            'client_name': self.client_name,
            'client_email': self.client_email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_summary(self):
        """Retorna resumo financeiro da máquina"""
        total_bruto = sum(t.valor_bruto for t in self.transactions if t.valor_bruto)
        total_taxa_pagbank = sum(t.valor_taxa for t in self.transactions if t.valor_taxa)
        total_liquido_pagbank = sum(t.valor_liquido for t in self.transactions if t.valor_liquido)
        
        return {
            'machine_id': self.machine_id,
            'client_name': self.client_name,
            'client_email': self.client_email,
            'total_transacoes': len(self.transactions),
            'valor_bruto_total': total_bruto,
            'valor_taxa_total': total_taxa_pagbank,
            'valor_liquido_total': total_liquido_pagbank
        }

class MachineConfig(db.Model):
    __tablename__ = 'machine_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.String(50), db.ForeignKey('machines.machine_id'), nullable=False, unique=True)
    
    # Taxas de crédito (1x até 18x)
    credit_1x = db.Column(db.Float, default=0.0)
    credit_2x = db.Column(db.Float, default=0.0)
    credit_3x = db.Column(db.Float, default=0.0)
    credit_4x = db.Column(db.Float, default=0.0)
    credit_5x = db.Column(db.Float, default=0.0)
    credit_6x = db.Column(db.Float, default=0.0)
    credit_7x = db.Column(db.Float, default=0.0)
    credit_8x = db.Column(db.Float, default=0.0)
    credit_9x = db.Column(db.Float, default=0.0)
    credit_10x = db.Column(db.Float, default=0.0)
    credit_11x = db.Column(db.Float, default=0.0)
    credit_12x = db.Column(db.Float, default=0.0)
    credit_13x = db.Column(db.Float, default=0.0)
    credit_14x = db.Column(db.Float, default=0.0)
    credit_15x = db.Column(db.Float, default=0.0)
    credit_16x = db.Column(db.Float, default=0.0)
    credit_17x = db.Column(db.Float, default=0.0)
    credit_18x = db.Column(db.Float, default=0.0)
    
    # Outras taxas
    debit_rate = db.Column(db.Float, default=0.0)
    pix_rate = db.Column(db.Float, default=0.0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Converte configuração para dicionário"""
        return {
            'machine_id': self.machine_id,
            'credito_1x': self.credit_1x,
            'credito_2x': self.credit_2x,
            'credito_3x': self.credit_3x,
            'credito_4x': self.credit_4x,
            'credito_5x': self.credit_5x,
            'credito_6x': self.credit_6x,
            'credito_7x': self.credit_7x,
            'credito_8x': self.credit_8x,
            'credito_9x': self.credit_9x,
            'credito_10x': self.credit_10x,
            'credito_11x': self.credit_11x,
            'credito_12x': self.credit_12x,
            'credito_13x': self.credit_13x,
            'credito_14x': self.credit_14x,
            'credito_15x': self.credit_15x,
            'credito_16x': self.credit_16x,
            'credito_17x': self.credit_17x,
            'credito_18x': self.credit_18x,
            'debito': self.debit_rate,
            'pix': self.pix_rate,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def update_from_dict(self, data):
        """Atualiza configuração a partir de dicionário"""
        print(f"🔧 Atualizando configuração com dados: {data}")
        
        # Atualizar taxas de crédito individuais (credito_1x, credito_2x, etc.)
        for i in range(1, 19):
            field_name = f'credito_{i}x'
            if field_name in data and data[field_name] is not None:
                setattr(self, f'credit_{i}x', float(data[field_name] or 0))
                print(f"✅ {field_name}: {data[field_name]}%")
        
        # Atualizar outras taxas
        if 'debito' in data and data['debito'] is not None:
            self.debit_rate = float(data['debito'] or 0)
            print(f"✅ débito: {data['debito']}%")
        
        if 'pix' in data and data['pix'] is not None:
            self.pix_rate = float(data['pix'] or 0)
            print(f"✅ pix: {data['pix']}%")
        
        # Compatibilidade com formato antigo
        if 'credit_rates' in data:
            for parcela, taxa in data['credit_rates'].items():
                if parcela in ['1x', '2x', '3x', '4x', '5x', '6x', '7x', '8x', '9x', '10x', 
                              '11x', '12x', '13x', '14x', '15x', '16x', '17x', '18x']:
                    setattr(self, f'credit_{parcela}', float(taxa or 0))
        
        if 'debit_rate' in data:
            self.debit_rate = float(data['debit_rate'] or 0)
        
        if 'pix_rate' in data:
            self.pix_rate = float(data['pix_rate'] or 0)
        
        self.updated_at = datetime.utcnow()

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.String(50), db.ForeignKey('machines.machine_id'), nullable=False)
    
    # Dados da transação
    codigo_transacao = db.Column(db.String(100), unique=True, nullable=False, index=True)
    data_transacao = db.Column(db.DateTime, nullable=False)
    data_liberacao = db.Column(db.DateTime)
    
    # Dados do pagamento
    bandeira = db.Column(db.String(50))
    forma_pagamento = db.Column(db.String(50))
    parcelas = db.Column(db.String(20))
    
    # Valores
    valor_bruto = db.Column(db.Float, nullable=False)
    valor_taxa = db.Column(db.Float, nullable=False)
    valor_liquido = db.Column(db.Float, nullable=False)
    
    # Status e outros dados
    status = db.Column(db.String(50))
    numero_cartao = db.Column(db.String(50))
    codigo_nsu = db.Column(db.String(50))
    codigo_autorizacao = db.Column(db.String(50))
    codigo_venda = db.Column(db.String(50))
    codigo_referencia = db.Column(db.String(50))
    nome_comprador = db.Column(db.String(200))
    email_comprador = db.Column(db.String(200))
    codigo_pix = db.Column(db.String(100))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'machine_id': self.machine_id,
            'codigo_transacao': self.codigo_transacao,
            'data': self.data_transacao.strftime('%d/%m/%Y %H:%M') if self.data_transacao else None,
            'data_liberacao': self.data_liberacao.strftime('%d/%m/%Y %H:%M') if self.data_liberacao else None,
            'bandeira': self.bandeira,
            'forma_pagamento': self.forma_pagamento,
            'parcelas': self.parcelas,
            'valor_bruto': self.valor_bruto,
            'valor_taxa_pagbank': self.valor_taxa,
            'valor_liquido': self.valor_liquido,
            'status': self.status,
            'numero_cartao': self.numero_cartao,
            'codigo_nsu': self.codigo_nsu,
            'codigo_autorizacao': self.codigo_autorizacao,
            'codigo_venda': self.codigo_venda,
            'codigo_referencia': self.codigo_referencia,
            'nome_comprador': self.nome_comprador,
            'email_comprador': self.email_comprador,
            'codigo_pix': self.codigo_pix,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

