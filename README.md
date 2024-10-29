
# Ticketing System

This is a simple ticketing system built with Django. Users can create, assign, and comment on tickets. Notifications are sent via email upon ticket creation, assignment, and status updates.

## Features

- User registration and authentication
- Create, assign, and update tickets
- Comment on tickets
- Email notifications for ticket assignments and updates
- Admin interface to manage users and tickets

## Requirements

- Python 3.x
- Django 4.x
- MySQL server

## Setup Instructions

1. **Clone the repository**:
    ```bash
    git clone <repository_url>
    cd ticketing_system
    ```

2. **Create a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install Django**:
    Install Django and any other dependencies you might need:
    ```bash
    pip install Django mysqlclient
    ```

4. **Configure Database**:
   - Create a MySQL database (e.g., `ticketing_db`).
   - Update `settings.py` with your MySQL database credentials:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'ticketing_db',
           'USER': 'your_db_user',
           'PASSWORD': 'your_db_password',
           'HOST': 'localhost',
           'PORT': '3306',
       }
   }
   ```

5. **Run migrations**:
    ```bash
    python manage.py migrate
    ```

6. **Create a superuser** (for admin access):
    ```bash
    python manage.py createsuperuser
    ```

7. **Run the development server**:
    ```bash
    python manage.py runserver
    ```

8. **Access the application**:
   Open your browser and go to `http://127.0.0.1:8000/`. 

## Additional Configuration

- Configure your email settings in `settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.your_email_provider.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your_email@example.com'
EMAIL_HOST_PASSWORD = 'your_email_password'
DEFAULT_FROM_EMAIL = 'your_email@example.com'
```



## Running Tests

To run the test cases for the application, use:
```bash
python manage.py test ticketing_app
```

## Acknowledgments

- Django Documentation: [https://docs.djangoproject.com/](https://docs.djangoproject.com/)
- MySQL Documentation: [https://dev.mysql.com/doc/](https://dev.mysql.com/doc/)
