# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
import werkzeug
import json
import logging
import uuid
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class AuthController(http.Controller):
    
    @http.route('/api/auth/login', type='json', auth='none', methods=['POST'], csrf=False)
    def login(self, **kw):
        """Login endpoint for API authentication"""
        username = request.jsonrequest.get('username')
        password = request.jsonrequest.get('password')
        db = request.jsonrequest.get('db', 'pos_system')
        
        if not username or not password:
            return {'error': 'Username and password are required'}, 400
        
        # Authenticate user
        uid = request.session.authenticate(db, username, password)
        if not uid:
            return {'error': 'Invalid username or password'}, 401
        
        # Get user information
        user = request.env['res.users'].sudo().browse(uid)
        if not user:
            return {'error': 'User not found'}, 404
        
        # Check if user has POS role
        if not hasattr(user, 'pos_role'):
            return {'error': 'User does not have POS access'}, 403
        
        # Generate API token
        token = str(uuid.uuid4())
        
        # Store token in user record with expiration
        user.write({
            'api_token': token,
            'api_token_expiry': datetime.now() + timedelta(days=1)
        })
        
        # Get user's shops
        shop_ids = []
        active_shop_id = None
        
        if hasattr(user, 'pos_shop_ids') and user.pos_shop_ids:
            shop_ids = user.pos_shop_ids.ids
            if shop_ids and hasattr(user, 'pos_active_shop_id') and user.pos_active_shop_id:
                active_shop_id = user.pos_active_shop_id.id
        
        return {
            'token': token,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'pos_role': user.pos_role,
                'shop_ids': shop_ids,
                'active_shop_id': active_shop_id,
            }
        }
    
    @http.route('/api/auth/logout', type='json', auth='none', methods=['POST'], csrf=False)
    def logout(self, **kw):
        """Logout endpoint for API authentication"""
        # Get token from header
        auth_header = request.httprequest.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return {'error': 'Invalid authorization header'}, 401
        
        token = auth_header.split(' ')[1]
        
        # Find user with this token
        user = request.env['res.users'].sudo().search([('api_token', '=', token)], limit=1)
        if user:
            # Clear token
            user.write({
                'api_token': False,
                'api_token_expiry': False
            })
        
        return {'success': True}
    
    @http.route('/api/auth/user', type='json', auth='none', methods=['GET'], csrf=False)
    def get_current_user(self, **kw):
        """Get current user information"""
        # Get token from header
        auth_header = request.httprequest.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return {'error': 'Invalid authorization header'}, 401
        
        token = auth_header.split(' ')[1]
        
        # Find user with this token
        user = request.env['res.users'].sudo().search([('api_token', '=', token)], limit=1)
        if not user:
            return {'error': 'Invalid token'}, 401
        
        # Check token expiry
        if not user.api_token_expiry or user.api_token_expiry < datetime.now():
            return {'error': 'Token expired'}, 401
        
        # Get user's shops
        shop_ids = []
        active_shop_id = None
        
        if hasattr(user, 'pos_shop_ids') and user.pos_shop_ids:
            shop_ids = user.pos_shop_ids.ids
            if shop_ids and hasattr(user, 'pos_active_shop_id') and user.pos_active_shop_id:
                active_shop_id = user.pos_active_shop_id.id
        
        return {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'pos_role': user.pos_role,
            'shop_ids': shop_ids,
            'active_shop_id': active_shop_id,
        }
    
    @http.route('/api/auth/set_active_shop', type='json', auth='none', methods=['POST'], csrf=False)
    def set_active_shop(self, **kw):
        """Set active shop for current user"""
        # Get token from header
        auth_header = request.httprequest.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return {'error': 'Invalid authorization header'}, 401
        
        token = auth_header.split(' ')[1]
        
        # Find user with this token
        user = request.env['res.users'].sudo().search([('api_token', '=', token)], limit=1)
        if not user:
            return {'error': 'Invalid token'}, 401
        
        # Check token expiry
        if not user.api_token_expiry or user.api_token_expiry < datetime.now():
            return {'error': 'Token expired'}, 401
        
        # Get shop ID from request
        shop_id = request.jsonrequest.get('shop_id')
        if not shop_id:
            return {'error': 'Shop ID is required'}, 400
        
        # Check if user has access to this shop
        if not hasattr(user, 'pos_shop_ids') or not user.pos_shop_ids or shop_id not in user.pos_shop_ids.ids:
            return {'error': 'User does not have access to this shop'}, 403
        
        # Set active shop
        shop = request.env['pos.shop'].sudo().browse(shop_id)
        if not shop:
            return {'error': 'Shop not found'}, 404
        
        user.write({'pos_active_shop_id': shop_id})
        
        return {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'pos_role': user.pos_role,
            'shop_ids': user.pos_shop_ids.ids if hasattr(user, 'pos_shop_ids') and user.pos_shop_ids else [],
            'active_shop_id': shop_id,
        }