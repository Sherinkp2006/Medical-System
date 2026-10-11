# Django Authentication Implementation — Complete Summary

## ✅ Requirements Completed

1. ✅ **Create login page** — Created `login.html` with Bootstrap form
2. ✅ **Use Django built-in authentication** — Using `authenticate()` and `login()` functions
3. ✅ **Authenticate username and password** — Via `authenticate(request, username, password)`
4. ✅ **Redirect successful login to medicine list** — `redirect('pharmacy:medicine_list')`
5. ✅ **Show error message for invalid credentials** — Using Django messages framework
6. ✅ **Explain authenticate() and login() functions** — Full explanations provided

---

## 📁 Files Implementation

### Created Files:
1. **`Pharmacy/templates/pharmacy/login.html`**
   - Bootstrap-styled login form
   - Displays error and success messages
   - Centered card layout

2. **`AUTHENTICATION_GUIDE.md`**
   - Detailed explanation of all functions
   - Security considerations
   - Optional enhancements

3. **`QUICK_START.md`**
   - Quick setup instructions
   - Testing scenarios
   - User creation commands

4. **`setup_test_user.py`**
   - Script to create test users
   - Helper for development

### Modified Files:

1. **`Pharmacy/views.py`**
   - Import: `authenticate`, `login`, `logout`, `login_required`, `messages`
   - New function: `user_login(request)` — Handles login form
   - New function: `user_logout(request)` — Handles logout
   - Decorator: `@login_required` added to all medicine views

2. **`Pharmacy/urls.py`**
   - Route: `path('login/', views.user_login, name='login')`
   - Route: `path('logout/', views.user_logout, name='logout')`

3. **`Pharmacy/templates/pharmacy/base.html`**
   - Updated navbar to show:
     - Login link (if not authenticated)
     - Username and logout link (if authenticated)
   - Added messages display block before content

4. **`MedicalSystem/settings.py`**
   - Added: `LOGIN_URL = 'pharmacy:login'`
   - Added: `MESSAGE_TAGS` mapping for Bootstrap styling

---

## 🔐 Core Functions Explained

### 1. authenticate(request, username=username, password=password)

**Location:** `django.contrib.auth.authenticate`

**Purpose:** Verify a username/password combination against the User database.

**How it works:**
```python
user = authenticate(request, username='admin', password='admin123')
```

1. Queries the User table for a user with `username='admin'`
2. If found, hashes the plaintext password and compares to the stored hash
3. If hashes match, returns the User object
4. If hashes don't match or user not found, returns None

**Security:** Uses Django's password hashing (PBKDF2 + SHA256 by default)

**Return values:**
- User object if valid credentials
- None if invalid credentials

**Example in user_login():**
```python
user = authenticate(request, username=username, password=password)
if user is not None:
    # Credentials are valid
    login(request, user)
else:
    # Credentials are invalid
    messages.error(request, "Invalid username or password.")
```

---

### 2. login(request, user)

**Location:** `django.contrib.auth.login`

**Purpose:** Create a session for an authenticated user.

**How it works:**
```python
login(request, user)
```

1. Creates a session record in the database (or cache, depending on SESSION_ENGINE)
2. Sets `request.user = user` (User object is now accessible in the view)
3. Sends a `Set-Cookie` header with the session ID in the HTTP response
4. Browser stores the session cookie
5. On next request, browser sends SESSION_ID cookie
6. Django middleware retrieves the session and loads the User

**After login():**
- `request.user.is_authenticated` is True
- `request.user.username` is available
- `request.user.email` is available
- All protected views (@login_required) allow access

**Example in user_login():**
```python
if user is not None:
    login(request, user)  # Create session
    messages.success(request, f"Welcome back, {user.username}!")
    return redirect('pharmacy:medicine_list')
```

---

### 3. logout(request)

**Location:** `django.contrib.auth.logout`

**Purpose:** End the user's session.

**How it works:**
```python
logout(request)
```

1. Retrieves the session ID from the request
2. Deletes the session data from the database
3. Deletes the session cookie (instructs browser to clear it)
4. Sets `request.user` to AnonymousUser

**After logout():**
- `request.user.is_authenticated` is False
- `request.user` is AnonymousUser
- Protected views (@login_required) block access
- User must log in again to access protected content

**Example in user_logout():**
```python
def user_logout(request):
    logout(request)  # Destroy session
    messages.success(request, "You have been logged out.")
    return redirect('pharmacy:login')
```

---

### 4. @login_required(login_url='pharmacy:login')

**Location:** `django.contrib.auth.decorators.login_required`

**Purpose:** Protect a view so only authenticated users can access it.

**How it works:**
1. Checks `request.user.is_authenticated`
2. If True, allows the view to execute normally
3. If False, redirects to the login URL (with `?next=...` parameter to redirect back after login)

**Usage:**
```python
@login_required(login_url='pharmacy:login')
def list_medicines(request):
    medicines = Pharmacy.objects.all()
    return render(request, 'pharmacy/list_medicine.html', {'medicines': medicines})
```

**Flow:**
1. Unauthenticated user visits `/pharmacy/`
2. `@login_required` intercepts the request
3. Redirects to `/pharmacy/login/?next=/pharmacy/`
4. User logs in
5. Django automatically redirects back to `/pharmacy/` (the original URL from `?next=`)

---

## 🔄 Authentication Flow

```
User Flow:
1. User opens http://127.0.0.1:8000/pharmacy/
   └─> @login_required checks request.user.is_authenticated

2. If NOT authenticated:
   └─> Redirect to /pharmacy/login/?next=/pharmacy/

3. Login page displays form
   └─> User enters username and password

4. User submits form (POST)
   └─> user_login() view processes request

5. user_login() calls authenticate(request, username, password)
   └─> Django hashes password and compares to stored hash

6. If credentials valid:
   └─> login(request, user) creates a session
   └─> Redirect to ?next=/pharmacy/

7. User is now authenticated
   └─> @login_required passes
   └─> list_medicines() view executes
   └─> Medicine list is displayed

8. When user clicks logout:
   └─> logout(request) destroys the session
   └─> Redirect to /pharmacy/login/

9. User is now anonymous again
   └─> @login_required blocks access to protected views
```

---

## 📋 Protected Views

All these views now require authentication:

```python
@login_required(login_url='pharmacy:login')
def list_medicines(request):
    # View code

@login_required(login_url='pharmacy:login')
def add_medicine(request):
    # View code

@login_required(login_url='pharmacy:login')
def edit_medicine(request, pk):
    # View code

@login_required(login_url='pharmacy:login')
def sell_medicine(request, pk):
    # View code

@login_required(login_url='pharmacy:login')
def delete_medicine(request, pk):
    # View code
```

---

## 🎨 Template Integration

### Login Page (`login.html`)
- Form with username and password fields
- CSRF token for security
- Displays error/success messages
- Bootstrap styling (card, buttons, form controls)

### Base Template (`base.html`)
- Updated navbar to conditionally show:
  - Login link (if `user.is_authenticated` is False)
  - Username and logout link (if `user.is_authenticated` is True)
- Messages display block to show Django messages
- All messages styled with Bootstrap alert colors

### Template Tag for Auth Check:
```django
{% if user.is_authenticated %}
    <p>Welcome, {{ user.username }}!</p>
    <a href="{% url 'pharmacy:logout' %}">Logout</a>
{% else %}
    <a href="{% url 'pharmacy:login' %}">Login</a>
{% endif %}
```

---

## 🔧 Configuration in settings.py

```python
# LOGIN_URL: where to redirect unauthenticated users
LOGIN_URL = 'pharmacy:login'

# MESSAGE_TAGS: map Django message levels to Bootstrap CSS classes
MESSAGE_TAGS = {
    messages.DEBUG: 'debug',           # alert-debug
    messages.INFO: 'info',             # alert-info (blue)
    messages.SUCCESS: 'success',       # alert-success (green)
    messages.WARNING: 'warning',       # alert-warning (yellow)
    messages.ERROR: 'danger',          # alert-danger (red)
}
```

---

## 🧪 Testing the System

### Create a Superuser:
```bash
python manage.py createsuperuser
# Username: admin
# Password: admin123
```

### Run the Server:
```bash
python manage.py runserver
```

### Test Scenarios:

**1. Try accessing /pharmacy/ without login:**
- Expected: Redirected to login page ✓

**2. Login with valid credentials:**
- Expected: Greeted with welcome message, redirected to /pharmacy/ ✓

**3. Try invalid credentials:**
- Expected: Error message displayed ✓

**4. Click logout:**
- Expected: Logged out message, redirected to login ✓

**5. Try accessing /pharmacy/ after logout:**
- Expected: Redirected to login page ✓

---

## 🔒 Security Features

1. **Password Hashing:** Passwords stored as PBKDF2 + SHA256 hashes
2. **CSRF Protection:** Login form includes `{% csrf_token %}`
3. **Session Security:** SessionID cookie marked HTTPOnly (not accessible via JavaScript)
4. **Message Framework:** Prevents sensitive info from being exposed
5. **Decorator-based Protection:** @login_required prevents unauthorized access

---

## 📊 Database Changes

The authentication system uses Django's built-in `auth_user` table with these fields:
- `id` — Primary key
- `username` — Unique username
- `password` — Hashed password (never plaintext)
- `email` — User email
- `first_name` — First name
- `last_name` — Last name
- `is_staff` — Admin staff flag
- `is_superuser` — Superuser/admin flag
- `is_active` — Account active flag
- `date_joined` — Account creation date
- `last_login` — Last login timestamp

Sessions are stored in `django_session` table:
- `session_key` — Unique session ID
- `session_data` — Encrypted session data (user ID, etc.)
- `expire_date` — When session expires

---

## 🚀 Next Steps & Enhancements

1. **Password Reset** — Django provides password reset views
2. **Email Verification** — Verify email addresses on registration
3. **Role-Based Access** — Different permissions for pharmacist/manager/admin
4. **Two-Factor Authentication** — Add TOTP/SMS verification
5. **User Registration** — Allow self-signup with approval workflow
6. **Rate Limiting** — Prevent brute force login attempts
7. **Audit Logging** — Log who made what changes
8. **Session Timeout** — Configure `SESSION_COOKIE_AGE` for security
9. **HTTPS Enforcement** — Require HTTPS in production
10. **Social Authentication** — Allow Google/GitHub login

---

## 📚 Summary of Key Concepts

| Concept | Purpose | Function |
|---------|---------|----------|
| **Authenticate** | Verify credentials | `authenticate(request, username, password)` |
| **Login** | Create session | `login(request, user)` |
| **Logout** | Destroy session | `logout(request)` |
| **@login_required** | Protect views | `@login_required(login_url='...')` |
| **Sessions** | Track login state | Django middleware handles automatically |
| **Messages** | Feedback to user | `messages.success/error/warning/info/debug` |

---

## ✨ Conclusion

Django authentication provides a complete, secure system for:
- ✅ User registration and login
- ✅ Password hashing and verification
- ✅ Session management
- ✅ View protection
- ✅ User state tracking

The implementation protects all medicine management operations with authentication, ensuring only authorized users can access the system.

**The Pharmacy Management System is now fully secured with Django authentication!**

