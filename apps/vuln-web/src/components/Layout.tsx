import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Shield, Menu, User, Sun, Moon, PlayCircle, ArrowLeft, HelpCircle, Scan } from 'lucide-react';
import { AiAssistant } from './AiAssistant';
import { RedTeamConsole } from './RedTeamConsole';
import { XRayInspector } from './XRayInspector';
import { WafVisualizer } from './WafVisualizer';
import { KillChainTracker } from './KillChainTracker';
import { useTheme } from './ThemeProvider';
import { useSettings } from './SettingsProvider';
import { TourGuide } from './TourGuide';

const PORTAL_MAP: Record<string, { name: string, color: string }> = {
  '/healthcare': { name: 'MediPortal Online', color: 'bg-emerald-600' },
  '/banking': { name: 'SecureBank Pro', color: 'bg-blue-600' },
  '/ecommerce': { name: 'ShopRight Retail', color: 'bg-orange-500' },
  '/saas': { name: 'Nexus SaaS', color: 'bg-indigo-600' },
  '/government': { name: 'GovPortal Services', color: 'bg-slate-600' },
  '/telecom': { name: 'TelcoConnect', color: 'bg-purple-600' },
  '/energy': { name: 'GridMatrix Utilities', color: 'bg-yellow-600' },
  '/ics-ot': { name: 'Industrial Command', color: 'bg-blue-900' },
  '/insurance': { name: 'ProtectFlow Insurance', color: 'bg-blue-700' },
  '/loyalty': { name: 'EliteRewards', color: 'bg-violet-600' },
  '/admin': { name: 'Core Admin Console', color: 'bg-red-600' },
  '/ai-lab': { name: 'AI Research Lab', color: 'bg-fuchsia-600' },
};

export const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const location = useLocation();
  const isHome = location.pathname === '/';
  const { theme, toggleTheme } = useTheme();
  const { showHints, toggleHints } = useSettings();

  const currentPortal = PORTAL_MAP[location.pathname] || null;

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 flex flex-col transition-colors duration-200">
      <RedTeamConsole />
      <XRayInspector />
      <WafVisualizer />
      <KillChainTracker />
      <TourGuide />
      
      <header className="bg-slate-900 dark:bg-slate-950 text-white shadow-lg sticky top-0 z-50 border-b border-slate-800 dark:border-slate-900">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link to="/" className="flex items-center gap-2 group">
              <div className={`p-1.5 rounded-lg transition-colors ${currentPortal ? currentPortal.color : 'bg-blue-600 group-hover:bg-blue-500'}`}>
                <Shield className="w-6 h-6" />
              </div>
              <span className="font-bold text-xl tracking-tight hidden lg:inline">EdgeResilience <span className="text-blue-400 font-medium text-lg italic">Portals</span></span>
            </Link>

            {!isHome && (
              <div className="flex items-center gap-3 ml-2">
                <div className="h-6 w-px bg-slate-700" />
                <Link to="/" className="flex items-center gap-1 text-xs font-bold text-slate-400 hover:text-white transition-colors uppercase tracking-widest">
                  <ArrowLeft className="w-3 h-3" />
                  Directory
                </Link>
              </div>
            )}
          </div>

          <nav className="hidden md:flex items-center gap-6">
            {currentPortal && (
              <span className="text-sm font-semibold text-blue-400 animate-in fade-in slide-in-from-left-4 duration-300">
                {currentPortal.name}
              </span>
            )}
          </nav>

            <button
              onClick={() => {
                // Dispatch event or use context? For now I'll just rely on the B key shortcut being known or add a local state if I wanted to control it from here.
                // Actually, I'll just dispatch a custom event to toggle it or use a simple window global for now since I don't want to add another context just for this.
                // Wait, I can just use a KeyboardEvent trigger.
                window.dispatchEvent(new KeyboardEvent('keydown', { ctrlKey: true, key: 'b' }));
              }}
              className="hidden lg:flex items-center gap-2 px-3 py-1.5 bg-slate-800 text-slate-400 hover:bg-blue-600 hover:text-white rounded-full text-xs font-bold transition-all"
              title="Toggle WAF Visualizer (Ctrl+B)"
              aria-label="Toggle WAF Visualizer"
            >
              <Shield className="w-3.5 h-3.5" />
              Blue Team
            </button>
            <button
              onClick={toggleHints}
              className={`hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold transition-all ${showHints ? 'bg-yellow-500 text-slate-950 ring-4 ring-yellow-500/20' : 'bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-white'}`}
              title={showHints ? 'Hide Exploit Hints' : 'Show Exploit Hints'}
              aria-pressed={showHints}
              aria-label={showHints ? 'Hide Exploit Hints' : 'Show Exploit Hints'}
            >
              <HelpCircle className="w-3.5 h-3.5" />
              {showHints ? 'Hints: ON' : 'Hints: OFF'}
            </button>
            <button
              onClick={() => (window as any).startTour && (window as any).startTour()}
              className="hidden md:flex items-center gap-2 px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-full text-xs font-bold transition-colors animate-pulse"
              aria-label="Start Exploit Tour"
            >
              <PlayCircle className="w-3.5 h-3.5" />
              Start Exploit Tour
            </button>
            <button 
              onClick={toggleTheme}
              className="p-2 text-slate-400 hover:text-white transition-colors rounded-full hover:bg-slate-800"
              title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
              aria-label={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            >
              {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
            <button className="p-2 text-slate-400 hover:text-white transition-colors" aria-label="User Profile">
              <User className="w-5 h-5" />
            </button>
            <button className="md:hidden p-2 text-slate-400 hover:text-white transition-colors" aria-label="Open Menu">
              <Menu className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      <main className="flex-grow dark:text-slate-200">
        {children}
      </main>

      <AiAssistant />

      <footer className="bg-white dark:bg-slate-950 border-t border-slate-200 dark:border-slate-800 py-8 transition-colors duration-200">
        <div className="container mx-auto px-4 flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="text-slate-500 dark:text-slate-400 text-sm">
            &copy; 2025 Edge Resilience Lab. Intentionally vulnerable for testing purposes.
          </div>
          <div className="flex gap-6 text-sm font-medium text-slate-400 dark:text-slate-500">
            <span className="hidden lg:inline text-slate-600 dark:text-slate-400 opacity-50 font-mono text-xs pt-0.5 red-team-console-hint">Console: Ctrl + ~</span>
            <a href="#" className="hover:text-slate-600 dark:hover:text-slate-300">Privacy Policy</a>
            <a href="#" className="hover:text-slate-600 dark:hover:text-slate-300">Terms of Service</a>
            <a href="#" className="hover:text-slate-600 dark:hover:text-slate-300">Security</a>
          </div>
        </div>
      </footer>
    </div>
  );
};
