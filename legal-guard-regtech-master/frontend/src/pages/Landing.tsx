import { Link } from 'react-router-dom';
import { Shield, FileText, TrendingUp, ArrowRight, Brain, Send } from 'lucide-react'; // Added Brain icon for consistency
import Header from '../components/layout/Header';

export default function Landing() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-slate-950 text-gray-100 font-sans antialiased">
      <Header />

      {/* Hero Section */}
      <div className="relative overflow-hidden py-24 px-4 sm:px-6 lg:px-8 text-center bg-gray-900/70">
        <div className="relative max-w-4xl mx-auto z-10">
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-extrabold text-white mb-6 leading-tight drop-shadow-2xl">
            Streamline Your
            <span className="text-blue-400"> Legal Compliance</span>
          </h1>
          <p className="text-lg md:text-xl text-gray-300 max-w-2xl mx-auto opacity-90 font-medium leading-relaxed">
            AI-powered document analysis and regulatory compliance monitoring.
            Stay ahead of legal requirements with automated risk assessment and real-time alerts.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center mt-8">
            <Link to="/signup" className="bg-blue-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-blue-700 transition-colors flex items-center justify-center shadow-lg transform hover:-translate-y-1">
              Start Free Trial
              <ArrowRight className="ml-2 w-5 h-5" />
            </Link>
            <Link to="/compliance" className="border-2 border-blue-600 text-blue-300 px-8 py-4 rounded-lg text-lg font-semibold hover:bg-slate-800 transition-colors shadow-lg transform hover:-translate-y-1">
              Learn More
            </Link>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-24 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-gray-900/80 to-slate-950/80">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Why Choose LegalGuard?
            </h2>
            <p className="text-lg text-gray-300 max-w-2xl mx-auto">
              Comprehensive legal compliance solutions designed for modern businesses.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center p-6 bg-slate-800 rounded-lg border border-slate-700 shadow-2xl transform hover:-translate-y-2 hover:scale-105 transition-all duration-300 ease-in-out">
              <div className="bg-blue-900/60 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 border border-blue-700/30 shadow-inner">
                <FileText className="text-blue-300 w-8 h-8" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">
                Document Analysis
              </h3>
              <p className="text-gray-300">
                AI-powered analysis of contracts, policies, and legal documents with instant risk assessment.
              </p>
            </div>

            <div className="text-center p-6 bg-slate-800 rounded-lg border border-slate-700 shadow-2xl transform hover:-translate-y-2 hover:scale-105 transition-all duration-300 ease-in-out">
              <div className="bg-green-900/60 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 border border-green-700/30 shadow-inner">
                <Shield className="text-green-300 w-8 h-8" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">
                Compliance Monitoring
              </h3>
              <p className="text-gray-300">
                Real-time monitoring of regulatory changes and automated compliance reporting.
              </p>
            </div>

            <div className="text-center p-6 bg-slate-800 rounded-lg border border-slate-700 shadow-2xl transform hover:-translate-y-2 hover:scale-105 transition-all duration-300 ease-in-out">
              <div className="bg-purple-900/60 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 border border-purple-700/30 shadow-inner">
                <Brain className="text-purple-300 w-8 h-8" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">
                AI-Powered Insights
              </h3>
              <p className="text-gray-300">
                Proactive risk identification and mitigation strategies with detailed analytics.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="py-24 bg-gradient-to-r from-blue-900 to-blue-950">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Ready to Transform Your Compliance Process?
          </h2>
          <p className="text-lg text-blue-100 mb-8 max-w-2xl mx-auto">
            Join thousands of companies already using LegalGuard to streamline their legal compliance.
          </p>
          <Link to="/signup" className="bg-blue-300 text-slate-900 px-8 py-4 rounded-lg text-lg font-semibold hover:bg-blue-200 transition-colors inline-flex items-center shadow-lg transform hover:-translate-y-1">
            Get Started Today
            <ArrowRight className="ml-2 w-5 h-5" />
          </Link>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12 border-t border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center mb-4">
                <div className="bg-blue-600 w-8 h-8 flex items-center justify-center rounded-lg shadow-md">
                  <FileText className="text-white w-5 h-5" />
                </div>
                <span className="ml-2 text-xl font-bold">LegalGuard</span>
              </div>
              <p className="text-gray-400">
                AI-powered legal compliance platform for modern businesses.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4 text-blue-300">Product</h3>
              <ul className="space-y-2 text-gray-400">
                <li><Link to="/compliance" className="hover:text-blue-200 transition-colors">Compliance</Link></li>
                <li><Link to="/regulations" className="hover:text-blue-200 transition-colors">Regulations</Link></li>
                <li><Link to="/signup" className="hover:text-blue-200 transition-colors">Pricing</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4 text-blue-300">Company</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-blue-200 transition-colors">About</a></li>
                <li><a href="#" className="hover:text-blue-200 transition-colors">Contact</a></li>
                <li><a href="#" className="hover:text-blue-200 transition-colors">Support</a></li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4 text-blue-300">Legal</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-blue-200 transition-colors">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-blue-200 transition-colors">Terms of Service</a></li>
                <li><a href="#" className="hover:text-blue-200 transition-colors">Cookie Policy</a></li>
              </ul>
            </div>
          </div>
          <div className="mt-10 grid gap-6 md:grid-cols-2">
            <Link
              to="/compliance"
              className="flex items-center gap-4 bg-slate-800 rounded-lg border border-slate-700 p-6 shadow-2xl hover:-translate-y-1 hover:scale-[1.01] transition-all duration-300 ease-in-out"
            >
              <div className="bg-blue-900/60 w-12 h-12 rounded-full flex items-center justify-center border border-blue-700/30 shadow-inner">
                <FileText className="text-blue-300 w-6 h-6" />
              </div>
              <div>
                <p className="text-lg font-semibold text-white">База знаний и FAQ</p>
                <p className="text-gray-400">Полезные материалы и ответы</p>
              </div>
            </Link>
            <a
              href="https://t.me/BioPeptideResearch"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-4 bg-slate-800 rounded-lg border border-slate-700 p-6 shadow-2xl hover:-translate-y-1 hover:scale-[1.01] transition-all duration-300 ease-in-out"
            >
              <div className="bg-teal-900/40 w-12 h-12 rounded-full flex items-center justify-center border border-teal-700/30 shadow-inner">
                <Send className="text-[#0ABAB5] w-6 h-6" />
              </div>
              <div>
                <p className="text-lg font-semibold text-white">Перейти в канал</p>
                <p className="text-gray-400">Telegram-сообщество</p>
              </div>
            </a>
          </div>
          <div className="border-t border-slate-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 LegalGuard. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
