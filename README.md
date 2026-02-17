# Back2U - Lost and Found Management System

Back2U is a comprehensive lost and found management system designed to help users report lost items, claim found items, and manage the resolution process efficiently. The system features a user-friendly web interface built with Flet and a robust backend API powered by Flask and MySQL.

## Features

- **User Authentication**: Secure login and signup with JWT-based authentication
- **Item Reporting**: Users can report lost or found items with detailed descriptions, categories, and titles
- **Public Item Listings**: Browse and search through reported items with filtering options
- **Claim Management**: Users can claim items they believe are theirs
- **Category Management**: Administrators can create, update, and delete item categories
- **Admin Dashboard**: Administrators can verify claims, resolve cases, and manage categories
- **Email Notifications**: Automated email notifications for claim updates and resolutions
- **Responsive Design**: Modern, dark/light theme toggleable interface

## Tech Stack

### Backend
- **Flask**: RESTful API framework
- **MySQL**: Database for storing users, items, claims, notifications, and categories
- **bcrypt**: Password hashing
- **JWT**: Token-based authentication
- **Flask-CORS**: Cross-origin resource sharing
- **python-dotenv**: Environment variable management

### Frontend
- **Flet**: Python-based UI framework for web applications
- **Requests**: HTTP client for API communication

## Quick Start

### Steps to Run the Project

- [x] Create MySQL database 'back2u_db' and execute schema.sql to set up tables.
- [x] Activate backend venv and run Flask server (python server.py in backend directory).
- [ ] Activate frontend venv and run Flet app (python main.py in frontend directory).

### Notes
- Assumes MySQL Server is installed and running on localhost.
- Assumes backend/.env is configured with MYSQL_USER, MYSQL_PASSWORD, etc.
- Virtual environments (venv) already exist in backend and frontend.
- After backend runs, it should be accessible at http://localhost:5000.
- Frontend will open in browser and connect to backend API.

## Installation

### Prerequisites
- Python 3.8+
- MySQL Server
- Git

### Backend Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd back2u-python-mysql
   ```

2. Navigate to the backend directory:
   ```bash
   cd backend
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Set up environment variables:
   Create a `.env` file in the backend directory with:
   ```
   SECRET_KEY=your-secret-key-here
   MYSQL_HOST=localhost
   MYSQL_USER=your-mysql-username
   MYSQL_PASSWORD=your-mysql-password
   MYSQL_DB=back2u_db
   EMAIL_USER=your-email@example.com
   EMAIL_PASSWORD=your-email-password
   ```

6. Ensure MySQL is running and create the database:
   ```sql
   CREATE DATABASE back2u_db;
   ```

7. Run the backend server:
   ```bash
   python server.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the frontend application:
   ```bash
   python main.py
   ```

The application will open in your default web browser.

## Usage

### For Users
1. **Sign Up/Login**: Create an account or log in to access the system
2. **Browse Items**: View reported lost and found items on the home page
3. **Report Items**: Use the "Report Item" feature to submit lost or found items
4. **Claim Items**: If you find an item that belongs to you, submit a claim

### For Administrators
1. **Login as Admin**: Use admin credentials to access the admin dashboard
2. **Manage Claims**: Review submitted claims and verify ownership
3. **Resolve Cases**: Mark claims as resolved and send notifications to users

## API Endpoints

### Authentication
- `POST /api/auth/signup` - User registration
- `POST /api/auth/login` - User login

### Items
- `GET /api/items` - Get items (supports `status`, `search`, and `include_resolved` filters)
- `POST /api/items` - Report a new item (authenticated)
- `POST /api/items/<id>/claim` - Submit a claim for an item (authenticated)

### Categories
- `GET /api/categories` - List all categories

### Admin
- `GET /api/admin/claims/pending` - Get all pending claims (admin only)
- `POST /api/admin/claims/resolve` - Approve or reject a claim (admin only)
- `GET /api/admin/categories` - List categories (admin only)
- `POST /api/admin/categories` - Create a new category (admin only)
- `PUT /api/admin/categories/<id>` - Update category name (admin only)
- `DELETE /api/admin/categories/<id>` - Delete category and associated items (admin only)

## Project Structure

```
back2u-python-mysql/
├── backend/
│   ├── config/
│   │   ├── db_connector.py      # MySQL connection & table self-initialization
│   ├── models/
│   │   ├── user_model.py        # User data model
│   │   ├── item_model.py        # Item data model
│   │   ├── claim_model.py       # Claim data model
│   │   ├── notification_model.py# Notification data model
│   │   └── category_model.py    # Category data model
│   ├── routes/
│   │   ├── auth_routes.py       # Authentication endpoints
│   │   ├── item_routes.py       # Item and claim management endpoints
│   │   ├── category_routes.py   # Public category endpoints
│   │   └── admin_routes.py      # Admin dashboard & category management
│   ├── utils/
│   │   ├── security.py          # Password hashing and JWT decorators
│   │   └── notification.py      # Email notification logic
│   ├── server.py                # Flask app entry point
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── views/
│   │   ├── login_view.py        # Login UI
│   │   ├── signup_view.py       # User signup UI
│   │   ├── home_view.py         # Item listings UI
│   │   ├── report_item_view.py  # Item reporting UI
│   │   └── admin_dashboard.py   # Admin dashboard UI
│   ├── components/
│   │   ├── navbar.py            # Navigation component with theme toggle
│   │   └── item_card.py         # Item display component
│   ├── api_client.py            # API communication layer
│   ├── main.py                  # Flet app entry point & routing
│   └── requirements.txt
├── schema.sql                   # Database schema reference
├── TODO.md                      # Testing and remaining tasks
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Contact

For questions or support, please contact the development team.
