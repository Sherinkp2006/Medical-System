# Django Authentication Implementation Guide

## Files Modified/Created

### 1. **Pharmacy/views.py** — Added authentication views
   - `user_login(request)` — Handles login form and authentication
   - `user_logout(request)` — Logs out the user
   - All medicine views now have `@login_required` decorator

### 2. **Pharmacy/urls.py** — Added authentication routes
   - `path('login/', views.user_login, name='login')`
   - `path('logout/', views.user_logout, name='logout')`

### 3. **Pharmacy/templates/pharmacy/login.html** — Created login page
   - Bootstrap-styled login form
   - Displays error/success messages
   - Clean centered layout

### 4. **Pharmacy/templates/pharmacy/base.html** — Updated with authentication
   - Shows login link when user is NOT authenticated
   - Shows username and logout link when user IS authenticated
   - Displays Django messages (success/error) at the top of content

### 5. **MedicalSystem/settings.py** — Added authentication settings
   - `LOGIN_URL = 'pharmacy:login'` — Redirects unauthenticated users here
   - `MESSAGE_TAGS` — Maps Django message levels to Bootstrap CSS classes

---

## How to Test Authentication

### Step 1: Create a Superuser (Admin Account)

```powershell
# From C:\Users\sheri\PycharmProjects\Intership\MedicalSystem
python manage.py createsuperuser
```

You'll be prompted:
```
Username: admin
Email address: admin@example.com
Password: <enter password>
Password (again): <confirm password>
```

### Step 2: Run the Development Server

```powershell
python manage.py runserver
```

### Step 3: Test the Flow

1. **Open the app:** http://127.0.0.1:8000/pharmacy/
   - You will be redirected to the login page (because you're not logged in).

2. **Login page:** http://127.0.0.1:8000/pharmacy/login/
   - Enter username and password from superuser creation.
   - Click "Login".
   - You'll see a success message and be redirected to the medicine list.

3. **After login:**
   - Navbar shows your username and the logout link.
   - All medicine operations (list, add, edit, delete, sell) are accessible.

4. **Logout:**
   - Click the logout link in the navbar.
   - See logout success message.
   - Redirected to login page.

5. **Try accessing protected URL without login:**
   - http://127.0.0.1:8000/pharmacy/ (while logged out)
   - Redirected to login page.

---

## Code Explanation — Line-by-Line

### user_login() View

```python
def user_login(request):
    """Handle user login using Django's built-in authentication system."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
```
- Extract username and password from POST form data.

```python
        user = authenticate(request, username=username, password=password)
```
- **`authenticate(request, username=username, password=password)`**
  - Django's built-in authentication function.
  - Queries the User table in the database.
  - Checks if a user exists with the given username.
  - If found, verifies the password (hashed comparison, not plaintext).
  - Returns a User object if credentials are valid, or None if invalid.
  - The `request` parameter helps with authentication backends (e.g., LDAP).

```python
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('pharmacy:medicine_list')
```
- If authentication succeeded (user is not None):
  - **`login(request, user)`**
    - Django's session management function.
    - Creates a session for this user.
    - Sets a session cookie in the browser response.
    - Subsequent requests with this cookie will have request.user = this user.
    - All `@login_required` decorators will recognize the user as authenticated.
  - Add a success message.
  - Redirect to the medicine list.

```python
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'pharmacy/login.html')
```
- If authentication failed or method is GET:
  - Add an error message (displayed by the messages framework).
  - Render the login form (on GET or after failed POST).

### user_logout() View

```python
def user_logout(request):
    """Log out the current user."""
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('pharmacy:login')
```
- **`logout(request)`**
  - Django's logout function.
  - Removes the session data for this user from the server.
  - Clears the session cookie in the browser.
  - After this, request.user is anonymous again.
  - Next request will trigger @login_required redirects.

### @login_required Decorator

```python
@login_required(login_url='pharmacy:login')
def list_medicines(request):
    ...
```
- Applied to all medicine views (list, add, edit, delete, sell).
- The decorator:
  1. Checks if `request.user.is_authenticated` is True.
  2. If True, proceeds to the view normally.
  3. If False, redirects to the URL specified in `login_url='pharmacy:login'`.
  4. After login, the user is redirected back to the original page (using GET parameter `?next=...`).

---

## Django authenticate() Function — Detailed Explanation

**Purpose:** Verify username/password against the User database.

**Signature:**
```python
authenticate(request, username=username, password=password)
```

**Parameters:**
- `request` — The HttpRequest object (used for authentication backends).
- `username` — The username to check.
- `password` — The plaintext password entered by the user.

**Returns:**
- User object if credentials match.
- None if no match.

**Behind the scenes:**
- Django uses password hashing (default: PBKDF2 with SHA256).
- The password is never stored in plaintext.
- authenticate() hashes the input password and compares to the stored hash.
- Only the User with matching username AND correct password hash returns a User object.

**Example flow:**
```
1. User submits "admin" / "mypassword123"
2. Django checks: SELECT * FROM auth_user WHERE username='admin'
3. If found, Django hashes "mypassword123" and compares to the stored hash
4. If hashes match, return the User object
5. If hashes don't match or user not found, return None
```

---

## Django login() Function — Detailed Explanation

**Purpose:** Create a session for an authenticated user.

**Signature:**
```python
login(request, user)
```

**Parameters:**
- `request` — The HttpRequest object.
- `user` — A User object (from authenticate() or any loaded user).

**What it does:**
1. Creates a session record on the server (stored in database or cache).
2. Sets `request.user = user` (the User object is now available in the view).
3. Sends a Set-Cookie header in the response with SESSION_ID cookie.
4. Browser stores the SESSION_ID cookie.
5. On next request, browser sends SESSION_ID in Cookie header.
6. Django middleware (_SessionMiddleware_) retrieves the session and loads the User.
7. All subsequent requests have `request.user` set to this User.

**After login():**
- `request.user.is_authenticated` is True.
- `request.user.username` is the user's username.
- All `@login_required` views allow access.
- Templates can check `{% if user.is_authenticated %}` to show different content.

**Session timeout:**
- By default, Django sessions expire after 2 weeks of inactivity.
- Configurable via `SESSION_COOKIE_AGE` in settings.

---

## Authentication Flow Diagram

```
1. User not authenticated
   ↓
2. Try to access /pharmacy/ (list_medicines view)
   ↓
3. @login_required decorator checks request.user.is_authenticated
   ↓
4. False → redirect to /pharmacy/login/?next=/pharmacy/
   ↓
5. User fills login form, clicks Submit (POST)
   ↓
6. user_login() view:
   - extract username/password from POST
   - call authenticate(request, username, password)
   - if valid: call login(request, user)
   - if valid: redirect to /pharmacy/ (using ?next parameter)
   ↓
7. User is now authenticated
8. Next request to /pharmacy/: @login_required passes, view executes
```

---

## Integration with Django Messages Framework

The messages framework is already configured in settings.py. When you call:

```python
messages.success(request, "Login successful!")
messages.error(request, "Invalid credentials.")
messages.warning(request, "This action is irreversible.")
```

The message is stored in the session and displayed on the next page render (usually via a template).

### In templates:
```django
{% for message in messages %}
    <div class="alert alert-{{ message.tags }}">
        {{ message }}
    </div>
{% endfor %}
```

### MESSAGE_TAGS mapping (in settings.py):
```python
MESSAGE_TAGS = {
    messages.SUCCESS: 'success',      # Bootstrap: alert-success (green)
    messages.ERROR: 'danger',         # Bootstrap: alert-danger (red)
    messages.WARNING: 'warning',      # Bootstrap: alert-warning (yellow)
    messages.INFO: 'info',            # Bootstrap: alert-info (blue)
    messages.DEBUG: 'debug',          # Bootstrap: alert-debug (gray)
}
```

---

## Security Considerations

1. **Password Hashing:** Django automatically hashes passwords (PBKDF2, Argon2, bcrypt). Never store plaintext.
2. **CSRF Protection:** The login form includes `{% csrf_token %}` to prevent cross-site attacks.
3. **Session Security:** SESSION_COOKIE_HTTPONLY = True (default) — JavaScript cannot access session cookie.
4. **SSL/HTTPS:** In production, always use HTTPS for authentication.
5. **Rate Limiting:** Consider implementing rate limiting on login attempts to prevent brute force.

---

## Optional Enhancements

1. **Email-based login** — Create a custom authentication backend to allow login via email instead of username.
2. **Password reset** — Django provides `PasswordResetView` and related views for password recovery.
3. **User registration** — Create a sign-up form and register new users (permission-based).
4. **Two-factor authentication** — Add TOTP or SMS-based 2FA.
5. **Social authentication** — Use django-allauth for Google/GitHub/Facebook login.
6. **Role-based access** — Add permission checks beyond @login_required (e.g., @permission_required).

---

## Summary

✅ **Created login page** with Bootstrap styling
✅ **Used Django authenticate()** to verify username/password
✅ **Used Django login()** to create sessions
✅ **Protected all medicine views** with @login_required
✅ **Added error/success messages** for user feedback
✅ **Updated navbar** to show login/logout status
✅ **Configured settings** for authentication

Users must now log in before accessing any medicine management features!

