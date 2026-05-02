# Frontend Integration Guide — Accounting User Differentiation

## Overview

The backend now exposes an `is_accounting_user` flag on the user session endpoint. The frontend should use this flag to conditionally show/hide accounting-related navigation, routes, and UI elements.

---

## API Contract

### `GET /api/session/`

**Response (authenticated):**
```json
{
  "id": 1,
  "username": "someuser",
  "email": "user@example.com",
  "is_accounting_user": true
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | User ID |
| `username` | string | Username |
| `email` | string | Email address |
| `is_accounting_user` | boolean | `true` if user has accounting access, `false` otherwise |

---

## Frontend Changes Required

### 1. UserContext — Add `isAccountingUser` State

**File:** `frontend/src/contexts/UserContext.js`

Initial user object should include the new field:

```javascript
let obj = {
    logged: false,
    username: null,
    email: null,
    isAccountingUser: false   // <-- add this
}
```

---

### 2. Login Flow (`helper.js` — `isLogged()`)

**File:** `frontend/src/helper.js`

After calling `GET /api/session/`, extract and store the flag:

```javascript
// In isLogged() or wherever /api/session/ response is handled:
let obj = { ...User };
obj.logged = true;
obj.username = data.username;
obj.email = data.email;
obj.isAccountingUser = data.is_accounting_user;   // <-- add this
setUser(obj);
```

---

### 3. Logout Flow (`helper.js` — `logout()`)

**File:** `frontend/src/helper.js`

Reset the flag on logout:

```javascript
export function logout(setUser, User) {
    let obj = { ...User };
    obj.logged = false;
    obj.username = null;
    obj.email = null;
    obj.isAccountingUser = false;   // <-- add this
    sessionStorage.removeItem("accessToken");
    sessionStorage.removeItem("refreshToken");
    setUser(obj);
}
```

---

### 4. Conditional UI — Show Accounting Menu

**File:** `frontend/src/components/MenuItem.js` (or wherever the navigation menu is built)

Use the `isAccountingUser` flag from `UserContext` to conditionally render the accounting menu item:

```jsx
import { useContext } from 'react';
import { UserContext } from '../contexts/UserContext';

function MenuItem() {
    const { User } = useContext(UserContext);

    return (
        <>
            {/* ... existing menu items ... */}

            {User.isAccountingUser && (
                <Link to="/accounting">Accounting</Link>
            )}
        </>
    );
}
```

---

### 5. Route Protection

Protect accounting routes so non-accountant users cannot navigate to them (the backend will block them anyway, but frontend guard improves UX):

```jsx
import { useContext } from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { UserContext } from '../contexts/UserContext';

function AccountingRouteGuard() {
    const { User } = useContext(UserContext);

    if (!User.isAccountingUser) {
        return <Navigate to="/" replace />;
    }

    return <Outlet />;
}
```

Usage in router:

```jsx
<Route element={<AccountingRouteGuard />}>
    <Route path="/accounting" element={<AccountingDashboard />} />
    {/* other accounting routes */}
</Route>
```

---

## Summary of Files to Modify

| File | Change |
|------|--------|
| `frontend/src/contexts/UserContext.js` | Add `isAccountingUser: false` to initial state |
| `frontend/src/helper.js` | Capture `is_accounting_user` in `isLogged()`; reset in `logout()` |
| `frontend/src/components/MenuItem.js` | Conditionally render accounting menu |
| `frontend/src/...` (router file) | Add `AccountingRouteGuard` for `/accounting/*` routes |

---

## Backend Reference (for context)

- **User Model:** `controller/models.py` — `CustomUser.is_accounting_user` (BooleanField)
- **Serializer:** `controller/serializer.py` — `RegisterSerializer` now exposes the field
- **Permission:** `accounting/permissions.py` — `IsAccountingUser` guards all accounting endpoints
- **Session Endpoint:** `GET /api/session/` — returns full user data including the flag
- **Accounting User Management:** `python manage.py create_accounting_user` (Django management command)
