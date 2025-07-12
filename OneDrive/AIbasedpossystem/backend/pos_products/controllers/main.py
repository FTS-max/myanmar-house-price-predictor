# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
import werkzeug
import json
from odoo.tools.image import image_data_uri

class PosProductController(http.Controller):
    
    def _validate_api_key(self, api_key):
        """Validate API key and return shop"""
        if not api_key:
            return None
        
        shop = request.env['pos.shop'].sudo().search([('api_key', '=', api_key)], limit=1)
        return shop if shop else None
    
    @http.route('/api/v1/products', type='http', auth='none', methods=['GET'], csrf=False)
    def get_products(self, **kwargs):
        """Get products for a shop"""
        api_key = kwargs.get('api_key') or request.httprequest.headers.get('X-API-Key')
        shop = self._validate_api_key(api_key)
        
        if not shop:
            return werkzeug.wrappers.Response(
                status=401,
                content_type='application/json; charset=utf-8',
                response=json.dumps({'error': 'Invalid API Key'})
            )
        
        # Get query parameters
        limit = min(int(kwargs.get('limit', 100)), 100)  # Max 100 products per request
        offset = int(kwargs.get('offset', 0))
        category_id = kwargs.get('category_id', False)
        search = kwargs.get('search', '')
        
        # Build domain
        domain = [('shop_id', '=', shop.id), ('pos_available', '=', True)]
        if category_id:
            domain.append(('shop_category_id', '=', int(category_id)))
        if search:
            domain.append(('name', 'ilike', search))
        
        # Get products
        Product = request.env['product.template'].sudo()
        products = Product.search(domain, limit=limit, offset=offset, order='pos_sequence, name')
        total_count = Product.search_count(domain)
        
        result = []
        for product in products:
            # Get current price
            current_price = product.get_current_price()
            
            # Get additional images
            additional_images = []
            for img in product.pos_image_ids:
                if img.image:
                    additional_images.append({
                        'id': img.id,
                        'name': img.name or '',
                        'image_url': image_data_uri(img.image)
                    })
            
            # Build product data
            product_data = {
                'id': product.id,
                'name': product.name,
                'default_code': product.default_code or '',
                'shop_sku': product.shop_sku or '',
                'barcode': product.barcode or '',
                'category_id': product.shop_category_id.id if product.shop_category_id else False,
                'category_name': product.shop_category_id.name if product.shop_category_id else '',
                'list_price': product.list_price,
                'list_price_shop': product.list_price_shop or product.list_price,
                'current_price': current_price,
                'discount_price': product.discount_price or 0.0,
                'on_discount': bool(product.discount_price and 
                                   product.discount_start and 
                                   product.discount_end),
                'currency': product.currency_id.name,
                'currency_symbol': product.currency_id.symbol,
                'pos_description': product.pos_description or '',
                'description': product.description_sale or '',
                'ai_description': product.ai_description or '',
                'ai_tags': product.ai_tags or '',
                'image_url': image_data_uri(product.image_1920) if product.image_1920 else '',
                'additional_images': additional_images,
                'pos_sequence': product.pos_sequence,
                'type': product.type,
                'uom': product.uom_id.name,
                'weight': product.weight,
                'volume': product.volume,
                'has_variants': product.product_variant_count > 1 and product.pos_use_variants,
            }
            
            result.append(product_data)
        
        return werkzeug.wrappers.Response(
            status=200,
            content_type='application/json; charset=utf-8',
            response=json.dumps({
                'total_count': total_count,
                'offset': offset,
                'limit': limit,
                'products': result
            })
        )
    
    @http.route('/api/v1/product/<int:product_id>', type='http', auth='none', methods=['GET'], csrf=False)
    def get_product(self, product_id, **kwargs):
        """Get a specific product"""
        api_key = kwargs.get('api_key') or request.httprequest.headers.get('X-API-Key')
        shop = self._validate_api_key(api_key)
        
        if not shop:
            return werkzeug.wrappers.Response(
                status=401,
                content_type='application/json; charset=utf-8',
                response=json.dumps({'error': 'Invalid API Key'})
            )
        
        # Get product
        product = request.env['product.template'].sudo().search(
            [('id', '=', product_id), ('shop_id', '=', shop.id)], limit=1)
        
        if not product:
            return werkzeug.wrappers.Response(
                status=404,
                content_type='application/json; charset=utf-8',
                response=json.dumps({'error': 'Product not found'})
            )
        
        # Get current price
        current_price = product.get_current_price()
        
        # Get additional images
        additional_images = []
        for img in product.pos_image_ids:
            if img.image:
                additional_images.append({
                    'id': img.id,
                    'name': img.name or '',
                    'image_url': image_data_uri(img.image)
                })
        
        # Get variants
        variants = []
        if product.product_variant_count > 1 and product.pos_use_variants:
            for variant in product.product_variant_ids:
                variant_data = {
                    'id': variant.id,
                    'name': variant.name,
                    'default_code': variant.default_code or '',
                    'barcode': variant.barcode or '',
                    'attributes': [],
                    'price_extra': variant.lst_price - product.list_price if variant.lst_price != product.list_price else 0,
                }
                
                # Get attributes
                for attr_value in variant.product_template_attribute_value_ids:
                    variant_data['attributes'].append({
                        'attribute_id': attr_value.attribute_id.id,
                        'attribute_name': attr_value.attribute_id.name,
                        'value_id': attr_value.product_attribute_value_id.id,
                        'value_name': attr_value.product_attribute_value_id.name,
                    })
                
                variants.append(variant_data)
        
        # Build product data
        product_data = {
            'id': product.id,
            'name': product.name,
            'default_code': product.default_code or '',
            'shop_sku': product.shop_sku or '',
            'barcode': product.barcode or '',
            'category_id': product.shop_category_id.id if product.shop_category_id else False,
            'category_name': product.shop_category_id.name if product.shop_category_id else '',
            'list_price': product.list_price,
            'list_price_shop': product.list_price_shop or product.list_price,
            'current_price': current_price,
            'discount_price': product.discount_price or 0.0,
            'discount_start': product.discount_start.isoformat() if product.discount_start else False,
            'discount_end': product.discount_end.isoformat() if product.discount_end else False,
            'on_discount': bool(product.discount_price and 
                               product.discount_start and 
                               product.discount_end),
            'currency': product.currency_id.name,
            'currency_symbol': product.currency_id.symbol,
            'pos_description': product.pos_description or '',
            'description': product.description_sale or '',
            'ai_description': product.ai_description or '',
            'ai_tags': product.ai_tags or '',
            'image_url': image_data_uri(product.image_1920) if product.image_1920 else '',
            'additional_images': additional_images,
            'pos_sequence': product.pos_sequence,
            'type': product.type,
            'uom': product.uom_id.name,
            'weight': product.weight,
            'volume': product.volume,
            'has_variants': product.product_variant_count > 1 and product.pos_use_variants,
            'variants': variants,
        }
        
        return werkzeug.wrappers.Response(
            status=200,
            content_type='application/json; charset=utf-8',
            response=json.dumps(product_data)
        )
    
    @http.route('/api/v1/product/categories', type='http', auth='none', methods=['GET'], csrf=False)
    def get_product_categories(self, **kwargs):
        """Get product categories for a shop"""
        api_key = kwargs.get('api_key') or request.httprequest.headers.get('X-API-Key')
        shop = self._validate_api_key(api_key)
        
        if not shop:
            return werkzeug.wrappers.Response(
                status=401,
                content_type='application/json; charset=utf-8',
                response=json.dumps({'error': 'Invalid API Key'})
            )
        
        # Get categories
        categories = request.env['pos.product.category'].sudo().search(
            [('shop_id', '=', shop.id), ('pos_available', '=', True)],
            order='pos_sequence, name')
        
        result = []
        for category in categories:
            category_data = {
                'id': category.id,
                'name': category.name,
                'complete_name': category.complete_name,
                'parent_id': category.parent_id.id if category.parent_id else False,
                'child_ids': category.child_id.ids,
                'sequence': category.pos_sequence,
                'product_count': category.product_count,
                'image_url': image_data_uri(category.image) if category.image else '',
                'color': category.color or 0,
            }
            result.append(category_data)
        
        return werkzeug.wrappers.Response(
            status=200,
            content_type='application/json; charset=utf-8',
            response=json.dumps(result)
        )