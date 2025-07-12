# AI-Based POS System Backend

This is the backend for an AI-based Point of Sale (POS) system built with Odoo 16. The system provides a multi-tenant architecture for managing shops, products, and sales.

## Project Structure

The backend consists of several Odoo modules:

- **pos_shop_core**: Core module for shop/tenant management
- **pos_products**: Product management module
- **pos_sales**: Sales and order management module

## Prerequisites

- Python 3.8, 3.9, or 3.10 (Odoo 16 is not fully compatible with Python 3.11+)
- PostgreSQL 12 or newer
- Node.js and npm (for web client)

## Installation

### 1. Set up a virtual environment

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate

# On Linux/Mac:
source venv/bin/activate
```

### 2. Install Odoo 16

Choose one of these methods:

#### Option A: Clone from GitHub

```bash
git clone https://github.com/odoo/odoo.git --depth=1 --branch=16.0 odoo16
cd odoo16
pip install -r requirements.txt
pip install -e .
```

#### Option B: Download the Windows installer

Download from the [official Odoo website](https://www.odoo.com/page/download)

### 3. Install project dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure PostgreSQL

1. Install PostgreSQL if not already installed
2. Create a database user named 'odoo' with password 'odoo'
3. Create a database named 'pos_system'

```sql
CREATE USER odoo WITH PASSWORD 'odoo';
ALTER USER odoo WITH CREATEDB;
CREATE DATABASE pos_system OWNER odoo;
```

## Configuration

The `odoo.conf` file contains the configuration for the Odoo server. Make sure the database connection details are correct.

## Running the Server

### First-time initialization

```bash
# If using GitHub clone
python /path/to/odoo16/odoo-bin -c odoo.conf -i pos_shop_core,pos_products,pos_sales --db-filter=pos_system

# If using installed package
odoo -c odoo.conf -i pos_shop_core,pos_products,pos_sales --db-filter=pos_system
```

### Regular startup

```bash
# If using GitHub clone
python /path/to/odoo16/odoo-bin -c odoo.conf

# If using installed package
odoo -c odoo.conf
```

## Accessing the System

Once the server is running, you can access the system at:

- Web interface: http://localhost:8069
- Default admin credentials: admin / admin

## API Endpoints

The system provides REST API endpoints for integration:

- `/api/v1/products` - Get products for a shop
- Additional endpoints are available in the controllers

## Troubleshooting

### Common Issues

1. **Module not found error**: Make sure the `addons_path` in `odoo.conf` points to the correct directory.

2. **Database connection error**: Verify PostgreSQL is running and the credentials in `odoo.conf` are correct.

3. **Port already in use**: Change the `http_port` in `odoo.conf` if port 8069 is already in use.

4. **Missing dependencies**: Run `pip install -r requirements.txt` to install all required packages.

## License

This project is licensed under the LGPL-3 - see the LICENSE file for details.