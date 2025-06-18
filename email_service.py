"""
Serviço de Email para Wetland E-commerce
Integrado com o sistema de notificações
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    """Serviço centralizado para envio de emails."""
    
    def __init__(self):
        # Configurações do Gmail
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 465
        self.email_remetente = "leoaguiar727@gmail.com"
        self.senha_app = "oylxliozllrciqat"
        self.email_cliente = "leoaguiar727@gmail.com"  # Por enquanto mesmo email
        
    def enviar_email(self, destinatario, assunto, corpo_html, corpo_texto=None):
        """
        Envia um email.
        
        Args:
            destinatario (str): Email do destinatário
            assunto (str): Assunto do email
            corpo_html (str): Corpo do email em HTML
            corpo_texto (str): Corpo do email em texto (opcional)
        
        Returns:
            bool: True se enviado com sucesso, False caso contrário
        """
        try:
            # Criar mensagem
            msg = MIMEMultipart('alternative')
            msg["Subject"] = assunto
            msg["From"] = self.email_remetente
            msg["To"] = destinatario
            
            # Adicionar corpo em texto (se fornecido)
            if corpo_texto:
                parte_texto = MIMEText(corpo_texto, 'plain', 'utf-8')
                msg.attach(parte_texto)
            
            # Adicionar corpo em HTML
            parte_html = MIMEText(corpo_html, 'html', 'utf-8')
            msg.attach(parte_html)
            
            # Enviar email
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as servidor:
                servidor.login(self.email_remetente, self.senha_app)
                servidor.sendmail(self.email_remetente, destinatario, msg.as_string())
            
            logger.info(f"Email enviado com sucesso para {destinatario}: {assunto}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email para {destinatario}: {e}")
            return False
    
    def email_pedido_criado(self, order_data):
        """Envia email de confirmação de pedido criado."""
        order_id = order_data.get('order_id', 'N/A')
        
        assunto = f"🎉 Pedido Confirmado #{order_id} - Wetland E-commerce"
        
        corpo_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #10b981, #059669); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .order-info {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #10b981; }}
                .status-badge {{ background: #10b981; color: white; padding: 8px 16px; border-radius: 20px; font-weight: bold; }}
                .footer {{ text-align: center; color: #666; margin-top: 30px; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🛍️ Wetland E-commerce</h1>
                    <h2>Seu pedido foi confirmado!</h2>
                </div>
                
                <div class="content">
                    <h3>Olá! 👋</h3>
                    <p>Recebemos seu pedido e ele está sendo processado. Aqui estão os detalhes:</p>
                    
                    <div class="order-info">
                        <h4>📦 Informações do Pedido</h4>
                        <p><strong>Número do Pedido:</strong> #{order_id}</p>
                        <p><strong>Data:</strong> {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
                        <p><strong>Status:</strong> <span class="status-badge">Pendente</span></p>
                    </div>
                    
                    <h4>🚚 Próximos Passos</h4>
                    <ol>
                        <li><strong>Processamento:</strong> Estamos preparando seu pedido</li>
                        <li><strong>Pagamento:</strong> Aguardando confirmação</li>
                        <li><strong>Envio:</strong> Após confirmação do pagamento</li>
                        <li><strong>Entrega:</strong> Você receberá o código de rastreamento</li>
                    </ol>
                    
                    <p>💡 <strong>Dica:</strong> Você receberá atualizações por email a cada mudança de status!</p>
                </div>
                
                <div class="footer">
                    <p>Obrigado por escolher a Wetland E-commerce! 🌿</p>
                    <p><em>Este é um email automático, não responda.</em></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.enviar_email(self.email_cliente, assunto, corpo_html)
    
    def email_status_atualizado(self, order_data):
        """Envia email de atualização de status do pedido."""
        order_id = order_data.get('order_id', 'N/A')
        status = order_data.get('status', 'Desconhecido')
        
        # Mapear status para mensagens amigáveis
        status_messages = {
            'Pending': {
                'emoji': '⏳',
                'titulo': 'Pedido Recebido',
                'descricao': 'Seu pedido foi recebido e está sendo processado.',
                'cor': '#f59e0b'
            },
            'Paid': {
                'emoji': '💳',
                'titulo': 'Pagamento Confirmado',
                'descricao': 'Pagamento aprovado! Estamos preparando seu pedido para envio.',
                'cor': '#10b981'
            },
            'Shipped': {
                'emoji': '🚚',
                'titulo': 'Pedido Enviado',
                'descricao': 'Seu pedido foi enviado e está a caminho!',
                'cor': '#3b82f6'
            },
            'Delivered': {
                'emoji': '📦',
                'titulo': 'Pedido Entregue',
                'descricao': 'Seu pedido foi entregue com sucesso!',
                'cor': '#059669'
            }
        }
        
        status_info = status_messages.get(status, {
            'emoji': '📋',
            'titulo': 'Status Atualizado',
            'descricao': f'Status do pedido alterado para: {status}',
            'cor': '#6b7280'
        })
        
        assunto = f"{status_info['emoji']} {status_info['titulo']} - Pedido #{order_id}"
        
        corpo_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, {status_info['cor']}, #374151); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .status-update {{ background: white; padding: 25px; border-radius: 8px; margin: 20px 0; border-left: 4px solid {status_info['cor']}; }}
                .status-badge {{ background: {status_info['cor']}; color: white; padding: 10px 20px; border-radius: 25px; font-weight: bold; font-size: 16px; }}
                .timeline {{ margin: 20px 0; }}
                .timeline-item {{ padding: 10px 0; border-left: 2px solid #e5e7eb; margin-left: 20px; padding-left: 20px; }}
                .timeline-item.active {{ border-left-color: {status_info['cor']}; font-weight: bold; }}
                .footer {{ text-align: center; color: #666; margin-top: 30px; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{status_info['emoji']} Wetland E-commerce</h1>
                    <h2>{status_info['titulo']}</h2>
                </div>
                
                <div class="content">
                    <div class="status-update">
                        <div style="text-align: center; margin-bottom: 20px;">
                            <span class="status-badge">{status}</span>
                        </div>
                        
                        <h4>📦 Pedido #{order_id}</h4>
                        <p>{status_info['descricao']}</p>
                        <p><strong>Atualizado em:</strong> {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
                    </div>
                    
                    <h4>📈 Progresso do Pedido</h4>
                    <div class="timeline">
                        <div class="timeline-item {'active' if status == 'Pending' else ''}">⏳ Pedido Recebido</div>
                        <div class="timeline-item {'active' if status == 'Paid' else ''}">💳 Pagamento Confirmado</div>
                        <div class="timeline-item {'active' if status == 'Shipped' else ''}">🚚 Enviado</div>
                        <div class="timeline-item {'active' if status == 'Delivered' else ''}">📦 Entregue</div>
                    </div>
                    
                    <p>💬 <strong>Dúvidas?</strong> Entre em contato conosco através do nosso suporte!</p>
                </div>
                
                <div class="footer">
                    <p>Obrigado por escolher a Wetland E-commerce! 🌿</p>
                    <p><em>Este é um email automático, não responda.</em></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.enviar_email(self.email_cliente, assunto, corpo_html)

# Instância global do serviço de email
email_service = EmailService() 