import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeOff, FileText, AlertCircle } from 'lucide-react';
import { authService } from '../utils/auth';
import type { LoginCredentials } from '../utils/auth';

export default function Login() {
    const navigate = useNavigate();
    const [formData, setFormData] = useState<LoginCredentials>({
        email: '',
        password: ''
    });
    
    const [showPassword, setShowPassword] = useState(false);
    const [errors, setErrors] = useState<{ [key: string]: string }>({});
    const [isLoading, setIsLoading] = useState(false);
    const [loginError, setLoginError] = useState('');

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
        
        // Clear error when user starts typing
        if (errors[name]) {
            setErrors(prev => ({
                ...prev,
                [name]: ''
            }));
        }
        setLoginError('');
    };

    const validateForm = () => {
        const newErrors: { [key: string]: string } = {};

        if (!formData.email) {
            newErrors.email = 'Email is required';
        } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
            newErrors.email = 'Please enter a valid email address';
        }

        if (!formData.password) {
            newErrors.password = 'Password is required';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        
        if (!validateForm()) {
            return;
        }

        setIsLoading(true);
        setLoginError('');

        try {
            console.log('Attempting login with:', { email: formData.email, password: formData.password });
            const user = authService.login(formData);
            console.log('Login result:', user);
            
            if (user) {
                console.log('Login successful, redirecting to dashboard');
                // Redirect to dashboard
                navigate('/dashboard');
            } else {
                console.log('Login failed - invalid credentials');
                setLoginError('Invalid email or password');
            }
        } catch (error) {
            console.error('Login error:', error);
            setLoginError('An error occurred during login. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md w-full space-y-8">
                <div className="text-center">
                    <div className="flex justify-center mb-4">
                        <div className="bg-[#1e40af] w-12 h-12 flex items-center justify-center rounded-lg shadow-lg">
                            <FileText className="text-white w-7 h-7" />
                        </div>
                    </div>
                    <h2 className="text-3xl font-bold text-white mb-2">
                        Welcome back
                    </h2>
                    <p className="text-gray-300">
                        Sign in to your LegalGuard account
                    </p>
                </div>

                <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
                    <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl shadow-xl p-8 space-y-6 border border-gray-700">
                        {loginError && (
                            <div className="bg-red-900/50 border border-red-700/50 rounded-lg p-4 flex items-center">
                                <AlertCircle className="text-red-400 w-5 h-5 mr-2" />
                                <span className="text-red-300 text-sm">{loginError}</span>
                            </div>
                        )}

                        <div>
                            <label htmlFor="email" className="block text-sm font-medium text-gray-200 mb-2">
                                Email Address
                            </label>
                            <input
                                id="email"
                                name="email"
                                type="email"
                                required
                                value={formData.email}
                                onChange={handleInputChange}
                                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-gray-700/50 text-white placeholder-gray-400 ${
                                    errors.email ? 'border-red-500' : 'border-gray-600'
                                }`}
                                placeholder="Enter your email"
                            />
                            {errors.email && (
                                <p className="mt-1 text-sm text-red-400">{errors.email}</p>
                            )}
                        </div>

        <div>
                            <label htmlFor="password" className="block text-sm font-medium text-gray-200 mb-2">
                                Password
                            </label>
                            <div className="relative">
                                <input
                                    id="password"
                                    name="password"
                                    type={showPassword ? 'text' : 'password'}
                                    required
                                    value={formData.password}
                                    onChange={handleInputChange}
                                    className={`w-full px-4 py-3 pr-12 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-gray-700/50 text-white placeholder-gray-400 ${
                                        errors.password ? 'border-red-500' : 'border-gray-600'
                                    }`}
                                    placeholder="Enter your password"
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-300"
                                >
                                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                                </button>
                            </div>
                            {errors.password && (
                                <p className="mt-1 text-sm text-red-400">{errors.password}</p>
                            )}
                        </div>

                        <div className="flex items-center justify-between">
                            <div className="flex items-center">
                                <input
                                    id="remember-me"
                                    name="remember-me"
                                    type="checkbox"
                                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-600 rounded bg-gray-700"
                                />
                                <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-300">
                                    Remember me
                                </label>
                            </div>
                            <div className="text-sm">
                                <a href="#" className="text-blue-400 hover:text-blue-300 font-medium">
                                    Forgot password?
                                </a>
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full bg-[#1e40af] text-white py-3 px-4 rounded-lg font-semibold hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        >
                            {isLoading ? 'Signing in...' : 'Sign in'}
                        </button>

                        <div className="text-center">
                            <p className="text-sm text-gray-300">
                                Don't have an account?{' '}
                                <Link to="/signup" className="text-blue-400 hover:text-blue-300 font-medium">
                                    Sign up
                                </Link>
                            </p>
                        </div>
                    </div>
                </form>

                <div className="text-center space-y-2">
                    <p className="text-xs text-gray-400">
                        Demo credentials: superadmin@legalguard.com / admin123
                    </p>
                    <button
                        onClick={() => {
                            authService.resetToDefaultUsers();
                            alert('Users reset to default. Try logging in again.');
                        }}
                        className="text-xs text-gray-500 hover:text-gray-400 underline"
                    >
                        Reset to default users
                    </button>
                    <button
                        onClick={() => {
                            authService.testCurrentState();
                        }}
                        className="text-xs text-gray-500 hover:text-gray-400 underline block mt-1"
                    >
                        Test auth system
                    </button>
                </div>
            </div>
        </div>
    );
}