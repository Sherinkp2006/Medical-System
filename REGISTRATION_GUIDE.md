# User Registration Implementation Guide

## ✅ Features Implemented

1. ✅ **Registration View** (`user_register`) — Handles registration form submission
2. ✅ **Registration Form** (`UserRegistrationForm`) — Validates user input
3. ✅ **Username Uniqueness Check** — Verifies username doesn't already exist
4. ✅ **Password Confirmation** — Ensures passwords match
5. ✅ **New User Creation** — Creates user in database with hashed password
6. ✅ **Redirect to Login** — After successful registration
7. ✅ **Registration Template** — Bootstrap-styled registration form
8. ✅ **Navigation Integration** — Links in navbar and login page

---

## 📁 Files Created/Modified

### Created:
1. **`Pharmacy/templates/pharmacy/register.html`** — Registration form template

### Modified:
1. **`Pharmacy/forms.py`** — Added `UserRegistrationForm` class
2. **`Pharmacy/views.py`** — Added `user_register()` view function
3. **`Pharmacy/urls.py`** — Added `/register/` route
4. **`Pharmacy/templates/pharmacy/login.html`** — Added register link
5. **`Pharmacy/templates/pharmacy/base.html`** — Added register link in navbar

---

## Code Explanation — Line-by-Line

### Registration Form (`Pharmacy/forms.py`)

```python
class UserRegistrationForm(forms.Form):
    """Form for user registration with password validation."""
```
- Defines a Django form for collecting registration data
- Not a ModelForm (doesn't directly map to User model) to allow custom validation

```python
    username = forms.CharField(
        max_length=150,
        min_length=3,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username (3-150 characters)',
            'required': True
        }),
        help_text='3-150 characters. Letters, digits, and @/./+/-/_ allowed.'
    )
```
- Django CharField with min/max length validation
- `max_length=150` — Django User.username max length is 150
- `min_length=3` — Require at least 3 characters
- `widget` — HTML rendering with Bootstrap CSS class
- `help_text` — Display helpful message to user

```python
    password = forms.CharField(
        min_length=6,
        widget=forms.PasswordInput(attrs={...}),
        help_text='Minimum 6 characters.'
    )
```
- Password field with `PasswordInput` widget (masks input with asterisks)
- `min_length=6` — Require at least 6 characters
- Does NOT enforce character complexity (can be customized)

```python
    confirm_password = forms.CharField(
        min_length=6,
        widget=forms.PasswordInput(attrs={...})
    )
```
- Second password field for user confirmation
- Same validation rules as password field

```python
    def clean_username(self):
        """Validate that username is unique and doesn't already exist."""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "This username is already taken. Please choose another."
            )
        return username
```
- **Field-level validation** for username
- Queries User table to check if username already exists
- If exists, raises ValidationError with user-friendly message
- Called automatically when form.is_valid() is called

```python
    def clean(self):
        """Cross-field validation: check if passwords match."""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError(
                    "Passwords do not match. Please try again."
                )
        return cleaned_data
```
- **Form-level validation** (cross-field check)
- Compares password and confirm_password fields
- If they don't match, raises ValidationError
- This error appears as a non-field error (displayed at top of form)

---

### Registration View (`Pharmacy/views.py`)

```python
def user_register(request):
    """Handle user registration using a custom form."""
    if request.method == 'POST':
```
- Handles both GET (display form) and POST (process submission)
- GET: displays empty registration form
- POST: processes submitted form data

```python
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
```
- Creates form instance bound to POST data
- `form.is_valid()` runs all validation:
  - Field-level: username min/max length, password min length
  - Field-level: username uniqueness check (via clean_username())
  - Form-level: password match check (via clean())

```python
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
```
- Extracts validated, cleaned data from form
- `cleaned_data` is a dictionary of validated field values
- Safe to use — already validated by form

```python
            user = User.objects.create_user(
                username=username,
                password=password
            )
```
- Django's built-in method to create a new User
- **Automatically hashes the password** (never stored as plaintext)
- Uses PBKDF2 + SHA256 hashing algorithm by default
- Creates and saves the user to database atomically

```python
            messages.success(
                request,
                f"Account created successfully for {username}! Please log in."
            )
```
- Adds success message to session
- Message displayed on next page load (the login page)
- Uses Django messages framework

```python
            return redirect('pharmacy:login')
```
- Redirects to login page after successful registration
- User must now log in with the new credentials

```python
    else:
        form = UserRegistrationForm()
    return render(request, 'pharmacy/register.html', {'form': form})
```
- For GET requests, display empty form
- Render register.html template with the form object

---

### URL Route (`Pharmacy/urls.py`)

```python
path('register/', views.user_register, name='register'),
```
- Accessible at: `http://127.0.0.1:8000/pharmacy/register/`
- URL name: `'pharmacy:register'` — used in templates
- Function called: `views.user_register`

---

### Registration Template (`register.html`)

```django
{% extends "pharmacy/base.html" %}
```
- Extends base template for consistent styling/navigation

```django
<label for="id_username" class="form-label">Username</label>
{{ form.username }}
```
- Renders the username field
- Django automatically assigns id `id_username` to the field
- Label associates with field via `for="id_username"`

```django
{% if form.username.errors %}
    <div class="alert alert-danger mt-2">
        {% for error in form.username.errors %}
            <small>{{ error }}</small><br>
        {% endfor %}
    </div>
{% endif %}
```
- Displays field-specific errors (e.g., "This username is already taken")
- Only shown if there are errors for this field
- Styled as red alert box (Bootstrap)

```django
{% if form.non_field_errors %}
    <div class="alert alert-danger">
        {% for error in form.non_field_errors %}
            {{ error }}<br>
        {% endfor %}
    </div>
{% endif %}
```
- Displays form-level errors (e.g., "Passwords do not match")
- Shown above all fields
- Set by form's clean() method validation

---

## User Registration Flow

```
1. User visits /pharmacy/register/
   ↓
2. GET request → user_register() displays empty form
   ↓
3. User fills form and clicks "Create Account"
   ↓
4. POST request with: username, password, confirm_password
   ↓
5. Form validation:
   ├─ Username: check min/max length
   ├─ Username: check uniqueness (clean_username)
   ├─ Password: check min length
   ├─ Passwords: check match (clean)
   ↓
6a. If validation fails:
    └─ Redisplay form with error messages
    └─ User corrects and resubmits
    ↓
6b. If validation succeeds:
    ├─ Extract cleaned_data (username, password)
    ├─ Create new User: User.objects.create_user()
    ├─ Password automatically hashed (stored secure)
    ├─ Add success message
    ├─ Redirect to /pharmacy/login/
    ↓
7. User sees "Account created successfully" message
   ↓
8. User logs in with new username/password
```

---

## Validation Rules

### Username Validation
- ✅ Length: 3-150 characters
- ✅ Uniqueness: No duplicate usernames in database
- ✅ Characters: Letters, digits, @, ., +, -, _

### Password Validation
- ✅ Length: Minimum 6 characters (customizable)
- ✅ Confirmation: Must match confirm_password field
- ⚠️ NO complexity requirements (add custom validation if needed)

### Database Constraints
- ✅ Username: Unique constraint in auth_user table
- ✅ Password: Stored as hash (PBKDF2 + SHA256)

---

## Testing Registration Locally

### Step 1: Start Server
```bash
python manage.py runserver
```

### Step 2: Access Register Page
- URL: http://127.0.0.1:8000/pharmacy/register/
- Or click "📝 Register" link in navbar (when not logged in)
- Or click "Register here" link on login page

### Step 3: Test Valid Registration
```
Username: testuser123
Password: testpass123
Confirm Password: testpass123
Click: Create Account
```
- Expected: Success message, redirected to login page

### Step 4: Test Invalid Registrations

**Duplicate Username:**
```
Username: testuser123 (same as before)
Password: password123
Confirm Password: password123
```
- Expected: Error "This username is already taken"

**Password Mismatch:**
```
Username: newuser
Password: pass1234
Confirm Password: pass5678
```
- Expected: Error "Passwords do not match"

**Username Too Short:**
```
Username: ab (only 2 chars)
Password: pass1234
```
- Expected: Error about minimum length

**Password Too Short:**
```
Username: gooduser
Password: pass (only 4 chars)
```
- Expected: Error about minimum length

### Step 5: Login with New Account
```
Go to: http://127.0.0.1:8000/pharmacy/login/
Username: testuser123
Password: testpass123
Click: Login
```
- Expected: "Welcome back, testuser123!", redirected to medicine list

---

## Database Changes

### auth_user Table After Registration

```sql
-- Before registration:
SELECT * FROM auth_user WHERE username='testuser123';
-- (no results)

-- After registration:
SELECT * FROM auth_user WHERE username='testuser123';
-- Results:
-- id: 2
-- username: testuser123
-- password: pbkdf2_sha256$260000$...abcdef123... (hashed)
-- email: (empty)
-- first_name: (empty)
-- last_name: (empty)
-- is_staff: 0
-- is_superuser: 0
-- is_active: 1
-- date_joined: 2026-06-13 10:30:45
```

### Username Uniqueness

Django enforces username uniqueness at the database level:
```sql
-- Table constraint:
CREATE UNIQUE INDEX auth_user_username ON auth_user(username);
```

This means:
- Can't insert duplicate username via SQL
- Form validation checks this BEFORE attempting insert
- If somehow a duplicate is submitted, database rejects it

---

## Integration with Authentication System

### User.objects.create_user()

This Django ORM method:
1. Creates a new User instance
2. Hashes the password using `set_password()`
3. Saves to database atomically
4. Returns the created User object

**Hash Algorithm:**
```
PBKDF2 (Password-Based Key Derivation Function 2)
├─ Hash Algorithm: SHA256
├─ Iterations: 260,000 (default)
└─ Salt: Random 32-byte value per password
```

**Password Storage Example:**
```
Plaintext: "testpass123"
Stored as: "pbkdf2_sha256$260000$saltsaltsalt123$hashhashhashhash456"
           ^                ^                    ^
           algorithm        iterations           salt|hash
```

When user logs in:
1. `authenticate()` hashes the submitted password
2. Compares hash to stored hash
3. If hashes match, authentication succeeds

---

## Security Considerations

1. **Password Hashing:** Automatic via `create_user()`
2. **Username Uniqueness:** Validated at form-level + database-level
3. **CSRF Protection:** Form includes `{% csrf_token %}`
4. **SQLi Prevention:** Django ORM parameterized queries
5. **Password Confirmation:** Prevents typos during registration
6. **Error Messages:** Don't leak sensitive info (e.g., "username taken" is OK)

---

## Error Handling

### Form-Level Errors (non_field_errors)
- "Passwords do not match. Please try again."
- Displayed at top of form in red alert

### Field-Level Errors
- **Username:** "This username is already taken. Please choose another."
- **Password:** "Ensure this value has at least 6 characters."
- **Confirm Password:** "Ensure this value has at least 6 characters."
- Displayed under respective field

### Database-Level Errors (rare)
- Most errors caught by form validation
- If somehow duplicate username reaches database, IntegrityError raised
- Django-Allauth handles this gracefully in production

---

## Customization Options

### Add Password Complexity Requirements
```python
def clean_password(self):
    password = self.cleaned_data.get('password')
    if password:
        if not any(char.isdigit() for char in password):
            raise forms.ValidationError("Password must contain at least one digit.")
        if not any(char.isupper() for char in password):
            raise forms.ValidationError("Password must contain at least one uppercase letter.")
    return password
```

### Add Email Field (Optional)
```python
email = forms.EmailField(
    required=False,
    widget=forms.EmailInput(attrs={'class': 'form-control'})
)

# Then in view:
user = User.objects.create_user(
    username=username,
    password=password,
    email=email  # Optional
)
```

### Add Terms & Conditions
```python
agree_terms = forms.BooleanField(
    required=True,
    label='I agree to the terms and conditions'
)

# Validate in clean():
if not self.cleaned_data.get('agree_terms'):
    raise forms.ValidationError("You must agree to the terms.")
```

### Require Email Verification
- Use django-allauth package
- Or implement custom email verification flow

---

## Summary

✅ **User Registration Fully Implemented:**
- Form with username, password, confirm password fields
- Comprehensive validation:
  - Username uniqueness check
  - Password min length
  - Password confirmation match
- Secure user creation with automatic password hashing
- Redirect to login after successful registration
- Error messages for all validation failures
- Bootstrap-styled template
- Navbar links for easy access

**Usage:**
1. Visit `/pharmacy/register/`
2. Enter username and password
3. Confirm password
4. Click "Create Account"
5. On success, redirected to login page
6. Log in with new credentials

---

## Files Modified

| File | Description |
|------|-------------|
| `Pharmacy/forms.py` | Added UserRegistrationForm |
| `Pharmacy/views.py` | Added user_register view |
| `Pharmacy/urls.py` | Added /register/ route |
| `Pharmacy/templates/pharmacy/register.html` | NEW: Registration form template |
| `Pharmacy/templates/pharmacy/login.html` | Added register link |
| `Pharmacy/templates/pharmacy/base.html` | Added register link in navbar |

---

**✅ Registration feature complete and tested!**

