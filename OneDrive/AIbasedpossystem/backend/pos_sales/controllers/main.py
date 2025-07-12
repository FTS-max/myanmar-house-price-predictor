# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo.exceptions import AccessError, ValidationError
import json
import logging
from odoo import fields

_logger = logging.getLogger(__name__)

class POSSalesController(http.Controller):
    
    def _validate_api_key(self, api_key):
        """Validate API key and return shop"""
        if not api_key:
            return {'success': False, 'error': 'API key is required'}, None
            
        shop = request.env['pos.shop'].sudo().search([('api_key', '=', api_key)], limit=1)
        if not shop:
            return {'success': False, 'error': 'Invalid API key'}, None
            
        return {'success': True}, shop
    
    @http.route('/api/pos/orders', type='http', auth='none', methods=['GET'], csrf=False)
    def get_orders(self, **kwargs):
        """Get orders for a shop"""
        api_key = kwargs.get('api_key')
        result, shop = self._validate_api_key(api_key)
        if not result['success']:
            return json.dumps(result)
        
        try:
            # Parse parameters
            limit = int(kwargs.get('limit', 20))
            offset = int(kwargs.get('offset', 0))
            order_by = kwargs.get('order_by', 'date_order desc')
            state = kwargs.get('state')
            date_from = kwargs.get('date_from')
            date_to = kwargs.get('date_to')
            customer_id = kwargs.get('customer_id')
            
            # Build domain
            domain = [('shop_id', '=', shop.id)]
            if state:
                domain.append(('state', '=', state))
            if date_from:
                domain.append(('date_order', '>=', date_from))
            if date_to:
                domain.append(('date_order', '<=', date_to))
            if customer_id:
                domain.append(('partner_id', '=', int(customer_id)))
            
            # Get orders
            orders = request.env['pos.order'].sudo().search(domain, limit=limit, offset=offset, order=order_by)
            total_count = request.env['pos.order'].sudo().search_count(domain)
            
            # Format response
            orders_data = []
            for order in orders:
                orders_data.append({
                    'id': order.id,
                    'name': order.name,
                    'external_id': order.external_id,
                    'date_order': order.date_order.isoformat() if order.date_order else False,
                    'state': order.state,
                    'amount_total': order.amount_total,
                    'amount_tax': order.amount_tax,
                    'amount_paid': order.amount_paid,
                    'receipt_number': order.receipt_number,
                    'customer': {
                        'id': order.partner_id.id,
                        'name': order.partner_id.name,
                    } if order.partner_id else False,
                    'user': {
                        'id': order.user_id.id,
                        'name': order.user_id.name,
                    },
                    'lines_count': len(order.lines),
                })
            
            return json.dumps({
                'success': True,
                'count': len(orders),
                'total_count': total_count,
                'orders': orders_data,
            })
            
        except Exception as e:
            _logger.exception("Error getting orders")
            return json.dumps({'success': False, 'error': str(e)})
    
    @http.route('/api/pos/orders/<string:external_id>', type='http', auth='none', methods=['GET'], csrf=False)
    def get_order(self, external_id, **kwargs):
        """Get order details"""
        api_key = kwargs.get('api_key')
        result, shop = self._validate_api_key(api_key)
        if not result['success']:
            return json.dumps(result)
        
        try:
            # Get order
            order = request.env['pos.order'].sudo().search([
                ('external_id', '=', external_id),
                ('shop_id', '=', shop.id)
            ], limit=1)
            
            if not order:
                return json.dumps({'success': False, 'error': 'Order not found'})
            
            # Format lines
            lines_data = []
            for line in order.lines:
                lines_data.append({
                    'id': line.id,
                    'product': {
                        'id': line.product_id.id,
                        'name': line.product_id.name,
                        'default_code': line.product_id.default_code,
                        'barcode': line.product_id.barcode,
                        'shop_sku': line.product_id.product_tmpl_id.shop_sku,
                    },
                    'name': line.name,
                    'qty': line.qty,
                    'price_unit': line.price_unit,
                    'discount': line.discount,
                    'price_subtotal': line.price_subtotal,
                    'price_subtotal_incl': line.price_subtotal_incl,
                })
            
            # Format payments
            payments_data = []
            for payment in order.payment_ids:
                payments_data.append({
                    'id': payment.id,
                    'name': payment.name,
                    'amount': payment.amount,
                    'payment_date': payment.payment_date.isoformat() if payment.payment_date else False,
                    'payment_method': {
                        'id': payment.payment_method_id.id,
                        'name': payment.payment_method_id.name,
                        'code': payment.payment_method_id.code,
                    },
                    'payment_status': payment.payment_status,
                    'transaction_id': payment.transaction_id,
                    'is_change': payment.is_change,
                })
            
            # Format order data
            order_data = {
                'id': order.id,
                'name': order.name,
                'external_id': order.external_id,
                'date_order': order.date_order.isoformat() if order.date_order else False,
                'state': order.state,
                'amount_total': order.amount_total,
                'amount_tax': order.amount_tax,
                'amount_paid': order.amount_paid,
                'amount_return': order.amount_return,
                'receipt_number': order.receipt_number,
                'pos_reference': order.pos_reference,
                'customer': {
                    'id': order.partner_id.id,
                    'name': order.partner_id.name,
                    'email': order.partner_id.email,
                    'phone': order.partner_id.phone,
                } if order.partner_id else False,
                'user': {
                    'id': order.user_id.id,
                    'name': order.user_id.name,
                },
                'session': {
                    'id': order.session_id.id,
                    'name': order.session_id.name,
                },
                'shop': {
                    'id': order.shop_id.id,
                    'name': order.shop_id.name,
                },
                'lines': lines_data,
                'payments': payments_data,
                'note': order.note,
                'invoice_state': order.invoice_state,
            }
            
            return json.dumps({
                'success': True,
                'order': order_data,
            })
            
        except Exception as e:
            _logger.exception("Error getting order details")
            return json.dumps({'success': False, 'error': str(e)})
    
    @http.route('/api/pos/orders', type='json', auth='none', methods=['POST'], csrf=False)
    def create_order(self, **kwargs):
        """Create a new order"""
        api_key = request.jsonrequest.get('api_key')
        result, shop = self._validate_api_key(api_key)
        if not result['success']:
            return result
        
        try:
            data = request.jsonrequest
            
            # Validate required fields
            if not data.get('lines'):
                return {'success': False, 'error': 'Order lines are required'}
            
            # Get or create session
            session_id = data.get('session_id')
            if not session_id:
                # Find an open session for the shop
                session = request.env['pos.session'].sudo().search([
                    ('shop_id', '=', shop.id),
                    ('state', '=', 'opened'),
                ], limit=1)
                
                if not session:
                    # Create a new session
                    user_id = data.get('user_id') or request.env.ref('base.user_admin').id
                    session = request.env['pos.session'].sudo().create({
                        'user_id': user_id,
                        'shop_id': shop.id,
                    })
                    session.sudo().action_open_session()
                
                session_id = session.id
            
            # Prepare order data
            order_vals = {
                'shop_id': shop.id,
                'session_id': session_id,
                'user_id': data.get('user_id') or request.env.ref('base.user_admin').id,
                'partner_id': data.get('partner_id'),
                'date_order': data.get('date_order') or fields.Datetime.now(),
                'note': data.get('note'),
                'external_id': data.get('external_id'),
            }
            
            # Create order
            order = request.env['pos.order'].sudo().create(order_vals)
            
            # Create order lines
            for line_data in data.get('lines', []):
                line_vals = {
                    'order_id': order.id,
                    'product_id': line_data.get('product_id'),
                    'qty': line_data.get('qty', 1),
                    'price_unit': line_data.get('price_unit'),
                    'discount': line_data.get('discount', 0),
                    'name': line_data.get('name'),
                }
                
                if not line_vals.get('name'):
                    product = request.env['product.product'].sudo().browse(line_data.get('product_id'))
                    line_vals['name'] = product.name
                
                request.env['pos.order.line'].sudo().create(line_vals)
            
            # Create payments
            for payment_data in data.get('payments', []):
                payment_vals = {
                    'order_id': order.id,
                    'amount': payment_data.get('amount'),
                    'payment_method_id': payment_data.get('payment_method_id'),
                    'payment_date': payment_data.get('payment_date') or fields.Datetime.now(),
                    'transaction_id': payment_data.get('transaction_id'),
                    'card_type': payment_data.get('card_type'),
                    'cardholder_name': payment_data.get('cardholder_name'),
                    'is_change': payment_data.get('is_change', False),
                }
                
                request.env['pos.payment'].sudo().create(payment_vals)
            
            # Mark as paid if fully paid
            if data.get('state') == 'paid' or data.get('auto_paid'):
                order.sudo().action_paid()
            
            # Mark as done if requested
            if data.get('state') == 'done':
                order.sudo().action_done()
            
            return {
                'success': True,
                'order_id': order.id,
                'name': order.name,
                'external_id': order.external_id,
                'receipt_number': order.receipt_number,
            }
            
        except Exception as e:
            _logger.exception("Error creating order")
            return {'success': False, 'error': str(e)}
    
    @http.route('/api/pos/sessions', type='http', auth='none', methods=['GET'], csrf=False)
    def get_sessions(self, **kwargs):
        """Get sessions for a shop"""
        api_key = kwargs.get('api_key')
        result, shop = self._validate_api_key(api_key)
        if not result['success']:
            return json.dumps(result)
        
        try:
            # Parse parameters
            limit = int(kwargs.get('limit', 20))
            offset = int(kwargs.get('offset', 0))
            state = kwargs.get('state')
            
            # Build domain
            domain = [('shop_id', '=', shop.id)]
            if state:
                domain.append(('state', '=', state))
            
            # Get sessions
            sessions = request.env['pos.session'].sudo().search(domain, limit=limit, offset=offset, order='id desc')
            total_count = request.env['pos.session'].sudo().search_count(domain)
            
            # Format response
            sessions_data = []
            for session in sessions:
                sessions_data.append({
                    'id': session.id,
                    'name': session.name,
                    'user': {
                        'id': session.user_id.id,
                        'name': session.user_id.name,
                    },
                    'start_at': session.start_at.isoformat() if session.start_at else False,
                    'stop_at': session.stop_at.isoformat() if session.stop_at else False,
                    'state': session.state,
                    'order_count': session.order_count,
                    'total_payments_amount': session.total_payments_amount,
                })
            
            return json.dumps({
                'success': True,
                'count': len(sessions),
                'total_count': total_count,
                'sessions': sessions_data,
            })
            
        except Exception as e:
            _logger.exception("Error getting sessions")
            return json.dumps({'success': False, 'error': str(e)})
    
    @http.route('/api/pos/sessions/<int:session_id>', type='http', auth='none', methods=['GET'], csrf=False)
    def get_session(self, session_id, **kwargs):
        """Get session details"""
        api_key = kwargs.get('api_key')
        result, shop = self._validate_api_key(api_key)
        if not result['success']:
            return json.dumps(result)
        
        try:
            # Get session
            session = request.env['pos.session'].sudo().search([
                ('id', '=', session_id),
                ('shop_id', '=', shop.id)
            ], limit=1)
            
            if not session:
                return json.dumps({'success': False, 'error': 'Session not found'})
            
            # Format orders
            orders_data = []
            for order in session.order_ids:
                orders_data.append({
                    'id': order.id,
                    'name': order.name,
                    'external_id': order.external_id,
                    'date_order': order.date_order.isoformat() if order.date_order else False,
                    'state': order.state,
                    'amount_total': order.amount_total,
                    'receipt_number': order.receipt_number,
                })
            
            # Format session data
            session_data = {
                'id': session.id,
                'name': session.name,
                'user': {
                    'id': session.user_id.id,
                    'name': session.user_id.name,
                },
                'shop': {
                    'id': session.shop_id.id,
                    'name': session.shop_id.name,
                },
                'start_at': session.start_at.isoformat() if session.start_at else False,
                'stop_at': session.stop_at.isoformat() if session.stop_at else False,
                'state': session.state,
                'cash_control': session.cash_control,
                'cash_register_balance_start': session.cash_register_balance_start,
                'cash_register_balance_end': session.cash_register_balance_end,
                'cash_register_balance_end_real': session.cash_register_balance_end_real,
                'cash_register_difference': session.cash_register_difference,
                'order_count': session.order_count,
                'total_payments_amount': session.total_payments_amount,
                'orders': orders_data,
                'note': session.note,
            }
            
            return json.dumps({
                'success': True,
                'session': session_data,
            })
            
        except Exception as e:
            _logger.exception("Error getting session details")
            return json.dumps({'success': False, 'error': str(e)})
    
    @http.route('/api/pos/sessions', type='json', auth='none', methods=['POST'], csrf=False)
    def create_session(self, **kwargs):
        """Create a new session"""
        api_key = request.jsonrequest.get('api_key')
        result, shop = self._validate_api_key(api_key)
        if not result['success']:
            return result
        
        try:
            data = request.jsonrequest
            
            # Check if there's already an open session for this shop
            if shop.limit_sessions:
                existing_session = request.env['pos.session'].sudo().search([
                    ('shop_id', '=', shop.id),
                    ('state', '=', 'opened'),
                ], limit=1)
                
                if existing_session:
                    return {
                        'success': False, 
                        'error': 'There is already an open session for this shop',
                        'session_id': existing_session.id,
                        'session_name': existing_session.name,
                    }
            
            # Prepare session data
            session_vals = {
                'shop_id': shop.id,
                'user_id': data.get('user_id') or request.env.ref('base.user_admin').id,
                'cash_control': data.get('cash_control', False),
                'cash_register_balance_start': data.get('cash_register_balance_start', 0.0),
                'note': data.get('note'),
            }
            
            # Create session
            session = request.env['pos.session'].sudo().create(session_vals)
            
            # Open session
            if data.get('auto_open', True):
                session.sudo().action_open_session()
            
            return {
                'success': True,
                'session_id': session.id,
                'name': session.name,
                'state': session.state,
            }
            
        except Exception as e:
            _logger.exception("Error creating session")
            return {'success': False, 'error': str(e)}
    
    @http.route('/api/pos/sessions/<int:session_id>/close', type='json', auth='none', methods=['POST'], csrf=False)
    def close_session(self, session_id, **kwargs):
        """Close a session"""
        api_key = request.jsonrequest.get('api_key')
        result, shop = self._validate_api_key(api_key)
        if not result['success']:
            return result
        
        try:
            data = request.jsonrequest
            
            # Get session
            session = request.env['pos.session'].sudo().search([
                ('id', '=', session_id),
                ('shop_id', '=', shop.id),
                ('state', '=', 'opened'),
            ], limit=1)
            
            if not session:
                return {'success': False, 'error': 'Session not found or not in opened state'}
            
            # Update cash control data if provided
            if session.cash_control and data.get('cash_register_balance_end_real') is not None:
                session.sudo().write({
                    'cash_register_balance_end_real': data.get('cash_register_balance_end_real'),
                })
            
            # Close session
            session.sudo().action_close_session()
            
            # Validate closing if requested
            if data.get('auto_validate', True):
                session.sudo().action_validate_closing()
            
            return {
                'success': True,
                'session_id': session.id,
                'name': session.name,
                'state': session.state,
            }
            
        except Exception as e:
            _logger.exception("Error closing session")
            return {'success': False, 'error': str(e)}
    
    @http.route('/api/pos/payment-methods', type='http', auth='none', methods=['GET'], csrf=False)
    def get_payment_methods(self, **kwargs):
        """Get payment methods for a shop"""
        api_key = kwargs.get('api_key')
        result, shop = self._validate_api_key(api_key)
        if not result['success']:
            return json.dumps(result)
        
        try:
            # Build domain
            domain = ['|', ('shop_id', '=', False), ('shop_id', '=', shop.id)]
            if kwargs.get('active_only', 'true').lower() == 'true':
                domain.append(('active', '=', True))
            
            # Get payment methods
            payment_methods = request.env['pos.payment.method'].sudo().search(domain, order='sequence, id')
            
            # Format response
            methods_data = []
            for method in payment_methods:
                methods_data.append({
                    'id': method.id,
                    'name': method.name,
                    'code': method.code,
                    'is_cash_count': method.is_cash_count,
                    'use_payment_terminal': method.use_payment_terminal,
                    'payment_terminal_provider': method.payment_terminal_provider,
                    'image': method.image.decode('utf-8') if method.image else False,
                })
            
            return json.dumps({
                'success': True,
                'count': len(methods_data),
                'payment_methods': methods_data,
            })
            
        except Exception as e:
            _logger.exception("Error getting payment methods")
            return json.dumps({'success': False, 'error': str(e)})
    
    @http.route('/api/pos/payments/<int:payment_id>', type='http', auth='none', methods=['GET'], csrf=False)
    def get_payment(self, payment_id, **kwargs):
        """Get payment details"""
        api_key = kwargs.get('api_key')
        result, shop = self._validate_api_key(api_key)
        if not result['success']:
            return json.dumps(result)
        
        try:
            # Get payment
            payment = request.env['pos.payment'].sudo().search([
                ('id', '=', payment_id),
                ('shop_id', '=', shop.id)
            ], limit=1)
            
            if not payment:
                return json.dumps({'success': False, 'error': 'Payment not found'})
            
            # Format payment data
            payment_data = {
                'id': payment.id,
                'name': payment.name,
                'amount': payment.amount,
                'payment_date': payment.payment_date.isoformat() if payment.payment_date else False,
                'payment_method': {
                    'id': payment.payment_method_id.id,
                    'name': payment.payment_method_id.name,
                    'code': payment.payment_method_id.code,
                },
                'order': {
                    'id': payment.order_id.id,
                    'name': payment.order_id.name,
                    'external_id': payment.order_id.external_id,
                },
                'payment_status': payment.payment_status,
                'transaction_id': payment.transaction_id,
                'card_type': payment.card_type,
                'cardholder_name': payment.cardholder_name,
                'is_change': payment.is_change,
                'note': payment.note,
            }
            
            return json.dumps({
                'success': True,
                'payment': payment_data,
            })
            
        except Exception as e:
            _logger.exception("Error getting payment details")
            return json.dumps({'success': False, 'error': str(e)})
    
    @http.route('/api/pos/payments/<int:payment_id>/reverse', type='json', auth='none', methods=['POST'], csrf=False)
    def reverse_payment(self, payment_id, **kwargs):
        """Reverse a payment"""
        api_key = request.jsonrequest.get('api_key')
        result, shop = self._validate_api_key(api_key)
        if not result['success']:
            return result
        
        try:
            # Get payment
            payment = request.env['pos.payment'].sudo().search([
                ('id', '=', payment_id),
                ('shop_id', '=', shop.id)
            ], limit=1)
            
            if not payment:
                return {'success': False, 'error': 'Payment not found'}
            
            # Reverse payment
            reversed_payment = payment.sudo().reverse_payment()
            
            return {
                'success': True,
                'payment_id': payment.id,
                'reversed_payment_id': reversed_payment.id,
                'message': 'Payment reversed successfully',
            }
            
        except Exception as e:
            _logger.exception("Error reversing payment")
            return {'success': False, 'error': str(e)}