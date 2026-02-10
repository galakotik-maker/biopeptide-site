import { useState, useEffect } from 'react';
import { Shield, UserPlus, Trash2, Users, Crown, ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';
import { authService } from '../utils/auth'; // Assuming authService and types are correctly imported
import type { User, RegisterData } from '../utils/auth';

export default function AdminManagement() {
    const [users, setUsers] = useState<User[]>([]);
    const [showCreateForm, setShowCreateForm] = useState(false);
    const [editingUser, setEditingUser] = useState<User | null>(null); // Not used in provided code but kept for completeness
    const [formData, setFormData] = useState<RegisterData>({
        firstName: '',
        lastName: '',
        email: '',
        password: '',
        company: ''
    });
    const [errors, setErrors] = useState<{ [key: string]: string }>({});
    const [isLoading, setIsLoading] = useState(false);
    const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

    // Effect to load users when the component mounts
    useEffect(() => {
        loadUsers();
    }, []);

    // Function to fetch and set all users
    const loadUsers = () => {
        const allUsers = authService.getAllUsers();
        setUsers(allUsers);
    };

    // Handler for input field changes in the form
    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
        
        // Clear error message for the specific field if input changes
        if (errors[name]) {
            setErrors(prev => ({
                ...prev,
                [name]: ''
            }));
        }
    };

    // Client-side form validation
    const validateForm = () => {
        const newErrors: { [key: string]: string } = {};

        if (!formData.firstName.trim()) {
            newErrors.firstName = 'First name is required';
        }

        if (!formData.lastName.trim()) {
            newErrors.lastName = 'Last name is required';
        }

        if (!formData.email) {
            newErrors.email = 'Email is required';
        } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
            newErrors.email = 'Please enter a valid email address';
        }

        if (!formData.company.trim()) {
            newErrors.company = 'Company name is required';
        }

        // Password is only required for new user creation, not for editing existing users
        if (!editingUser && !formData.password) {
            newErrors.password = 'Password is required';
        } else if (!editingUser && formData.password.length < 6) {
            newErrors.password = 'Password must be at least 6 characters';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    // Handler for creating a new admin user
    const handleCreateAdmin = async (e: React.FormEvent) => {
        e.preventDefault();
        
        if (!validateForm()) {
            return;
        }

        setIsLoading(true);
        setMessage(null); // Clear previous messages

        try {
            const newAdmin = authService.createAdmin(formData);
            
            if (newAdmin) {
                setMessage({ type: 'success', text: 'Admin created successfully!' });
                setShowCreateForm(false); // Hide the form on success
                resetForm(); // Clear form fields
                loadUsers(); // Reload user list to show new admin
            } else {
                setMessage({ type: 'error', text: 'Failed to create admin. Email might already exist.' });
            }
        } catch (error) {
            console.error("Error creating admin:", error); // Log the error for debugging
            setMessage({ type: 'error', text: 'An error occurred while creating admin.' });
        } finally {
            setIsLoading(false);
        }
    };

    // Handler for deleting a user
    const handleDeleteUser = (userId: string) => {
        // Replace window.confirm with a custom modal for better UI/UX and consistent styling
        // For this example, keeping window.confirm as per original but noted for improvement
        if (window.confirm('Are you sure you want to delete this user?')) {
            const success = authService.deleteUser(userId);
            
            if (success) {
                setMessage({ type: 'success', text: 'User deleted successfully!' });
                loadUsers(); // Reload user list after deletion
            } else {
                setMessage({ type: 'error', text: 'Failed to delete user.' });
            }
        }
    };

    // Handler for updating a user's role
    const handleUpdateRole = (userId: string, newRole: 'user' | 'admin') => {
        const success = authService.updateUserRole(userId, newRole);
        
        if (success) {
            setMessage({ type: 'success', text: 'User role updated successfully!' });
            loadUsers(); // Reload user list after role update
        } else {
            setMessage({ type: 'error', text: 'Failed to update user role.' });
        }
    };

    // Function to reset the form fields and errors
    const resetForm = () => {
        setFormData({
            firstName: '',
            lastName: '',
            email: '',
            password: '',
            company: ''
        });
        setErrors({});
        setEditingUser(null);
    };

    // Helper function to get role badge styling
    const getRoleBadge = (role: string) => {
        const baseClasses = "px-2 py-1 rounded-full text-xs font-medium";
        
        switch (role) {
            case 'super-admin':
                return (
                    <span className={`${baseClasses} bg-red-900/20 text-red-400 border border-red-500/30 flex items-center gap-1`}>
                        <Crown className="w-3 h-3" />
                        Super Admin
                    </span>
                );
            case 'admin':
                return (
                    <span className={`${baseClasses} bg-blue-900/20 text-blue-400 border border-blue-500/30 flex items-center gap-1`}>
                        <Shield className="w-3 h-3" />
                        Admin
                    </span>
                );
            default:
                return (
                    <span className={`${baseClasses} bg-slate-700 text-gray-300 border border-slate-600 flex items-center gap-1`}>
                        <Users className="w-3 h-3" />
                        User
                    </span>
                );
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 to-slate-950 py-8 font-sans antialiased">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="bg-slate-800 rounded-lg shadow-xl border border-slate-700">
                    <div className="px-6 py-4 border-b border-slate-700">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-4">
                                <Link
                                    to="/dashboard"
                                    className="flex items-center gap-2 text-gray-400 hover:text-blue-400 transition-colors duration-200"
                                >
                                    <ArrowLeft className="w-4 h-4" />
                                    <span className="text-sm font-medium">Back to Dashboard</span>
                                </Link>
                                <div className="h-6 w-px bg-slate-600"></div> {/* Adjusted color */}
                                <div>
                                    <h1 className="text-2xl font-bold text-white">Admin Management</h1>
                                    <p className="text-gray-400">Manage users and their roles</p>
                                </div>
                            </div>
                            <button
                                onClick={() => {
                                    setShowCreateForm(true);
                                    resetForm(); // Reset form when opening create form
                                }}
                                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 shadow-md"
                            >
                                <UserPlus className="w-4 h-4" />
                                Create Admin
                            </button>
                        </div>
                    </div>

                    {message && (
                        <div className={`px-6 py-3 ${
                            message.type === 'success' ? 'bg-green-900/20 text-green-400 border border-green-500/30' : 'bg-red-900/20 text-red-400 border border-red-500/30'
                        }`}>
                            {message.text}
                        </div>
                    )}

                    {showCreateForm && (
                        <div className="px-6 py-4 border-b border-slate-700">
                            <form onSubmit={handleCreateAdmin} className="space-y-4">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4"> {/* Added responsiveness for grid */}
                                    <div>
                                        <label htmlFor="firstName" className="block text-sm font-medium text-gray-300 mb-1">
                                            First Name *
                                        </label>
                                        <input
                                            type="text"
                                            id="firstName"
                                            name="firstName"
                                            value={formData.firstName}
                                            onChange={handleInputChange}
                                            className={`w-full px-3 py-2 border rounded-md bg-slate-700 text-white placeholder-gray-400 ${
                                                errors.firstName ? 'border-red-500' : 'border-slate-600'
                                            } focus:border-blue-500 focus:ring-1 focus:ring-blue-500`}
                                        />
                                        {errors.firstName && (
                                            <p className="text-sm text-red-400 mt-1">{errors.firstName}</p>
                                        )}
                                    </div>
                                    <div>
                                        <label htmlFor="lastName" className="block text-sm font-medium text-gray-300 mb-1">
                                            Last Name *
                                        </label>
                                        <input
                                            type="text"
                                            id="lastName"
                                            name="lastName"
                                            value={formData.lastName}
                                            onChange={handleInputChange}
                                            className={`w-full px-3 py-2 border rounded-md bg-slate-700 text-white placeholder-gray-400 ${
                                                errors.lastName ? 'border-red-500' : 'border-slate-600'
                                            } focus:border-blue-500 focus:ring-1 focus:ring-blue-500`}
                                        />
                                        {errors.lastName && (
                                            <p className="text-sm text-red-400 mt-1">{errors.lastName}</p>
                                        )}
                                    </div>
                                    <div>
                                        <label htmlFor="email" className="block text-sm font-medium text-gray-300 mb-1">
                                            Email *
                                        </label>
                                        <input
                                            type="email"
                                            id="email"
                                            name="email"
                                            value={formData.email}
                                            onChange={handleInputChange}
                                            className={`w-full px-3 py-2 border rounded-md bg-slate-700 text-white placeholder-gray-400 ${
                                                errors.email ? 'border-red-500' : 'border-slate-600'
                                            } focus:border-blue-500 focus:ring-1 focus:ring-blue-500`}
                                        />
                                        {errors.email && (
                                            <p className="text-sm text-red-400 mt-1">{errors.email}</p>
                                        )}
                                    </div>
                                    <div>
                                        <label htmlFor="company" className="block text-sm font-medium text-gray-300 mb-1">
                                            Company *
                                        </label>
                                        <input
                                            type="text"
                                            id="company"
                                            name="company"
                                            value={formData.company}
                                            onChange={handleInputChange}
                                            className={`w-full px-3 py-2 border rounded-md bg-slate-700 text-white placeholder-gray-400 ${
                                                errors.company ? 'border-red-500' : 'border-slate-600'
                                            } focus:border-blue-500 focus:ring-1 focus:ring-blue-500`}
                                        />
                                        {errors.company && (
                                            <p className="text-sm text-red-400 mt-1">{errors.company}</p>
                                        )}
                                    </div>
                                    <div>
                                        <label htmlFor="password" className="block text-sm font-medium text-gray-300 mb-1">
                                            Password *
                                        </label>
                                        <input
                                            type="password"
                                            id="password"
                                            name="password"
                                            value={formData.password}
                                            onChange={handleInputChange}
                                            className={`w-full px-3 py-2 border rounded-md bg-slate-700 text-white placeholder-gray-400 ${
                                                errors.password ? 'border-red-500' : 'border-slate-600'
                                            } focus:border-blue-500 focus:ring-1 focus:ring-blue-500`}
                                        />
                                        {errors.password && (
                                            <p className="text-sm text-red-400 mt-1">{errors.password}</p>
                                        )}
                                    </div>
                                </div>
                                <div className="flex gap-2 pt-4"> {/* Added padding top */}
                                    <button
                                        type="submit"
                                        disabled={isLoading}
                                        className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors shadow-md flex items-center gap-2"
                                    >
                                        {isLoading ? (
                                            <>
                                                <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                                </svg>
                                                Creating...
                                            </>
                                        ) : (
                                            <>
                                                <UserPlus className="w-4 h-4" />
                                                Create Admin
                                            </>
                                        )}
                                    </button>
                                    <button
                                        type="button"
                                        onClick={() => {
                                            setShowCreateForm(false);
                                            resetForm();
                                        }}
                                        className="bg-slate-600 text-gray-300 px-4 py-2 rounded-md hover:bg-slate-500 transition-colors shadow-md"
                                    >
                                        Cancel
                                    </button>
                                </div>
                            </form>
                        </div>
                    )}

                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-slate-700"> {/* Adjusted divider */}
                            <thead className="bg-slate-800"> {/* Adjusted background */}
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                                        User
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                                        Company
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                                        Role
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                                        Created
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                                        Actions
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="bg-slate-800 divide-y divide-slate-700"> {/* Adjusted background and divider */}
                                {users.length > 0 ? (
                                    users.map((user) => (
                                        <tr key={user.id} className="hover:bg-slate-700/20 transition-colors duration-200"> {/* Adjusted hover */}
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <div>
                                                    <div className="text-sm font-medium text-white">
                                                        {user.firstName} {user.lastName}
                                                    </div>
                                                    <div className="text-sm text-gray-400">{user.email}</div>
                                                </div>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                                                {user.company}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                {getRoleBadge(user.role)}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                                                {new Date(user.createdAt).toLocaleDateString()}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                                {user.role !== 'super-admin' && (
                                                    <div className="flex gap-2">
                                                        {user.role === 'admin' ? (
                                                            <button
                                                                onClick={() => handleUpdateRole(user.id, 'user')}
                                                                className="text-blue-400 hover:text-blue-300 transition-colors flex items-center gap-1"
                                                                title="Demote to User"
                                                            >
                                                                <Users className="w-4 h-4" /> Demote
                                                            </button>
                                                        ) : (
                                                            <button
                                                                onClick={() => handleUpdateRole(user.id, 'admin')}
                                                                className="text-green-400 hover:text-green-300 transition-colors flex items-center gap-1"
                                                                title="Promote to Admin"
                                                            >
                                                                <Shield className="w-4 h-4" /> Promote
                                                            </button>
                                                        )}
                                                        <button
                                                            onClick={() => handleDeleteUser(user.id)}
                                                            className="text-red-400 hover:text-red-300 transition-colors flex items-center gap-1"
                                                            title="Delete User"
                                                        >
                                                            <Trash2 className="w-4 h-4" />
                                                            Delete
                                                        </button>
                                                    </div>
                                                )}
                                            </td>
                                        </tr>
                                    ))
                                ) : (
                                    <tr>
                                        <td colSpan={5} className="px-6 py-4 text-center text-gray-400">
                                            No users found.
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
}
