import { Link } from 'react-router-dom';
import { ArrowRight, BarChart3, Bot, Shield, Sparkles, TrendingUp, Upload } from 'lucide-react';
import { Button } from '../components/ui/Button';

export function Landing() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-primary-50 dark:from-gray-900 dark:via-gray-900 dark:to-primary-950">
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-4 py-6 lg:px-8">
        <div className="flex items-center gap-2">
          <Sparkles className="h-8 w-8 text-primary-600" />
          <span className="text-xl font-bold text-gray-900 dark:text-white">DataInsight AI</span>
        </div>
        <div className="flex gap-3">
          <Link to="/login">
            <Button variant="ghost">Sign In</Button>
          </Link>
          <Link to="/register">
            <Button>Get Started</Button>
          </Link>
        </div>
      </nav>

      <section className="mx-auto max-w-7xl px-4 py-20 text-center lg:px-8 lg:py-32">
        <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl dark:text-white">
          AI-Powered Data Analysis
          <span className="block text-primary-600">Made Simple</span>
        </h1>
        <p className="mx-auto mt-6 max-w-2xl text-lg text-gray-600 dark:text-gray-400">
          Upload datasets, get automatic insights, create stunning visualizations, run ML predictions,
          and export professional reports — all in one platform.
        </p>
        <div className="mt-10 flex flex-wrap justify-center gap-4">
          <Link to="/register">
            <Button size="lg">
              Start Free <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </Link>
          <Link to="/login">
            <Button size="lg" variant="secondary">
              View Demo
            </Button>
          </Link>
        </div>
      </section>

      <section className="mx-auto grid max-w-7xl gap-6 px-4 pb-20 sm:grid-cols-2 lg:grid-cols-4 lg:px-8">
        {[
          { icon: Upload, title: 'Smart Upload', desc: 'CSV, Excel, JSON with validation' },
          { icon: BarChart3, title: 'Visualizations', desc: 'Interactive charts with Plotly' },
          { icon: Bot, title: 'AI Assistant', desc: 'Ask questions in plain English' },
          { icon: TrendingUp, title: 'Predictions', desc: 'Regression & classification ML' },
        ].map(({ icon: Icon, title, desc }) => (
          <div
            key={title}
            className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm transition hover:shadow-md dark:border-gray-700 dark:bg-gray-800"
          >
            <Icon className="h-10 w-10 text-primary-600" />
            <h3 className="mt-4 font-semibold text-gray-900 dark:text-white">{title}</h3>
            <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">{desc}</p>
          </div>
        ))}
      </section>

      <footer className="border-t border-gray-200 py-8 text-center text-sm text-gray-500 dark:border-gray-700">
        <Shield className="mx-auto mb-2 h-5 w-5" />
        Enterprise-grade security with JWT authentication
      </footer>
    </div>
  );
}
