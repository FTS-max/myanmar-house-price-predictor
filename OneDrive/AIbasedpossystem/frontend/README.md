# AI-Powered Point of Sale (POS) System

A modern, modular Point of Sale (POS) frontend built with Next.js 15.3.3 and React 19 that connects to an Odoo backend via REST APIs. This application features custom UI components built with Tailwind CSS and includes AI-powered features via OpenRouter.

## Features

- **Custom Authentication**: Secure login with Odoo backend integration
- **Role-Based Access**: Different interfaces for Owners, Managers, and Cashiers
- **Shop Dashboard**: View shop statistics, users, and configuration
- **Product Catalog**: Grid/list view with category filters, search, and pagination
- **POS Interface**: Intuitive product selection, cart management, and payment processing
- **Order Management**: View order history with filtering options
- **AI Assistant**: Powered by OpenRouter for business insights and automation

## Tech Stack

- **Frontend**: Next.js 15.3.3 with React 19 and App Router
- **Styling**: Tailwind CSS (no third-party UI libraries)
- **State Management**: React Context API and React Query
- **Form Handling**: React Hook Form with Zod validation
- **API Integration**: Axios for REST API communication with Odoo backend
- **AI Integration**: OpenRouter API for AI-powered features

## Getting Started

### Prerequisites

- Node.js 18.17 or later
- Odoo backend server running (configured in `.env.local`)

### Installation

```bash
# Install dependencies
npm install

# Create .env.local file
cp .env.example .env.local
# Edit .env.local with your Odoo backend URL and OpenRouter API key

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the application.

## Project Structure

- `/src/app`: Next.js App Router pages and layouts
- `/src/components`: Reusable UI components
  - `/ui`: Base UI components (Button, Modal, etc.)
  - `/auth`: Authentication components
  - `/dashboard`: Dashboard components
  - `/pos`: Point of Sale components
- `/src/lib`: Utilities, hooks, and API clients
- `/src/types`: TypeScript type definitions

## Custom UI Components

All UI components are custom-built with Tailwind CSS to ensure full compatibility with React 19 and avoid dependencies on third-party libraries.

## Backend Integration

This frontend connects to an Odoo backend via REST APIs. The connection is configured in the `.env.local` file and managed through API client utilities in `/src/lib/api/`.

## AI Features

The application includes AI-powered features using OpenRouter:

- Product caption generation
- Smart reorder suggestions
- Social media content ideas
- Order/sales summaries

## Security

- Authentication tokens stored securely
- Role-based access control
- Protected API routes
- Component-level permission checks

## Next Steps: Development Roadmap

### 1. AI Assistant Enhancements

- Replace mock responses in `AIAssistantPanel.tsx` with actual API calls to OpenRouter
- Expand context awareness with user roles, store information, and transaction data
- Add advanced features like product recommendations and pricing assistance

### 2. Backend Integration

- Complete Odoo backend connection with proper credentials
- Implement real API endpoints for products, orders, users, and shops
- Replace all mock data with live data from the backend

### 3. Feature Enhancements

- **Inventory Management**: Real-time stock tracking and low stock alerts
- **Customer Management**: Customer database with purchase history and loyalty features
- **Reporting & Analytics**: Sales dashboard with key metrics and export functionality
- **Receipt Generation**: Customizable receipt templates with print and email options

### 4. Advanced Features

- **Offline Mode**: Service workers and local storage for offline transactions
- **Multi-language Support**: i18n implementation for UI and AI responses
- **Payment Processing**: Integration with multiple payment gateways

### 5. UI/UX Improvements

- Responsive design for all screen sizes
- Keyboard shortcuts for faster checkout
- Dark mode implementation
- Performance optimizations for smoother animations

### 6. Testing & Deployment

- Comprehensive test suite for critical components
- CI/CD pipeline setup
- Production environment configuration
- Deployment documentation
