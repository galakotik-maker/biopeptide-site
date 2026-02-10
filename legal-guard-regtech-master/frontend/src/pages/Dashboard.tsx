import { FileText, Gauge, AlertCircle, BookText, ChevronRight, Brain } from 'lucide-react';
import Header from '../components/layout/Header';

export default function Dashboard() {
    // Mock data for stats
    const stats = [
        { title: "Contracts Analyzed", value: "142", icon: <FileText className="w-5 h-5" />, trend: "up", change: "12%" },
        { title: "Compliance Rate", value: "87%", icon: <Gauge className="w-5 h-5" />, trend: "up", change: "5%" },
        { title: "Alerts Detected", value: "23", icon: <AlertCircle className="w-5 h-5" />, trend: "down", change: "3%" }
    ];

    // Mock data for recent activities
    const recentActivities = [
        { id: 1, contract: "Employment Agreement", time: "10 mins ago", risk: "medium" },
        { id: 2, contract: "NDA with TechCorp", time: "2 hours ago", risk: "low" },
        { id: 3, contract: "Data Processing Addendum", time: "1 day ago", risk: "high" }
    ];

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 to-slate-950 text-gray-100 font-sans antialiased">
            <Header />

            {/* Hero section */}
            <section className="relative py-24 px-4 sm:px-6 lg:px-8 text-center overflow-hidden">
                {/* If want can put a bg image at hero section */}
                <div className="absolute inset-0" style={{ backgroundImage: '")', backgroundSize: 'cover', backgroundRepeat: 'no-repeat', backgroundPosition: 'center' }}>
                    <div className="absolute inset-0 bg-blue-950 opacity-40 mix-blend-multiply"></div>
                </div>
                <div className="relative max-w-4xl mx-auto z-10">
                    <h1 className="text-4xl md:text-5xl lg:text-6xl font-extrabold text-white mb-6 leading-tight drop-shadow-2xl">
                        Automated Legal Compliance for Modern Businesses
                    </h1>
                    <p className="text-lg md:text-xl text-gray-300 max-w-2xl mx-auto opacity-90 font-medium leading-relaxed">
                        Streamline your contract analysis and regulatory compliance across multiple jurisdictions with our AI-powered platform.
                    </p>
                </div>
            </section>

            {/* Stats cards section */}
            <section className="py-20 px-4 sm:px-6 lg:px-8">
                <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {stats.map((stat, index) => (
                        <div
                            key={index}
                            className="bg-slate-800 p-6 rounded-lg shadow-2xl hover:shadow-blue-500/40 border border-slate-700
                                transform hover:-translate-y-2 hover:scale-105 transition-all duration-300 ease-in-out cursor-pointer"
                        >
                            <div className="flex items-start gap-5">
                                <div className="p-3 rounded-xl bg-blue-900/60 text-blue-300 flex-shrink-0 shadow-inner">
                                    {stat.icon}
                                </div>
                                <div className="flex-grow">
                                    <p className="text-sm text-gray-300 font-medium uppercase tracking-wider mb-1 leading-snug">{stat.title}</p>
                                    <p className="text-4xl font-extrabold text-white mt-1 mb-2 leading-none">{stat.value}</p>
                                    <p className={`text-sm mt-2 font-semibold ${stat.trend === 'up' ? 'text-green-600' : 'text-red-600'} leading-snug`}>
                                        {stat.change} {stat.trend === 'up' ? 'increase' : 'decrease'} from last month
                                    </p>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </section>

            {/* Recent activity section */}
            <section className="py-16 px-4 sm:px-6 lg:px-8">
                <div className="max-w-6xl mx-auto grid lg:grid-cols-3 gap-10">
                    <div className="lg:col-span-2 bg-slate-800 border border-slate-700 rounded-lg shadow-2xl">
                        <div className="flex justify-between items-center px-6 py-5 border-b border-slate-700/50">
                            <h2 className="text-xl font-semibold text-blue-300">Recent Activity</h2>
                            {/* <a href="#" className="text-blue-300 text-sm hover:underline flex items-center gap-1 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-800">
                                View all <ChevronRight className="w-4 h-4" />
                            </a> */}
                        </div>
                        <div className="divide-y divide-slate-700/50">
                            {recentActivities.map((activity) => (
                                <div key={activity.id} className="px-6 py-4 flex justify-between items-center hover:bg-slate-700/20 transition-colors duration-200 cursor-pointer">
                                    <div className="flex items-center gap-4">
                                        <div className={`p-2 rounded-md ${activity.risk === 'high' ? 'bg-red-700/20 text-red-600' : activity.risk === 'medium' ? 'bg-amber-700/20 text-amber-600' : 'bg-green-700/20 text-green-600'} flex-shrink-0 shadow-sm`}>
                                            <FileText className="w-5 h-5" />
                                        </div>
                                        <div>
                                            <p className="text-base font-medium text-white leading-snug">{activity.contract}</p>
                                            <p className="text-xs text-gray-300 mt-0.5 leading-snug">{activity.time}</p>
                                        </div>
                                    </div>
                                    <span className={`text-xs px-3 py-1 rounded-full font-semibold ${activity.risk === 'high' ? 'bg-red-700/30 text-red-300' : activity.risk === 'medium' ? 'bg-amber-700/30 text-amber-200' : 'bg-green-700/30 text-green-200'} border border-opacity-20 ${activity.risk === 'high' ? 'border-red-500' : activity.risk === 'medium' ? 'border-amber-500' : 'border-green-500'}`}>
                                        {activity.risk} risk
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Quick Actions - link to compliance and regulations */}
                    <aside className="lg:col-span-1 bg-slate-800 border border-slate-700 rounded-lg p-6 shadow-2xl sticky top-24 h-fit">
                        <h3 className="text-xl font-semibold text-blue-300 mb-5">Quick Actions</h3>
                        <div className="space-y-4">
                            <a
                            href="/compliance"
                            className="flex items-center gap-4 p-4 border border-slate-700 rounded-md hover:bg-slate-700/20 group transform hover:translate-x-1 hover:shadow-md transition-all duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-800"
                            >
                            <div className="p-3 bg-blue-700/50 text-blue-200 rounded-md group-hover:bg-blue-700/70 flex-shrink-0 shadow-sm">
                                <Gauge className="w-5 h-5" />
                            </div>
                            <div className="flex-grow">
                                <h4 className="text-base font-medium text-white leading-snug">Compliance Dashboard</h4>
                                <p className="text-xs text-gray-300 mt-0.5 leading-snug">Access Compliance Dashboard</p>
                            </div>
                            <ChevronRight className="ml-auto w-5 h-5 text-blue-400 group-hover:translate-x-1 transition-transform duration-200" />
                            </a>
                            <a
                            href="/ai-insights"
                            className="flex items-center gap-4 p-4 border border-slate-700 rounded-md hover:bg-slate-700/20 group transform hover:translate-x-1 hover:shadow-md transition-all duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-800"
                            >
                            <div className="p-3 bg-purple-700/50 text-purple-200 rounded-md group-hover:bg-purple-700/70 flex-shrink-0 shadow-sm">
                                <Brain className="w-5 h-5" />
                            </div>
                            <div className="flex-grow">
                                <h4 className="text-base font-medium text-white leading-snug">AI Insights</h4>
                                <p className="text-xs text-gray-300 mt-0.5 leading-snug">Get AI-powered document summaries</p>
                            </div>
                            <ChevronRight className="ml-auto w-5 h-5 text-blue-400 group-hover:translate-x-1 transition-transform duration-200" />
                            </a>
                            <a
                            href="/regulations"
                            className="flex items-center gap-4 p-4 border border-slate-700 rounded-md hover:bg-slate-700/20 group transform hover:translate-x-1 hover:shadow-md transition-all duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-800"
                            >
                            <div className="p-3 bg-blue-600/50 text-blue-100 rounded-md group-hover:bg-blue-600/70 flex-shrink-0 shadow-sm">
                                <BookText className="w-5 h-5" />
                            </div>
                            <div className="flex-grow">
                                <h4 className="text-base font-medium text-white leading-snug">Regulatory Library</h4>
                                <p className="text-xs text-gray-300 mt-0.5 leading-snug">Access regulatory library</p>
                            </div>
                            <ChevronRight className="ml-auto w-5 h-5 text-blue-400 group-hover:translate-x-1 transition-transform duration-200" />
                            </a>
                        </div>
                    </aside>
                </div>
            </section>
        </div>
    );
}
