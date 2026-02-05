
# BlogSpace - Personal Blogging Platform


A complete, full-stack personal blogging platform with a RESTful API backend and a modern, minimal GUI frontend. Built with Flask, SQLite, and vanilla JavaScript.

---
##  Features
### Backend API
- RESTful API with proper HTTP methods and status codes

- JWT Authentication with refresh tokens

- SQLite Database for lightweight, file-based storage

- CRUD Operations for posts, users, comments, and categories

- Pagination, Filtering & Sorting on all list endpoints

- Rate Limiting and input validation middleware

- Error Handling with consistent JSON responses

### Frontend GUI
- Modern, Responsive Design that works on all devices

- Minimalist Interface with clean typography and subtle animations

- Real-time Updates without page reloads

- Rich Text Editor with markdown support

- User Dashboard with statistics and quick actions

- Authentication Flow with login/register pages

## Core Functionality
- Blog Post Management - Create, edit, delete, and publish posts

- User Profiles - Customizable profiles with bio and avatar

- Comments System - Nested comments with approval system

- Categories & Tags - Organize content with categories and tags

- Likes System - Like/unlike posts

- Analytics - Track views, comments, and likes

- Search & Filter - Find content by category, tags, or keywords

## Project Structure
```bash
blogging-platform/
├── api/                    # Flask REST API Backend
│   ├── app.py             # Main API application
│   ├── models.py          # SQLAlchemy models
│   ├── auth.py            # JWT authentication
│   ├── middleware.py      # Custom middleware
│   └── config.py          # Configuration settings
├── routes/                # API route blueprints
│   ├── users.py           # User authentication routes
│   ├── posts.py           # Blog post routes
│   ├── comments.py        # Comment routes
│   └── categories.py      # Category routes
├── templates/             # HTML Templates
│   ├── base.html          # Base template
│   ├── index.html         # Home page
│   ├── login.html         # Login page
│   ├── register.html      # Registration page
│   ├── dashboard.html     # User dashboard
│   ├── posts.html         # Posts listing
│   ├── create_post.html   # Post editor
│   └── view_post.html     # Single post view
├── static/                # Static assets
│   ├── css/
│   │   └── style.css      # Main stylesheet
│   ├── js/
│   │   └── app.js         # Main JavaScript
│   └── images/            # Images and icons
├── utils/                 # Utility functions
│   └── helpers.py         # Helper functions
├── gui_app.py            # Main application (serves both API & GUI)
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
└── README.md             
```
---
## Installation
```bash
Prerequisites
Python 3.8 or higher

pip (Python package manager)

Step 1: Clone and Setup
bash
# Clone the repository
git clone <your-repo-url>
cd blogging-platform

# Create virtual environment (optional but recommended)
python -m venv venv

# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
Step 2: Configure Environment
bash
# Create .env file from example
cp .env.example .env

# Edit .env with your settings
# You can generate secret keys using:
# python -c "import secrets; print(secrets.token_hex(32))"
Step 3: Initialize Database
bash
# The database will be created automatically on first run
# Or manually initialize:
python -c "
from gui_app import create_gui_app
app = create_gui_app()
with app.app_context():
    from api.models import db
    db.create_all()
    print('Database created!')
"
Step 4: Run the Application
bash
# Development mode
python gui_app.py

# Or with Flask CLI
export FLASK_APP=gui_app.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000
The application will be available at: http://localhost:5000
```
---
## API Documentation
```bash
Base URL

http://localhost:5000/api
Authentication Endpoints
Method	Endpoint	Description	Auth Required
POST	/users/register	Register new user	No
POST	/users/login	Login user	No
POST	/users/refresh	Refresh access token	Refresh Token
GET	/users/profile	Get current user profile	Yes
PUT	/users/profile	Update user profile	Yes
GET	/users/{username}	Get public user profile	No
Post Endpoints
Method	Endpoint	Description	Auth Required
GET	/posts/	Get all published posts	No
GET	/posts/{slug}	Get single post	No
POST	/posts/	Create new post	Yes
PUT	/posts/{id}	Update post	Yes (Owner/Admin)
DELETE	/posts/{id}	Delete post	Yes (Owner/Admin)
POST	/posts/{id}/like	Like/unlike post	Yes
GET	/posts/drafts	Get user drafts	Yes
Comment Endpoints
Method	Endpoint	Description	Auth Required
GET	/comments/post/{post_id}	Get post comments	No
POST	/comments/	Create comment	Yes
PUT	/comments/{id}	Update comment	Yes (Owner/Admin)
DELETE	/comments/{id}	Delete comment	Yes (Owner/Admin)
Category Endpoints
Method	Endpoint	Description	Auth Required
GET	/categories/	Get all categories	No
GET	/categories/{slug}	Get single category	No
POST	/categories/	Create category	Yes (Admin)
PUT	/categories/{id}	Update category	Yes (Admin)
DELETE	/categories/{id}	Delete category	Yes (Admin)
🔑 Default Admin Account
On first run, the system creates a default admin account:

Email: admin@blog.com

Password: admin123

Username: admin
```
---
- ⚠️ Important: Change the default admin password immediately after first login!

## GUI Walkthrough
```bash
1. Home Page (/)
Welcome screen with platform introduction

Recent posts showcase

Feature highlights

Call-to-action buttons

2. Authentication (/login, /register)
Clean, modern forms with validation

Password strength indicators

Remember me functionality

Social login placeholders

3. Dashboard (/dashboard)
User statistics (posts, views, comments, likes)

Recent activity feed

Quick action buttons

Popular posts list

4. Post Management (/posts/create)
Rich text editor with formatting toolbar

Category and tag selection

Featured image upload

Draft vs publish options

Auto-slug generation

5. Profile (/profile)
User information display

Profile picture upload

Bio editing

Account settings
```
---
🔧 Configuration
Environment Variables (.env)
env
# Flask Configuration
SECRET_KEY=your-super-secret-key-32-chars-long-here
JWT_SECRET_KEY=another-super-secret-key-for-jwt-here

# Database Configuration
DATABASE_NAME=blogging_platform.db

# Development Settings
FLASK_ENV=development
FLASK_DEBUG=True

## Optional: Email Configuration (for future features)
 
 - MAIL_SERVER=smtp.gmail.com
 - MAIL_PORT=587
 - MAIL_USE_TLS=True
 - MAIL_USERNAME=your-email@gmail.com
 - MAIL_PASSWORD=your-password
## Database Configuration
The platform uses SQLite by default for simplicity:

Database file: blogging_platform.db

Auto-creates on first run

Includes sample categories

Creates admin user

To use another database (PostgreSQL, MySQL), update config.py:

python
# PostgreSQL example
SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/blogging_platform'

# MySQL example
```bash
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:password@localhost/blogging_platform'
 Testing the API
Using curl
Register a user:

bash
curl -X POST http://localhost:5000/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
Login:

bash
curl -X POST http://localhost:5000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
Create a post (with JWT):

bash
curl -X POST http://localhost:5000/api/posts/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "title": "My First Blog Post",
    "content": "This is the content of my blog post...",
    "tags": ["blogging", "tutorial"],
    "is_published": true
  }'
Get all posts with pagination:

bash
curl "http://localhost:5000/api/posts/?page=1&per_page=10&sort_by=created_at&sort_order=desc"
Using Postman/Insomnia
Import the following collection:

json
{
  "info": {
    "name": "BlogSpace API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Authentication",
      "item": [
        {
          "name": "Register",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"username\": \"testuser\",\n  \"email\": \"test@example.com\",\n  \"password\": \"password123\"\n}"
            },
            "url": "http://localhost:5000/api/users/register"
          }
        }
      ]
    }
  ]
}
```
---
## Deployment
```bash
Option 1: Local Development
bash
python gui_app.py
# Access at http://localhost:5000
Option 2: Docker (Recommended for Production)
dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=gui_app.py
ENV FLASK_ENV=production
ENV SECRET_KEY=your-production-secret-key

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "gui_app:create_gui_app()"]
Build and run:

bash
docker build -t blogspace .
docker run -p 5000:5000 -d blogspace
Option 3: Traditional Hosting
Set up a WSGI server (Gunicorn, uWSGI)

Configure reverse proxy (Nginx, Apache)

Set up SSL certificates (Let's Encrypt)

Configure environment variables

Set up database backups
```
---


## Security Features
Password Hashing: Bcrypt with salt

JWT Tokens: Access and refresh tokens

CORS Protection: Configured for API endpoints

Input Validation: Server-side and client-side

Rate Limiting: Per-IP request limiting

SQL Injection Prevention: SQLAlchemy ORM

XSS Protection: Input sanitization

## Database Schema


![alt text](ra.svg)



## Extending the Platform
Adding New Features
Email Notifications:

- Add to requirements.txt
- flask-mail

- Add email configuration to config.py
- Implement email sending in utils/helpers.py
Social Sharing:

javascript
// Add social sharing buttons to view_post.html
// Implement share functionality in app.js
Image Upload:

- Add file upload handling
- Update Post model for image storage
- Add upload endpoint in routes/posts.py
API Documentation (Swagger):

- Add flask-swagger-ui
- Document endpoints with docstrings
Custom Styling
To customize the appearance:

Colors: Edit CSS variables in style.css

css
:root {
    --primary-color: #your-color;
    --secondary-color: #your-color;
    /* ... */
}
Fonts: Change Google Fonts link in base.html

html
<link href="https://fonts.googleapis.com/css2?family=Your+Font&display=swap" rel="stylesheet">
Layout: Modify grid systems and breakpoints in style.css

## Contributing
Fork the repository

Create a feature branch (git checkout -b feature/AmazingFeature)

Commit your changes (git commit -m 'Add some AmazingFeature')

Push to the branch (git push origin feature/AmazingFeature)

Open a Pull Request




## Troubleshooting
Common Issues
Database connection errors:

Ensure SQLite file has proper permissions

Check database path in config.py

JWT authentication failing:

Verify JWT_SECRET_KEY in .env matches

Check token expiration time

CORS errors in API calls:

Ensure CORS is properly configured in gui_app.py

Check request headers

Static files not loading:

Verify static folder path

Check file permissions

Email sending issues:

Verify SMTP settings in config.py

Check email service credentials

Debug Mode
For development, enable debug mode:

python
app.config['DEBUG'] = True
Check logs for detailed error information.

## Support
Documentation: Read this README

## Acknowledgments
Flask - The web framework

SQLAlchemy - ORM toolkit

Font Awesome - Icons

Google Fonts - Typography

All Contributors

Made with ❤️ for bloggers and writers everywhere. Happy blogging! ✍️
