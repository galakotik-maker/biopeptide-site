import { Link, useNavigate } from 'react-router-dom';
import { FileText, LogOut, Crown, Shield, Users, Settings } from 'lucide-react';
import { authService } from '../../utils/auth';
import { useState } from 'react';

export default function Header() {
    const navigate = useNavigate();
    const [showDropdown, setShowDropdown] = useState(false);
    const currentUser = authService.getCurrentUser();
    const isAuthenticated = authService.isAuthenticated();

    // Handles user logout and navigates to the home page
    const handleLogout = () => {
        authService.logout();
        navigate('/');
    };

    // Returns a styled badge for user roles
    const getRoleBadge = (role: string) => {
        const baseClasses = "px-2 py-1 rounded-full text-xs font-medium flex items-center gap-1";
        
        switch (role) {
            case 'super-admin':
                return (
                    <span className={`${baseClasses} bg-red-900/20 text-red-400 border border-red-500/30`}> {/* Adjusted colors for dark theme */}
                        <Crown className="w-3 h-3" />
                        Super Admin
                    </span>
                );
            case 'admin':
                return (
                    <span className={`${baseClasses} bg-blue-900/20 text-blue-400 border border-blue-500/30`}> {/* Adjusted colors for dark theme */}
                        <Shield className="w-3 h-3" />
                        Admin
                    </span>
                );
            default:
                return (
                    <span className={`${baseClasses} bg-slate-700 text-gray-300 border border-slate-600`}> {/* Adjusted colors for dark theme */}
                        <Users className="w-3 h-3" />
                        User
                    </span>
                );
        }
    };

    // Render header for unauthenticated users
    if (!isAuthenticated) {
        return (
            <header className="w-full sticky top-0 z-50 bg-gradient-to-br from-blue-900 to-slate-950 backdrop-blur-sm bg-opacity-90 shadow-2xl text-gray-100 font-sans antialiased"> {/* Added font-sans and antialiased here */}
                <div className="max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-20">
                    <div className="flex items-center gap-3">
                        <div className="bg-blue-600 w-10 h-10 flex items-center justify-center rounded-md shadow-lg"> {/* Adjusted color */}
                            <FileText className="text-white w-6 h-6" />
                        </div>
                        <Link
                            to="/"
                            className="text-2xl font-bold text-white tracking-wide hover:text-blue-200 transition-colors duration-200"
                        >
                            LegalGuard
                        </Link>
                    </div>

                    <nav className="hidden md:flex items-center gap-6 text-sm font-medium">
                        <Link to="/compliance" className="text-gray-300 hover:text-blue-300">Compliance</Link>
                        <Link to="/regulations" className="text-gray-300 hover:text-blue-300">Regulations</Link>
                        <Link to="/journal" className="text-gray-300 hover:text-blue-300">Journal</Link>
                    </nav>

                    <div className="flex items-center gap-3">
                        <Link
                            to="/login"
                            className="text-blue-300 hover:bg-blue-800/30 px-4 py-2 rounded-md text-sm font-medium transition-colors duration-200 border border-transparent hover:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-900"
                        >
                            Sign In
                        </Link>
                        <Link
                            to="/signup"
                            className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 transition-colors duration-200 shadow-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-900"
                        >
                            Register
                        </Link>
                    </div>
                </div>
            </header>
        );
    }

    // Render header for authenticated users
    return (
        <header className="w-full sticky top-0 z-50 bg-gradient-to-br from-blue-900 to-slate-950 backdrop-blur-sm bg-opacity-90 shadow-2xl text-gray-100 font-sans antialiased"> {/* Added font-sans and antialiased here */}
            <div className="max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-20">
                <div className="flex items-center gap-3">
                    <div className="bg-blue-600 w-10 h-10 flex items-center justify-center rounded-md shadow-lg"> {/* Adjusted color */}
                        <FileText className="text-white w-6 h-6" />
                    </div>
                    <Link
                        to="/dashboard"
                        className="text-2xl font-bold text-white tracking-wide hover:text-blue-200 transition-colors duration-200"
                    >
                        LegalGuard
                    </Link>
                </div>

                <nav className="hidden md:flex items-center gap-6 text-sm font-medium">
                    <Link to="/dashboard" className="text-gray-300 hover:text-blue-300">Dashboard</Link>
                    <Link to="/analyze" className="text-gray-300 hover:text-blue-300">Analyze</Link>
                    <Link to="/ai-insights" className="text-gray-300 hover:text-blue-300">AI Insights</Link>
                    <Link to="/compliance" className="text-gray-300 hover:text-blue-300">Compliance</Link>
                    <Link to="/regulations" className="text-gray-300 hover:text-blue-300">Regulations</Link>
                    <Link to="/reports" className="text-gray-300 hover:text-blue-300">Reports</Link>
                    <Link to="/journal" className="text-gray-300 hover:text-blue-300">Journal</Link>
                    {authService.hasRole('super-admin') && (
                        <Link to="/admin" className="text-gray-300 hover:text-blue-300">Admin</Link>
                    )}
                </nav>

                <div className="flex items-center gap-3">
                    <div className="hidden md:block">
                        {getRoleBadge(currentUser?.role || 'user')}
                    </div>
                    
                    <div className="relative">
                        <button
                            onClick={() => setShowDropdown(!showDropdown)}
                            className="flex items-center gap-2 text-white hover:text-blue-200 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-900 rounded-full" // Added rounded-full for better focus ring
                        >
                            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-sm font-medium">
                                {currentUser?.firstName?.charAt(0)}{currentUser?.lastName?.charAt(0)}
                            </div>
                            <span className="hidden md:block text-sm font-medium">
                                {currentUser?.firstName} {currentUser?.lastName}
                            </span>
                        </button>

                        {showDropdown && (
                            <div className="absolute right-0 mt-2 w-48 bg-slate-800 rounded-md shadow-lg py-1 z-50 border border-slate-700"> {/* Adjusted colors for dark theme */}
                                <div className="px-4 py-2 border-b border-slate-700"> {/* Adjusted color */}
                                    <p className="text-sm font-medium text-white">
                                        {currentUser?.firstName} {currentUser?.lastName}
                                    </p>
                                    <p className="text-xs text-gray-400">{currentUser?.email}</p> {/* Adjusted color */}
                                    <div className="mt-1">
                                        {getRoleBadge(currentUser?.role || 'user')}
                                    </div>
                                </div>
                                
                                <Link
                                    to="/settings"
                                    className="flex items-center gap-2 px-4 py-2 text-sm text-gray-300 hover:bg-slate-700/50 transition-colors" // Adjusted colors for dark theme
                                    onClick={() => setShowDropdown(false)}
                                >
                                    <Settings className="w-4 h-4 text-blue-300" /> {/* Adjusted icon color */}
                                    Settings
                                </Link>
                                
                                {authService.hasRole('super-admin') && (
                                    <Link
                                        to="/admin"
                                        className="flex items-center gap-2 px-4 py-2 text-sm text-gray-300 hover:bg-slate-700/50 transition-colors" // Adjusted colors for dark theme
                                        onClick={() => setShowDropdown(false)}
                                    >
                                        <Crown className="w-4 h-4 text-red-300" /> {/* Adjusted icon color */}
                                        Admin Panel
                                    </Link>
                                )}
                                
                                <button
                                    onClick={() => {
                                        handleLogout();
                                        setShowDropdown(false);
                                    }}
                                    className="flex items-center gap-2 px-4 py-2 text-sm text-red-400 hover:bg-red-900/20 w-full text-left transition-colors" // Adjusted colors for dark theme
                                >
                                    <LogOut className="w-4 h-4" />
                                    Sign Out
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </header>
    );
}
