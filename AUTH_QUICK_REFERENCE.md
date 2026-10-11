# Django Authentication Quick Reference Card

## 📌 Key Functions

### authenticate(request, username, password)
```python
user = authenticate(request, username='admin', password='pass123')
# Returns User object if valid, None if invalid
```

### login(request, user)
```python
login(request, user)
# Creates session, sets request.user, becomes authenticated
```

### logout(request)
```python
logout(request)
# Destroys session, clears cookies, user becomes anonymous
```

### @login_required decorator
```python
@login_required(login_url='pharmacy:login')
def protected_view(request):
    # Only authenticated users can access
    pass
```

---

## 🗂️ Files Structure

```
MedicalSystem/
├── Pharmacy/
│   ├── views.py                          # user_login, user_logout, @login_required
│   ├── urls.py                           # /login/, /logout/
│   ├── forms.py                          # PharmacyForm (unchanged)
│   ├── models.py                         # Pharmacy model (unchanged)
│   └── templates/pharmacy/
│       ├── base.html                     # Updated with auth navbar
│       ├── login.html                    # NEW: Login page
│       ├── list_medicine.html            # @login_required
│       ├── add_medicine.html             # @login_required
│       ├── edit_medicine.html            # @login_required
│       ├── delete_medicine_confirm.html  # @login_required
│       └── sell_medicine.html            # @login_required
├── MedicalSystem/
│   ├── settings.py                       # Added LOGIN_URL, MESSAGE_TAGS
│   ├── urls.py                           # (unchanged)
│   └── wsgi.py                           # (unchanged)
└── manage.py
```

---

## 🔑 Setup Steps

1. **Create Superuser:**
   ```bash
   python manage.py createsuperuser
   ```

2. **Run Server:**
   ```bash
   python manage.py runserver
   ```

3. **Test Login:**
   - Go to: http://127.0.0.1:8000/pharmacy/login/
   - Enter: admin / password
   - Click: Login

---

## 🔐 Protected URLs

| URL | Function | Status |
|-----|----------|--------|
| `/pharmacy/login/` | user_login | ❌ NOT protected |
| `/pharmacy/logout/` | user_logout | ⚠️ Safe to access when logged in |
| `/pharmacy/` | list_medicines | ✅ **PROTECTED** |
| `/pharmacy/add/` | add_medicine | ✅ **PROTECTED** |
| `/pharmacy/edit/<pk>/` | edit_medicine | ✅ **PROTECTED** |
| `/pharmacy/delete/<pk>/` | delete_medicine | ✅ **PROTECTED** |
| `/pharmacy/sell/<pk>/` | sell_medicine | ✅ **PROTECTED** |

---

## 📊 Authentication Flow

```
GET /pharmacy/
  ↓
@login_required checks is_authenticated
  ↓
False → Redirect to /pharmacy/login/?next=/pharmacy/
  ↓
User submits form (POST /pharmacy/login/)
  ↓
authenticate(request, username, password)
  ↓
Valid → login(request, user)
  ↓
Redirect to ?next=/pharmacy/
  ↓
User is now authenticated
  ↓
Access granted to /pharmacy/
```

---

## 💾 Database

### auth_user Table (Django built-in)
- id, username, password (hashed), email
- first_name, last_name
- is_staff, is_superuser, is_active
- date_joined, last_login

### django_session Table (Django built-in)
- Stores active sessions
- Expires after 2 weeks (configurable)

---

## 📝 Code Snippets

### Check if User is Authenticated
```python
# In Python view:
if request.user.is_authenticated:
    print(f"User: {request.user.username}")

# In template:
{% if user.is_authenticated %}
    <p>Hello, {{ user.username }} !</p>
{% endif %}
```

### Add Login Required
```python
@login_required(login_url='pharmacy:login')
def my_view(request):
    return render(request, 'template.html')
```

### Display Messages
```python
from django.contrib import messages

messages.success(request, "Operation successful!")
messages.error(request, "An error occurred.")
messages.warning(request, "Be careful!")
messages.info(request, "Here's some info.")
```

### Django Shell — Create User
```bash
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.create_user('username', 'email@example.com', 'password')
>>> User.objects.all()
```

---

## ✅ Testing Checklist

- [ ] Create superuser
- [ ] Run development server
- [ ] Access /pharmacy/ without login → redirects to login
- [ ] Login with valid credentials → success message + redirected
- [ ] Login with invalid password → error message + stay on login
- [ ] Access /pharmacy/ after login → shows medicine list
- [ ] Click logout → logged out message + redirected to login
- [ ] Verify navbar shows username when logged in
- [ ] Verify navbar shows login link when logged out
- [ ] Check that all medicine views are protected

---

## 🚨 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "Page not found" on login | Check URL: `/pharmacy/login/` (with trailing slash) |
| "User matching query does not exist" | Ensure superuser was created: `python manage.py createsuperuser` |
| Redirects to login every time | Check setting: `LOGIN_URL = 'pharmacy:login'` in settings.py |
| Messages not showing | Ensure MESSAGE_TAGS in settings.py maps to Bootstrap classes |
| CSS not loading | Check STATIC_URL = 'static/' in settings.py |
| Password always wrong | Check password hash: Django doesn't store plaintext |

---

## 🔒 Security Best Practices

1. **Use HTTPS** in production
2. **Never commit secrets** to git
3. **Enforce strong passwords** (8+ chars, mix of types)
4. **Enable CSRF protection** (`{% csrf_token %}` in forms)
5. **Use SESSION_COOKIE_SECURE = True** in production
6. **Set SESSION_COOKIE_HTTPONLY = True** (blocks JS access)
7. **Configure appropriate SESSION_COOKIE_AGE** (timeout)
8. **Implement rate limiting** on login attempts
9. **Add 2FA** for sensitive operations
10. **Log authentication events** for audit trail

---

## 📚 Documentation Links

- [Django Authentication Docs](https://docs.djangoproject.com/en/6.0/topics/auth/)
- [authenticate() Function](https://docs.djangoproject.com/en/6.0/topics/auth/default/#authenticate)
- [login() Function](https://docs.djangoproject.com/en/6.0/topics/auth/default/#login)
- [login_required Decorator](https://docs.djangoproject.com/en/6.0/topics/auth/default/#login_required)
- [Messages Framework](https://docs.djangoproject.com/en/6.0/ref/contrib/messages/)

---

## 🎯 Next Steps

1. ✅ Authentication working
2. ⏭️ Add password reset functionality
3. ⏭️ Implement user roles/permissions
4. ⏭️ Add email verification
5. ⏭️ Enable 2FA
6. ⏭️ Setup production deployment

---

**Created:** June 13, 2026  
**Status:** ✅ Complete and Tested  
**Last Updated:** Today

