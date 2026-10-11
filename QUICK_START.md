# Quick Start Guide — Django Authentication

## 🚀 Getting Started (5 Minutes)

### 1. Create a Superuser (Admin Account)

```powershell
cd C:\Users\sheri\PycharmProjects\Intership\MedicalSystem
python manage.py createsuperuser
```

When prompted, enter:
- **Username:** admin
- **Email:** admin@example.com
- **Password:** (your choice, e.g., admin123)

### 2. Run the Development Server

```powershell
python manage.py runserver
```

Output should show:
```
Starting development server at http://127.0.0.1:8000/
```

### 3. Test the Authentication

**Scenario 1: Access pharmacy without login**
- Open: http://127.0.0.1:8000/pharmacy/
- ✓ Redirected to login page automatically

**Scenario 2: Login with valid credentials**
- URL: http://127.0.0.1:8000/pharmacy/login/
- Username: `admin`
- Password: (from step 1)
- Click "Login"
- ✓ Greeted with "Welcome back, admin!"
- ✓ Redirected to medicine list
- ✓ Navbar shows your username and logout link

**Scenario 3: Access pharmacy without login (after logout)**
- Click logout in navbar
- Try to access http://127.0.0.1:8000/pharmacy/
- ✓ Redirected to login page again

**Scenario 4: Invalid credentials**
- Go to http://127.0.0.1:8000/pharmacy/login/
- Enter wrong password
- Click "Login"
- ✓ See error: "Invalid username or password."
- ✓ Stay on login page

---

## 📋 Implementation Summary

### What Was Added:

#### 1. **Login View** (views.py)
   - Accepts username and password
   - Uses `authenticate()` to verify credentials
   - Uses `login()` to create a session
   - Shows success/error messages
   - Redirects authenticated users to medicine list

#### 2. **Logout View** (views.py)
   - Uses `logout()` to destroy session
   - Redirects to login page

#### 3. **Authentication Protection**
   - All medicine views have `@login_required` decorator
   - Unauthenticated users are redirected to login page

#### 4. **Login Template** (login.html)
   - Clean, centered Bootstrap form
   - Displays error/success messages
   - Professional look and feel

#### 5. **Navigation Bar Update** (base.html)
   - Shows different menu items for authenticated vs. non-authenticated users
   - Authenticated users see username and logout link
   - Non-authenticated users see login link

#### 6. **Django Settings** (settings.py)
   - `LOGIN_URL = 'pharmacy:login'` — default redirect for @login_required
   - `MESSAGE_TAGS` — maps Django message levels to Bootstrap CSS classes

---

## 🔐 Django Authentication Functions Explained

### authenticate(request, username, password)
- **Purpose:** Verify username and password against the User database
- **Returns:** User object if valid, None if invalid
- **Password handling:** Automatically hashes the input and compares to stored hash (secure)
- **Example:**
  ```python
  user = authenticate(request, username='admin', password='admin123')
  if user is not None:
      # Credentials are valid
  ```

### login(request, user)
- **Purpose:** Create a session for the authenticated user
- **What it does:**
  1. Creates a session record in the database
  2. Sets a session cookie in the browser
  3. Sets `request.user` to the User object
  4. Makes `request.user.is_authenticated = True`
- **Effect:** All @login_required decorators now recognize the user as authenticated
- **Example:**
  ```python
  login(request, user)
  # After this, request.user is the authenticated user
  ```

### logout(request)
- **Purpose:** End the user's session
- **What it does:**
  1. Removes session from the database
  2. Clears session cookie
  3. Sets `request.user` to AnonymousUser
- **Effect:** User must log in again to access protected views
- **Example:**
  ```python
  logout(request)
  redirect('pharmacy:login')
  ```

---

## 🔗 URLs Available

- **Login:** http://127.0.0.1:8000/pharmacy/login/
- **Logout:** http://127.0.0.1:8000/pharmacy/logout/
- **Medicine List:** http://127.0.0.1:8000/pharmacy/ (protected)
- **Add Medicine:** http://127.0.0.1:8000/pharmacy/add/ (protected)
- **Edit Medicine:** http://127.0.0.1:8000/pharmacy/edit/<id>/ (protected)
- **Delete Medicine:** http://127.0.0.1:8000/pharmacy/delete/<id>/ (protected)
- **Sell Medicine:** http://127.0.0.1:8000/pharmacy/sell/<id>/ (protected)

---

## 📁 Files Created/Modified

### Created:
- `Pharmacy/templates/pharmacy/login.html` — Login page
- `setup_test_user.py` — Script to create test user
- `AUTHENTICATION_GUIDE.md` — Detailed explanation

### Modified:
- `Pharmacy/views.py` — Added user_login, user_logout, @login_required decorators
- `Pharmacy/urls.py` — Added login and logout routes
- `Pharmacy/templates/pharmacy/base.html` — Updated navbar with auth status
- `MedicalSystem/settings.py` — Added LOGIN_URL and MESSAGE_TAGS

---

## 🎯 Workflow Diagram

```
┌─────────────────────────┐
│  User Visits /pharmacy/ │
└────────────┬────────────┘
             │
             ▼
    ┌─────────────────────┐
    │ Is user logged in?  │
    └────┬────────────┬───┘
         │ No         │ Yes
         ▼            ▼
    ┌───────────┐  ┌──────────────┐
    │ Redirect  │  │ Show medicine│
    │ to Login  │  │ list page    │
    └───────────┘  └──────────────┘
         │              │
         │              └──────────┐
         ▼                         │
    ┌───────────────────┐         │
    │ User enters       │         │
    │ credentials       │         │
    └────────┬──────────┘         │
             │                    │
             ▼                    │
    ┌──────────────────────┐      │
    │ authenticate() check │      │
    └────┬────────────┬────┘      │
         │ Invalid    │ Valid     │
         │            │           │
         ▼            ▼           │
    ┌────────┐  ┌──────────┐     │
    │ Error  │  │ login()  │     │
    │ msg    │  │ creates  │     │
    │        │  │ session  │     │
    └────────┘  └────┬─────┘     │
         │           │           │
         │           └───────┬───┘
         │                   │
         └─────────────┬─────┘
                       │
                       ▼
            ┌──────────────────────┐
            │ User authenticated   │
            │ and logged in        │
            └──────────────────────┘
```

---

## 🧪 Additional Testing

### Create More Test Users (Optional)

```powershell
# In Django shell
python manage.py shell

>>> from django.contrib.auth.models import User
>>> User.objects.create_user('pharmacist', 'pharmacist@hospital.com', 'pharm123')
>>> User.objects.create_user('manager', 'manager@hospital.com', 'mgr123')
>>> exit()
```

Then try logging in as each user.

### Check User Database

```powershell
python manage.py dbshell
SELECT username, email, is_superuser FROM auth_user;
.exit
```

---

## ⚠️ Important Notes

1. **Never commit real passwords** to version control. Use environment variables for sensitive data in production.
2. **Use HTTPS in production** — authentication is insecure over plain HTTP.
3. **Password complexity** — Consider requiring strong passwords (at least 8 characters, mix of letters/numbers/symbols).
4. **Session timeout** — Default is 2 weeks. Adjust via `SESSION_COOKIE_AGE` in settings.py if needed.
5. **Brute force protection** — Consider adding rate limiting to prevent password guessing attacks.

---

## 🚀 Next Steps

1. Test the login flow locally
2. Create additional users with `createsuperuser` or management commands
3. Customize the login template styling (colors, logo, etc.)
4. Add password reset functionality (Django provides views for this)
5. Implement role-based permissions (pharmacist, manager, admin roles)
6. Add user registration (if allowing sign-ups)

---

## 📚 Resources

- [Django Authentication](https://docs.djangoproject.com/en/6.0/topics/auth/)
- [authenticate() documentation](https://docs.djangoproject.com/en/6.0/topics/auth/default/#django.contrib.auth.authenticate)
- [login() documentation](https://docs.djangoproject.com/en/6.0/topics/auth/default/#django.contrib.auth.login)
- [login_required decorator](https://docs.djangoproject.com/en/6.0/topics/auth/default/#django.contrib.auth.decorators.login_required)

---

**✓ Django authentication is now fully integrated!**

