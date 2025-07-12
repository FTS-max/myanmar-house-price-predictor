#!/usr/bin/env python3
"""
Development script for Myanmar House Price Predictor.

Provides utilities for development, testing, and deployment.
"""

import asyncio
import sys
import os
from pathlib import Path
import subprocess
import argparse
from typing import List

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.config import settings
from app.database.database import init_database, close_database
from app.services.ml_service import MLModelManager


class DevTools:
    """Development tools and utilities."""
    
    def __init__(self):
        self.project_root = project_root
    
    async def setup_database(self):
        """Initialize database with tables."""
        print("🔧 Setting up database...")
        try:
            await init_database()
            print("✅ Database setup completed")
        except Exception as e:
            print(f"❌ Database setup failed: {e}")
            return False
        return True
    
    async def train_models(self):
        """Train ML models with sample data."""
        print("🤖 Training ML models...")
        try:
            ml_service = MLModelManager()
            await ml_service.initialize()
            print("✅ ML models training completed")
        except Exception as e:
            print(f"❌ ML models training failed: {e}")
            return False
        return True
    
    def run_tests(self, test_path: str = None, coverage: bool = False):
        """Run tests with optional coverage."""
        print("🧪 Running tests...")
        
        cmd = ["python", "-m", "pytest"]
        
        if coverage:
            cmd.extend(["--cov=app", "--cov-report=html", "--cov-report=term"])
        
        if test_path:
            cmd.append(test_path)
        else:
            cmd.append("tests/")
        
        cmd.extend(["-v", "--tb=short"])
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root)
            if result.returncode == 0:
                print("✅ Tests passed")
                if coverage:
                    print("📊 Coverage report generated in htmlcov/")
            else:
                print("❌ Tests failed")
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Test execution failed: {e}")
            return False
    
    def lint_code(self):
        """Run code linting and formatting."""
        print("🔍 Running code linting...")
        
        commands = [
            (["python", "-m", "black", "app/", "tests/", "scripts/"], "Black formatting"),
            (["python", "-m", "isort", "app/", "tests/", "scripts/"], "Import sorting"),
            (["python", "-m", "flake8", "app/", "tests/"], "Flake8 linting"),
            (["python", "-m", "mypy", "app/"], "Type checking")
        ]
        
        all_passed = True
        for cmd, description in commands:
            print(f"  Running {description}...")
            try:
                result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"  ✅ {description} passed")
                else:
                    print(f"  ❌ {description} failed:")
                    print(f"    {result.stdout}")
                    print(f"    {result.stderr}")
                    all_passed = False
            except Exception as e:
                print(f"  ❌ {description} execution failed: {e}")
                all_passed = False
        
        return all_passed
    
    def start_server(self, host: str = "0.0.0.0", port: int = 8000, reload: bool = True):
        """Start the development server."""
        print(f"🚀 Starting development server on {host}:{port}...")
        
        cmd = [
            "python", "-m", "uvicorn",
            "main:app",
            "--host", host,
            "--port", str(port)
        ]
        
        if reload:
            cmd.append("--reload")
        
        try:
            subprocess.run(cmd, cwd=self.project_root)
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")
        except Exception as e:
            print(f"❌ Server failed to start: {e}")
    
    def build_docker(self, tag: str = "myanmar-house-predictor:latest"):
        """Build Docker image."""
        print(f"🐳 Building Docker image: {tag}...")
        
        cmd = ["docker", "build", "-t", tag, "."]
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root)
            if result.returncode == 0:
                print(f"✅ Docker image built successfully: {tag}")
            else:
                print("❌ Docker build failed")
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Docker build execution failed: {e}")
            return False
    
    def generate_sample_data(self, count: int = 1000):
        """Generate sample property data for testing."""
        print(f"📊 Generating {count} sample property records...")
        
        try:
            # This would typically generate synthetic data
            # For now, we'll create a placeholder
            data_dir = self.project_root / "data"
            data_dir.mkdir(exist_ok=True)
            
            sample_file = data_dir / "sample_properties.json"
            
            import json
            import random
            from datetime import datetime, timedelta
            
            cities = ["Yangon", "Mandalay", "Naypyidaw", "Bagan", "Taunggyi"]
            townships = {
                "Yangon": ["Kamayut", "Bahan", "Dagon", "Yankin", "Sanchaung"],
                "Mandalay": ["Chanayethazan", "Mahaaungmye", "Chanmyathazi"],
                "Naypyidaw": ["Pyinmana", "Lewe", "Tatkon"],
                "Bagan": ["Old Bagan", "New Bagan", "Nyaung-U"],
                "Taunggyi": ["Taunggyi", "Nyaungshwe", "Kalaw"]
            }
            
            property_types = ["apartment", "house", "condo", "townhouse", "villa"]
            conditions = ["new", "excellent", "good", "fair", "poor"]
            
            sample_data = []
            
            for i in range(count):
                city = random.choice(cities)
                township = random.choice(townships[city])
                
                property_data = {
                    "id": f"prop_{i+1:06d}",
                    "property_type": random.choice(property_types),
                    "condition": random.choice(conditions),
                    "size_sqft": random.randint(500, 5000),
                    "lot_size_sqft": random.randint(600, 8000) if random.random() > 0.3 else None,
                    "year_built": random.randint(1990, 2024),
                    "location": {
                        "city": city,
                        "township": township,
                        "latitude": 16.8 + random.uniform(-2, 2),
                        "longitude": 96.2 + random.uniform(-2, 2)
                    },
                    "features": {
                        "bedrooms": random.randint(1, 6),
                        "bathrooms": random.randint(1, 4),
                        "floors": random.randint(1, 3),
                        "parking_spaces": random.randint(0, 3),
                        "has_elevator": random.random() > 0.7,
                        "has_swimming_pool": random.random() > 0.8,
                        "has_gym": random.random() > 0.8,
                        "has_security": random.random() > 0.5,
                        "has_garden": random.random() > 0.6,
                        "has_air_conditioning": random.random() > 0.4
                    },
                    "price_mmk": random.randint(50000000, 500000000),
                    "created_at": (datetime.now() - timedelta(days=random.randint(0, 365))).isoformat()
                }
                
                sample_data.append(property_data)
            
            with open(sample_file, 'w') as f:
                json.dump(sample_data, f, indent=2)
            
            print(f"✅ Sample data generated: {sample_file}")
            return True
            
        except Exception as e:
            print(f"❌ Sample data generation failed: {e}")
            return False
    
    async def full_setup(self):
        """Run full development setup."""
        print("🔧 Running full development setup...")
        
        steps = [
            ("Database setup", self.setup_database()),
            ("Sample data generation", self.generate_sample_data()),
            ("ML models training", self.train_models()),
            ("Code linting", self.lint_code()),
            ("Tests", self.run_tests())
        ]
        
        for step_name, step_coro in steps:
            print(f"\n📋 {step_name}...")
            if asyncio.iscoroutine(step_coro):
                success = await step_coro
            else:
                success = step_coro
            
            if not success:
                print(f"❌ Setup failed at: {step_name}")
                return False
        
        print("\n🎉 Full development setup completed successfully!")
        return True


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(description="Myanmar House Price Predictor Development Tools")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Setup development environment")
    setup_parser.add_argument("--full", action="store_true", help="Run full setup")
    setup_parser.add_argument("--db", action="store_true", help="Setup database only")
    setup_parser.add_argument("--models", action="store_true", help="Train models only")
    setup_parser.add_argument("--data", action="store_true", help="Generate sample data")
    setup_parser.add_argument("--count", type=int, default=1000, help="Number of sample records")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.add_argument("--path", help="Specific test path")
    test_parser.add_argument("--coverage", action="store_true", help="Run with coverage")
    
    # Lint command
    subparsers.add_parser("lint", help="Run code linting and formatting")
    
    # Server command
    server_parser = subparsers.add_parser("server", help="Start development server")
    server_parser.add_argument("--host", default="0.0.0.0", help="Server host")
    server_parser.add_argument("--port", type=int, default=8000, help="Server port")
    server_parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload")
    
    # Docker command
    docker_parser = subparsers.add_parser("docker", help="Docker operations")
    docker_parser.add_argument("--build", action="store_true", help="Build Docker image")
    docker_parser.add_argument("--tag", default="myanmar-house-predictor:latest", help="Docker image tag")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    dev_tools = DevTools()
    
    if args.command == "setup":
        if args.full:
            asyncio.run(dev_tools.full_setup())
        elif args.db:
            asyncio.run(dev_tools.setup_database())
        elif args.models:
            asyncio.run(dev_tools.train_models())
        elif args.data:
            dev_tools.generate_sample_data(args.count)
        else:
            print("Please specify a setup option. Use --help for details.")
    
    elif args.command == "test":
        dev_tools.run_tests(args.path, args.coverage)
    
    elif args.command == "lint":
        dev_tools.lint_code()
    
    elif args.command == "server":
        dev_tools.start_server(args.host, args.port, not args.no_reload)
    
    elif args.command == "docker":
        if args.build:
            dev_tools.build_docker(args.tag)
        else:
            print("Please specify a docker operation. Use --help for details.")


if __name__ == "__main__":
    main()
