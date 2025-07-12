# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
import werkzeug
import json

class PosShopController(http.Controller):
    
    def _validate_api_key(self, api_key):
        """Validate API key and return shop"""
        if not api_key:
            return None
        
        shop = request.env['pos.shop'].sudo().search([('api_key', '=', api_key)], limit=1)
        return shop if shop else None
    
    @http.route('/api/v1/shop/info', type='http', auth='none', methods=['GET'], csrf=False)
    def get_shop_info(self, **kwargs):
        """Get shop information"""
        api_key = kwargs.get('api_key') or request.httprequest.headers.get('X-API-Key')
        shop = self._validate_api_key(api_key)
        
        if not shop:
            return werkzeug.wrappers.Response(
                status=401,
                content_type='application/json; charset=utf-8',
                response=json.dumps({'error': 'Invalid API Key'})
            )
        
        data = {
            'id': shop.id,
            'name': shop.name,
            'code': shop.code,
            'email': shop.email,
            'phone': shop.phone,
            'website': shop.website,
            'address': {
                'street': shop.street,
                'street2': shop.street2,
                'city': shop.city,
                'zip': shop.zip,
                'state': shop.state_id.name if shop.state_id else False,
                'country': shop.country_id.name if shop.country_id else False,
            },
            'owner': {
                'id': shop.owner_id.id,
                'name': shop.owner_id.name,
                'email': shop.owner_id.email,
            },
            'stats': {
                'product_count': shop.product_count,
                'order_count': shop.order_count,
            }
        }
        
        return werkzeug.wrappers.Response(
            status=200,
            content_type='application/json; charset=utf-8',
            response=json.dumps(data)
        )
    
    @http.route('/api/v1/shop/settings', type='http', auth='none', methods=['GET'], csrf=False)
    def get_shop_settings(self, **kwargs):
        """Get shop settings"""
        api_key = kwargs.get('api_key') or request.httprequest.headers.get('X-API-Key')
        shop = self._validate_api_key(api_key)
        
        if not shop:
            return werkzeug.wrappers.Response(
                status=401,
                content_type='application/json; charset=utf-8',
                response=json.dumps({'error': 'Invalid API Key'})
            )
        
        settings = request.env['pos.shop.settings'].sudo().search([('shop_id', '=', shop.id)], limit=1)
        if not settings:
            return werkzeug.wrappers.Response(
                status=404,
                content_type='application/json; charset=utf-8',
                response=json.dumps({'error': 'Settings not found'})
            )
        
        data = {
            'receipt': {
                'header': settings.receipt_header,
                'footer': settings.receipt_footer,
                'show_logo': settings.show_logo_on_receipt,
            },
            'tax': {
                'default_tax_id': settings.default_tax_id.id if settings.default_tax_id else False,
                'include_tax_in_price': settings.include_tax_in_price,
            },
            'ui': {
                'theme_color': settings.theme_color,
                'font_size': settings.font_size,
            },
            'operational': {
                'auto_print_receipt': settings.auto_print_receipt,
                'ask_customer_for_receipt': settings.ask_customer_for_receipt,
                'require_customer_for_order': settings.require_customer_for_order,
            },
            'integration': {
                'enable_api_access': settings.enable_api_access,
                'enable_ai_integration': settings.enable_ai_integration,
                'webhook_url': settings.webhook_url,
            }
        }
        
        return werkzeug.wrappers.Response(
            status=200,
            content_type='application/json; charset=utf-8',
            response=json.dumps(data)
        )