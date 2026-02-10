# LegalGuard Frontend

## New Authentication System

### Features Implemented

1. **Local User Storage**: User credentials are stored locally in the browser's localStorage
2. **Role-Based Access Control**: Three user roles with different permissions:
   - **User**: Basic access to dashboard and analysis features
   - **Admin**: User permissions plus additional management capabilities
   - **Super Admin**: Full system access including user management (red-tagged)

3. **Authentication Pages**:
   - **Login Page**: Secure sign-in with form validation
   - **Signup Page**: User registration with local storage
   - **Landing Page**: Public marketing page with call-to-action

4. **Protected Routes**: Dashboard and analysis features are locked behind authentication
5. **Public Access**: Compliance and Regulations pages remain publicly accessible

### Default Super Admin Credentials

- **Email**: superadmin@legalguard.com
- **Password**: admin123

### User Management

Super admins can:
- Create new admin users
- Promote users to admin role
- Demote admins to user role
- Delete users (except themselves)
- View all users in the system

### File Structure

```
src/
├── data/
│   └── users.json          # Initial user data
├── utils/
│   └── auth.ts            # Authentication service
├── components/
│   ├── ProtectedRoute.tsx # Route protection component
│   └── layout/
│       └── Header.tsx     # Updated header with user info
├── pages/
│   ├── Landing.tsx        # New landing page
│   ├── Login.tsx          # Updated login page
│   ├── Signup.tsx         # Updated signup page
│   ├── AdminManagement.tsx # Admin panel for super admins
│   └── ...                # Other existing pages
└── App.tsx                # Updated routing
```

### How to Use

1. **Start the development server**:
   ```bash
   npm run dev
   ```

2. **Access the application**:
   - Visit the landing page at `/`
   - Sign up for a new account or use the default super admin credentials
   - Access the dashboard and other protected features after login

3. **Super Admin Features**:
   - Login with super admin credentials
   - Access the Admin panel from the header dropdown
   - Manage users and their roles

### Security Notes

- This is a demo implementation with local storage
- Passwords are stored in plain text (not recommended for production)
- User data persists in browser localStorage
- For production, implement proper backend authentication with encrypted passwords

### Navigation

- **Public Routes**: `/`, `/login`, `/signup`, `/compliance`, `/regulations`
- **Protected Routes**: `/dashboard`, `/analyze`, `/bulk-analyze`, `/reports`, `/settings`
- **Admin Routes**: `/admin` (super admin only)
