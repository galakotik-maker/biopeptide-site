import usersData from '../data/users.json';

// Fallback default users in case JSON import fails
const DEFAULT_USERS = [
  {
    id: "1",
    firstName: "Super",
    lastName: "Admin",
    email: "superadmin@legalguard.com",
    password: "admin123",
    company: "LegalGuard",
    role: "super-admin" as const,
    createdAt: "2024-01-01T00:00:00.000Z"
  }
];

export interface User {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  password: string;
  company: string;
  role: 'user' | 'admin' | 'super-admin';
  createdAt: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
  company: string;
}

class AuthService {
  private users: User[] = [];

  constructor() {
    console.log('AuthService constructor called');
    
    // Try to load from JSON, fallback to default if it fails
    try {
      this.users = (usersData.users as User[]);
      console.log('Users loaded from JSON:', this.users);
    } catch (error) {
      console.error('Failed to load users from JSON, using defaults:', error);
      this.users = DEFAULT_USERS;
    }
    
    console.log('Initial users:', this.users);
    
    // Load users from localStorage if available
    const storedUsers = localStorage.getItem('users');
    console.log('Stored users from localStorage:', storedUsers);
    
    if (storedUsers) {
      try {
        this.users = JSON.parse(storedUsers);
        console.log('Users loaded from localStorage:', this.users);
      } catch (error) {
        console.error('Failed to parse stored users, using defaults:', error);
        this.users = DEFAULT_USERS;
      }
    } else {
      // Initialize with default users
      console.log('No stored users found, initializing with default users');
      localStorage.setItem('users', JSON.stringify(this.users));
      console.log('Default users saved to localStorage');
    }
    
    console.log('Final users array:', this.users);
  }

  private saveUsers(): void {
    localStorage.setItem('users', JSON.stringify(this.users));
  }

  login(credentials: LoginCredentials): User | null {
    console.log('AuthService.login called with:', credentials);
    console.log('Available users:', this.users);
    
    const user = this.users.find(
      u => u.email === credentials.email && u.password === credentials.password
    );
    
    console.log('Found user:', user);
    
    if (user) {
      // Store current user in session
      const { password, ...userWithoutPassword } = user;
      localStorage.setItem('currentUser', JSON.stringify(userWithoutPassword));
      console.log('User stored in localStorage');
      return user;
    }
    
    return null;
  }

  register(userData: RegisterData): User | null {
    // Check if user already exists
    if (this.users.find(u => u.email === userData.email)) {
      return null;
    }

    const newUser: User = {
      id: Date.now().toString(),
      ...userData,
      role: 'user', // Default role
      createdAt: new Date().toISOString()
    };

    this.users.push(newUser);
    this.saveUsers();

    // Auto-login after registration
    const { password, ...userWithoutPassword } = newUser;
    localStorage.setItem('currentUser', JSON.stringify(userWithoutPassword));

    return newUser;
  }

  logout(): void {
    localStorage.removeItem('currentUser');
  }

  getCurrentUser(): User | null {
    const userStr = localStorage.getItem('currentUser');
    if (userStr) {
      const user = JSON.parse(userStr);
      // Get full user data including password
      return this.users.find(u => u.id === user.id) || null;
    }
    return null;
  }

  isAuthenticated(): boolean {
    return this.getCurrentUser() !== null;
  }

  hasRole(role: 'user' | 'admin' | 'super-admin'): boolean {
    const user = this.getCurrentUser();
    if (!user) return false;

    const roleHierarchy = {
      'user': 1,
      'admin': 2,
      'super-admin': 3
    };

    return roleHierarchy[user.role] >= roleHierarchy[role];
  }

  getAllUsers(): User[] {
    return this.users.map(user => {
      const { password, ...userWithoutPassword } = user;
      return userWithoutPassword as User;
    });
  }

  createAdmin(userData: RegisterData): User | null {
    if (!this.hasRole('super-admin')) {
      return null;
    }

    if (this.users.find(u => u.email === userData.email)) {
      return null;
    }

    const newAdmin: User = {
      id: Date.now().toString(),
      ...userData,
      role: 'admin',
      createdAt: new Date().toISOString()
    };

    this.users.push(newAdmin);
    this.saveUsers();
    return newAdmin;
  }

  deleteUser(userId: string): boolean {
    if (!this.hasRole('super-admin')) {
      return false;
    }

    const userIndex = this.users.findIndex(u => u.id === userId);
    if (userIndex === -1) return false;

    // Don't allow super-admin to delete themselves
    const currentUser = this.getCurrentUser();
    if (currentUser && currentUser.id === userId) {
      return false;
    }

    this.users.splice(userIndex, 1);
    this.saveUsers();
    return true;
  }

  updateUserRole(userId: string, newRole: 'user' | 'admin'): boolean {
    if (!this.hasRole('super-admin')) {
      return false;
    }

    const user = this.users.find(u => u.id === userId);
    if (!user) return false;

    // Don't allow changing super-admin role
    if (user.role === 'super-admin') {
      return false;
    }

    user.role = newRole;
    this.saveUsers();
    return true;
  }

  // Method to reset users to default for testing
  resetToDefaultUsers(): void {
    console.log('Resetting to default users');
    localStorage.removeItem('users');
    localStorage.removeItem('currentUser');
    
    // Try to use JSON data, fallback to defaults
    try {
      this.users = (usersData.users as User[]);
    } catch (error) {
      console.error('Failed to load from JSON during reset, using defaults:', error);
      this.users = DEFAULT_USERS;
    }
    
    localStorage.setItem('users', JSON.stringify(this.users));
    console.log('Reset complete. Users:', this.users);
  }

  // Method to test the current state
  testCurrentState(): void {
    console.log('=== AUTH SERVICE TEST ===');
    console.log('usersData:', usersData);
    console.log('usersData.users:', usersData.users);
    console.log('this.users:', this.users);
    console.log('localStorage users:', localStorage.getItem('users'));
    console.log('localStorage currentUser:', localStorage.getItem('currentUser'));
    
    // Test the exact credentials
    const testCredentials = {
      email: 'superadmin@legalguard.com',
      password: 'admin123'
    };
    
    const testUser = this.users.find(
      u => u.email === testCredentials.email && u.password === testCredentials.password
    );
    
    console.log('Test user found:', testUser);
    console.log('=== END TEST ===');
  }
}

export const authService = new AuthService(); 