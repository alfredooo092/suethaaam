import csv
import io
from datetime import datetime
from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.machine import Machine, MachineConfig, Transaction

pagbank_bp = Blueprint('pagbank', __name__)

def parse_brazilian_float(value_str):
    """Converte string no formato brasileiro para float"""
    if not value_str or value_str.strip() == '':
        return 0.0
    try:
        # Remove espaços e substitui vírgula por ponto
        clean_value = value_str.strip().replace('.', '').replace(',', '.')
        return float(clean_value)
    except (ValueError, AttributeError):
        return 0.0

def parse_brazilian_date(date_str):
    """Converte string de data brasileira para datetime"""
    if not date_str or date_str.strip() == '':
        return None
    try:
        # Formato: DD/MM/YYYY HH:MM ou DD/MM/YYYY
        date_clean = date_str.strip()
        if ' ' in date_clean:
            return datetime.strptime(date_clean, '%d/%m/%Y %H:%M')
        else:
            return datetime.strptime(date_clean, '%d/%m/%Y')
    except (ValueError, AttributeError):
        return None

@pagbank_bp.route('/upload', methods=['POST'])
@pagbank_bp.route('/upload-csv', methods=['POST'])
def upload_csv():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'Nenhum arquivo enviado'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Nenhum arquivo selecionado'})
        
        # Ler conteúdo do arquivo
        content = file.read().decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(content), delimiter=';')  # Usar ponto e vírgula como delimitador
        
        # NÃO limpar dados existentes - apenas adicionar novos
        print("📊 Mantendo dados existentes e adicionando novos...")
        
        new_transactions = 0
        updated_machines = set()
        total_rows = 0
        skipped_duplicates = 0
        
        print(f"🔍 Iniciando processamento do CSV...")
        
        for row in csv_reader:
            total_rows += 1
            if total_rows <= 5:  # Mostrar apenas primeiras 5 linhas para debug
                print(f"📋 Linha {total_rows}: {list(row.keys())[:5]}...")  # Mostrar primeiras 5 colunas
                print(f"📋 Valores: {list(row.values())[:5]}...")  # Mostrar primeiros 5 valores
            
            machine_id = row.get('Identificação da Maquininha', '')  # Nome correto da coluna
            codigo_transacao = row.get('Código da Transação', '')
            
            if total_rows <= 5:  # Debug das primeiras linhas
                print(f"🏷️ Linha {total_rows} - Máquina: '{machine_id}', Código: '{codigo_transacao}'")
            
            if not machine_id or not codigo_transacao:
                if total_rows <= 10:  # Debug das primeiras 10 linhas
                    print(f"⚠️ Linha {total_rows} ignorada: máquina='{machine_id}', código='{codigo_transacao}'")
                continue
            
            # Verificar se a transação já existe para evitar duplicatas
            existing_transaction = Transaction.query.filter_by(codigo_transacao=codigo_transacao).first()
            if existing_transaction:
                skipped_duplicates += 1
                if skipped_duplicates <= 5:  # Log apenas as primeiras 5 duplicatas
                    print(f"🔄 Transação duplicada ignorada: {codigo_transacao}")
                continue
                
            machine_id = machine_id.strip()
            codigo_transacao = codigo_transacao.strip()
            
            if not machine_id or not codigo_transacao:
                if total_rows <= 10:  # Debug das primeiras 10 linhas
                    print(f"⚠️ Linha {total_rows} ignorada após strip: máquina='{machine_id}', código='{codigo_transacao}'")
                continue
            
            # Verificar se a transação já existe (removido para processar todas)
            # existing_transaction = Transaction.query.filter_by(codigo_transacao=codigo_transacao).first()
            # if existing_transaction:
            #     print(f"⚠️ Transação {codigo_transacao} já existe, pulando...")
            #     continue  # Pular transações duplicadas
            
            # Buscar ou criar máquina
            machine = Machine.query.filter_by(machine_id=machine_id).first()
            if not machine:
                client_name = row.get('Nome Cliente', '') or ''
                client_email = row.get('E-mail Cliente', '') or ''
                
                machine = Machine(
                    machine_id=machine_id,
                    client_name=client_name.strip(),
                    client_email=client_email.strip()
                )
                db.session.add(machine)
                db.session.flush()  # Para obter o ID
                
                # Criar configuração padrão
                config = MachineConfig(machine_id=machine_id)
                db.session.add(config)
            else:
                # Atualizar dados da máquina se necessário
                client_name = row.get('Nome Cliente', '') or machine.client_name
                client_email = row.get('E-mail Cliente', '') or machine.client_email
                
                machine.client_name = client_name.strip()
                machine.client_email = client_email.strip()
                machine.updated_at = datetime.utcnow()
            
            # Criar nova transação
            data_transacao_str = row.get('Data da Transação', '') or ''
            bandeira = row.get('Bandeira', '') or ''
            forma_pagamento = row.get('Forma de Pagamento', '') or ''
            parcelas = row.get('Parcela', '') or ''  # Nome correto da coluna
            valor_bruto_str = row.get('Valor Bruto', '0') or '0'
            valor_liquido_str = row.get('Valor Líquido', '0') or '0'
            status = row.get('Status', '') or ''
            
            # Calcular taxa PagBank (diferença entre bruto e líquido)
            valor_bruto = parse_brazilian_float(valor_bruto_str)
            valor_liquido = parse_brazilian_float(valor_liquido_str)
            valor_taxa = valor_bruto - valor_liquido
            
            transaction = Transaction(
                machine_id=machine_id,
                codigo_transacao=codigo_transacao,
                data_transacao=parse_brazilian_date(data_transacao_str),
                forma_pagamento=forma_pagamento.strip(),
                parcelas=parcelas.strip(),
                valor_bruto=valor_bruto,
                valor_taxa=valor_taxa,
                valor_liquido=valor_liquido,
                status=status.strip()
            )
            
            db.session.add(transaction)
            new_transactions += 1
            updated_machines.add(machine_id)
        
        db.session.commit()
        
        print(f"✅ Processamento concluído:")
        print(f"📊 Total de linhas processadas: {total_rows}")
        print(f"💾 Novas transações adicionadas: {new_transactions}")
        print(f"🔄 Transações duplicadas ignoradas: {skipped_duplicates}")
        print(f"🏷️ Máquinas atualizadas: {len(updated_machines)}")
        
        # Buscar todas as máquinas para retornar (incluindo as existentes)
        machines = Machine.query.all()
        machines_data = [machine.get_summary() for machine in machines]
        
        print(f"📈 Total de máquinas no sistema: {len(machines_data)}")
        
        return jsonify({
            'success': True,
            'clients': machines_data,
            'total_clients': len(machines_data),
            'new_transactions': new_transactions,
            'skipped_duplicates': skipped_duplicates,
            'updated_machines': len(updated_machines),
            'total_rows_processed': total_rows,
            'message': f'✅ Upload concluído! {new_transactions} novas transações adicionadas. Total: {len(machines_data)} máquinas no sistema ({skipped_duplicates} duplicatas ignoradas)'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Erro ao processar arquivo: {str(e)}'})

@pagbank_bp.route('/machines', methods=['GET'])
def get_machines():
    """Retorna todas as máquinas salvas"""
    try:
        machines = Machine.query.all()
        machines_data = [machine.get_summary() for machine in machines]
        
        return jsonify({
            'success': True,
            'clients': machines_data,
            'total_clients': len(machines_data)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@pagbank_bp.route('/client-config/<machine_id>', methods=['GET'])
@pagbank_bp.route('/api/client-config/<machine_id>', methods=['GET'])
def get_client_config(machine_id):
    try:
        print(f"📋 Carregando configurações para máquina: {machine_id}")
        config = MachineConfig.query.filter_by(machine_id=machine_id).first()
        
        if config:
            print(f"✅ Configuração encontrada para máquina {machine_id}")
            config_dict = config.to_dict()
            print(f"📊 Dados da configuração: {config_dict}")
            return jsonify(config_dict)
        else:
            print(f"⚠️ Nenhuma configuração encontrada para máquina {machine_id}, retornando padrão")
            # Retornar configuração padrão se não existir
            default_config = {
                'machine_id': machine_id,
                'credito_1x': 0.0, 'credito_2x': 0.0, 'credito_3x': 0.0, 'credito_4x': 0.0,
                'credito_5x': 0.0, 'credito_6x': 0.0, 'credito_7x': 0.0, 'credito_8x': 0.0,
                'credito_9x': 0.0, 'credito_10x': 0.0, 'credito_11x': 0.0, 'credito_12x': 0.0,
                'credito_13x': 0.0, 'credito_14x': 0.0, 'credito_15x': 0.0, 'credito_16x': 0.0,
                'credito_17x': 0.0, 'credito_18x': 0.0, 'debito': 0.0, 'pix': 0.0
            }
            return jsonify(default_config)
    except Exception as e:
        print(f"❌ Erro ao carregar configuração para máquina {machine_id}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@pagbank_bp.route('/client-config/<machine_id>', methods=['PUT'])
@pagbank_bp.route('/api/client-config/<machine_id>', methods=['PUT'])
def save_client_config(machine_id):
    try:
        data = request.get_json()
        print(f"💾 Salvando configurações para máquina {machine_id}: {data}")
        
        # Buscar ou criar configuração
        config = MachineConfig.query.filter_by(machine_id=machine_id).first()
        
        if not config:
            print(f"🆕 Criando nova configuração para máquina {machine_id}")
            config = MachineConfig(machine_id=machine_id)
            db.session.add(config)
        else:
            print(f"🔄 Atualizando configuração existente para máquina {machine_id}")
        
        # Atualizar configuração
        config.update_from_dict(data)
        
        db.session.commit()
        print(f"✅ Configuração salva com sucesso para máquina {machine_id}")
        
        return jsonify({
            'success': True,
            'config': config.to_dict(),
            'message': 'Configuração salva com sucesso!'
        })
        
    except Exception as e:
        print(f"❌ Erro ao salvar configuração para máquina {machine_id}: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})
@pagbank_bp.route('/transactions/<machine_id>', methods=['GET'])
@pagbank_bp.route('/api/transactions/<machine_id>', methods=['GET'])
def get_transactions(machine_id):
    try:
        print(f"🔍 Buscando transações para máquina: {machine_id}")
        
        # Buscar transações da máquina
        transactions = Transaction.query.filter_by(machine_id=machine_id).all()
        
        print(f"📊 Encontradas {len(transactions)} transações")
        
        transactions_data = []
        for transaction in transactions:
            transaction_data = {
                'data_transacao': transaction.data_transacao.isoformat() if transaction.data_transacao else None,
                'forma_pagamento': transaction.forma_pagamento or '',
                'parcela': transaction.parcelas or '',  # Usar 'parcelas' do banco
                'valor_bruto': float(transaction.valor_bruto) if transaction.valor_bruto else 0,
                'valor_taxa': float(transaction.valor_taxa) if transaction.valor_taxa else 0,
                'valor_liquido': float(transaction.valor_liquido) if transaction.valor_liquido else 0,
                'status': transaction.status or '',
                'codigo_transacao': transaction.codigo_transacao or '',
                'sua_taxa': 0,  # Será calculado no frontend
                'seu_lucro': 0  # Será calculado no frontend
            }
            transactions_data.append(transaction_data)
            
            if len(transactions_data) <= 3:  # Debug das primeiras 3 transações
                print(f"📋 Transação {len(transactions_data)}: {transaction_data}")
        
        print(f"✅ Retornando {len(transactions_data)} transações")
        return jsonify(transactions_data)
        
    except Exception as e:
        print(f"❌ Erro ao buscar transações: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@pagbank_bp.route('/calculate-profit/<machine_id>', methods=['POST'])
@pagbank_bp.route('/api/calculate-profit/<machine_id>', methods=['POST'])
def calculate_profit(machine_id):
    try:
        print(f"🧮 Calculando lucro para máquina: {machine_id}")
        
        # Buscar máquina e configuração
        machine = Machine.query.filter_by(machine_id=machine_id).first()
        if not machine:
            print(f"❌ Máquina {machine_id} não encontrada")
            return jsonify({'success': False, 'error': 'Máquina não encontrada'})
        
        config = MachineConfig.query.filter_by(machine_id=machine_id).first()
        if not config:
            print(f"❌ Configuração para máquina {machine_id} não encontrada")
            return jsonify({'success': False, 'error': 'Configuração não encontrada'})
        
        print(f"📊 Encontradas {len(machine.transactions)} transações")
        print(f"⚙️ Configuração carregada: 1x={config.credit_1x}%, débito={config.debit_rate}%, pix={config.pix_rate}%")
        
        # Calcular lucro para cada transação
        profit_data = []
        total_taxa_cliente = 0
        total_lucro = 0
        
        for transaction in machine.transactions:
            # Determinar taxa do cliente baseada no tipo de pagamento
            taxa_cliente_percent = 0
            
            if transaction.forma_pagamento and 'Crédito' in transaction.forma_pagamento:
                # Extrair número de parcelas
                parcelas_str = transaction.parcelas or '1x'
                if 'x' in parcelas_str:
                    parcelas_num = parcelas_str.replace('x', '').replace('Parcelado ', '').strip()
                    # Usar o nome correto do campo (credit_1x em vez de credit_1x)
                    taxa_attr = f'credit_{parcelas_num}x'
                    if hasattr(config, taxa_attr):
                        taxa_cliente_percent = getattr(config, taxa_attr, 0)
                        print(f"💳 Crédito {parcelas_num}x: {taxa_cliente_percent}%")
                else:
                    # Se não tem 'x', assumir 1x
                    taxa_cliente_percent = config.credit_1x
                    print(f"💳 Crédito 1x (padrão): {taxa_cliente_percent}%")
            elif transaction.forma_pagamento and 'Débito' in transaction.forma_pagamento:
                taxa_cliente_percent = config.debit_rate
                print(f"💰 Débito: {taxa_cliente_percent}%")
            elif transaction.forma_pagamento and 'PIX' in transaction.forma_pagamento:
                taxa_cliente_percent = config.pix_rate
                print(f"🏦 PIX: {taxa_cliente_percent}%")
            else:
                print(f"⚠️ Forma de pagamento não reconhecida: {transaction.forma_pagamento}")
            
            # Calcular valores
            valor_bruto = float(transaction.valor_bruto) if transaction.valor_bruto else 0
            valor_taxa_pagbank = float(transaction.valor_taxa) if transaction.valor_taxa else 0
            taxa_cliente_valor = valor_bruto * (taxa_cliente_percent / 100)
            lucro_transacao = taxa_cliente_valor - valor_taxa_pagbank
            
            total_taxa_cliente += taxa_cliente_valor
            total_lucro += lucro_transacao
            
            profit_data.append({
                'codigo_transacao': transaction.codigo_transacao,
                'data_transacao': transaction.data_transacao.isoformat() if transaction.data_transacao else None,
                'forma_pagamento': transaction.forma_pagamento,
                'parcela': transaction.parcelas,
                'valor_bruto': valor_bruto,
                'valor_taxa': valor_taxa_pagbank,
                'sua_taxa': taxa_cliente_valor,
                'seu_lucro': lucro_transacao,
                'taxa_cliente_percent': taxa_cliente_percent
            })
        
        print(f"✅ Cálculo concluído: Taxa cliente total=R${total_taxa_cliente:.2f}, Lucro total=R${total_lucro:.2f}")
        
        return jsonify({
            'success': True,
            'suas_taxas_total': total_taxa_cliente,
            'lucro_total': total_lucro,
            'margem_lucro': (total_lucro / total_taxa_cliente * 100) if total_taxa_cliente > 0 else 0,
            'transactions': profit_data
        })
        
    except Exception as e:
        print(f"❌ Erro ao calcular lucro: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'})

@pagbank_bp.route('/export-data/<machine_id>', methods=['GET'])
def export_data(machine_id):
    try:
        machine = Machine.query.filter_by(machine_id=machine_id).first()
        if not machine:
            return jsonify({'success': False, 'error': 'Máquina não encontrada'})
        
        # Preparar dados para exportação
        export_data = {
            'machine_info': machine.to_dict(),
            'config': machine.config.to_dict() if machine.config else None,
            'transactions': [t.to_dict() for t in machine.transactions],
            'summary': machine.get_summary()
        }
        
        return jsonify({
            'success': True,
            'data': export_data,
            'filename': f'machine_{machine_id}_export.json'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@pagbank_bp.route('/api/clear-test-data', methods=['POST'])
def clear_test_data():
    try:
        # Remover máquinas de teste
        test_machines = ['9999999999', '8888888888']
        for machine_id in test_machines:
            # Remover transações da máquina
            Transaction.query.filter_by(machine_id=machine_id).delete()
            # Remover configurações da máquina
            MachineConfig.query.filter_by(machine_id=machine_id).delete()
            # Remover máquina
            Machine.query.filter_by(machine_id=machine_id).delete()
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Dados de teste removidos com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})



