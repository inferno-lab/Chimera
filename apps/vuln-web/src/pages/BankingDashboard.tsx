import React, { useState, useEffect, useCallback } from 'react';
import {
  Landmark,
  CreditCard,
  ArrowRightLeft,
  DollarSign,
  Shield,
  TrendingUp,
  History,
  Send,
  Info
} from 'lucide-react';
import { VulnerabilityModal } from '../components/VulnerabilityModal';
import { HintChip } from '../components/HintChip';
import { useApi } from '../hooks/useApi';
import { useVulnerabilityInfo } from '../hooks/useVulnerabilityInfo';

export const BankingDashboard: React.FC = () => {
  const [accounts, setAccounts] = useState<any[]>([]);
  const [transferStatus, setTransferStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [showInfo, setShowInfo] = useState(false);
  
  // Separate API instances to isolate loading states
  const accountsApi = useApi();
  const transferApi = useApi();
  
  // Fetch vulnerability documentation from VaaS API
  const { info: bankingInfo } = useVulnerabilityInfo('banking');

  /**
   * Fetches the current user's accounts.
   * Stability: accountsApi.request is memoized in useApi hook.
   */
  const fetchAccounts = useCallback(async () => {
    const data = await accountsApi.request('/api/v1/banking/accounts');
    if (data && !data.error) {
      setAccounts(data.accounts || []);
    }
  }, [accountsApi.request]);

  useEffect(() => {
    fetchAccounts();
  }, [fetchAccounts]);

  const handleTransfer = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = e.currentTarget;
    const formData = new FormData(form);
    const amountStr = formData.get('amount') as string;
    const to = formData.get('to');

    // Basic client-side guard (educationally vulnerable, but prevents zero-dollar spam)
    if (!amountStr || Number(amountStr) <= 0) return;

    setTransferStatus('idle');
    
    // Backend uses 'account_id', not 'id'. Using demo ID as default.
    const fromAccount = accounts[0]?.account_id || 'ACC-user-demo-001';

    try {
      const data = await transferApi.request('/api/v1/banking/transfer', { 
        from_account: fromAccount,
        to_account: to, 
        amount: Number(amountStr) 
      });

      // Check for truthy data AND lack of error payload (API contract)
      if (data && !data.error) {
        setTransferStatus('success');
        form.reset();
        fetchAccounts();
      } else {
        setTransferStatus('error');
      }
    } catch (err) {
      console.error('Transfer exception:', err);
      setTransferStatus('error');
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <VulnerabilityModal isOpen={showInfo} onClose={() => setShowInfo(false)} info={bankingInfo} />
      
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-8">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold text-slate-900 flex items-center gap-2">
              <Landmark className="w-8 h-8 text-blue-600" />
              SecureBank Pro
            </h1>
            <button 
              onClick={() => setShowInfo(true)}
              className="p-1.5 text-blue-600 bg-blue-50 rounded-full hover:bg-blue-100 transition-colors"
              aria-label="View Vulnerability Info"
            >
              <Info className="w-5 h-5" />
            </button>
          </div>
          <p className="text-slate-500">Corporate Banking & Treasury Management</p>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="px-4 py-2 bg-emerald-50 text-emerald-700 rounded-lg text-sm font-bold border border-emerald-100 flex items-center gap-2">
            <Shield className="w-4 h-4" />
            FDIC Insured
          </div>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-bold hover:bg-blue-700 transition-all shadow-md shadow-blue-200">
            Download Statements
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Accounts */}
        <div className="lg:col-span-8 space-y-8">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="p-6 border-b border-slate-100 bg-slate-50/50 flex justify-between items-center">
              <h2 className="font-bold text-slate-900 flex items-center gap-2">
                <CreditCard className="w-5 h-5 text-blue-500" />
                Your Accounts
              </h2>
              <HintChip label="BOLA / IDOR" onClick={() => setShowInfo(true)} />
            </div>
            
            <div className="divide-y divide-slate-100">
              {accountsApi.loading && accounts.length === 0 ? (
                <div className="p-12 text-center text-slate-400 italic">Accessing secure vault...</div>
              ) : (
                accounts.map((acc) => (
                  <div key={acc.account_id} className="p-6 flex items-center justify-between hover:bg-slate-50 transition-colors">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center text-blue-600">
                        <DollarSign className="w-6 h-6" />
                      </div>
                      <div>
                        <p className="font-bold text-slate-900">{acc.account_id}</p>
                        <p className="text-xs text-slate-500 uppercase tracking-wider">{acc.account_type}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-xl font-bold text-slate-900">${(acc.balance ?? 0).toLocaleString()}</p>
                      <p className="text-[10px] text-emerald-600 font-bold">AVAILABLE</p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
              <h3 className="font-bold text-slate-900 mb-4 flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-emerald-500" />
                Market Overview
              </h3>
              <div className="space-y-4">
                {[
                  { label: 'S&P 500', value: '+1.2%', color: 'text-emerald-600' },
                  { label: 'Dow Jones', value: '+0.8%', color: 'text-emerald-600' },
                  { label: 'NASDAQ', value: '-0.3%', color: 'text-rose-600' },
                ].map((m, i) => (
                  <div key={i} className="flex justify-between items-center text-sm">
                    <span className="text-slate-500">{m.label}</span>
                    <span className={`font-bold ${m.color}`}>{m.value}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="bg-slate-900 p-6 rounded-2xl text-white shadow-xl">
              <h3 className="font-bold mb-4 flex items-center gap-2 text-blue-400">
                <Shield className="w-4 h-4" />
                Security Status
              </h3>
              <div className="space-y-3 text-xs">
                <div className="flex justify-between">
                  <span className="text-slate-400">2FA Status</span>
                  <span className="text-emerald-400 font-bold tracking-widest uppercase">Active</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Last Login</span>
                  <span>Today, 09:42 AM</span>
                </div>
                <div className="w-full bg-slate-800 h-1 rounded-full mt-4 overflow-hidden">
                  <div className="bg-blue-500 h-full w-full" />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Actions */}
        <div className="lg:col-span-4 space-y-8">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="p-6 border-b border-slate-100 bg-slate-50/50 flex justify-between items-center">
              <h2 className="font-bold text-slate-900 flex items-center gap-2">
                <ArrowRightLeft className="w-5 h-5 text-blue-500" />
                Quick Transfer
              </h2>
              <HintChip label="Logic Manipulation" onClick={() => setShowInfo(true)} />
            </div>
            <form onSubmit={handleTransfer} className="p-6 space-y-4">
              <div>
                <label htmlFor="transfer-to" className="block text-xs font-bold text-slate-500 uppercase mb-1">To Account</label>
                <input 
                  id="transfer-to"
                  name="to"
                  type="text" 
                  placeholder="Account Number (e.g. ACC-002)" 
                  className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-all"
                  required
                />
              </div>
              <div>
                <label htmlFor="transfer-amount" className="block text-xs font-bold text-slate-500 uppercase mb-1">Amount ($)</label>
                <input 
                  id="transfer-amount"
                  name="amount"
                  type="number" 
                  placeholder="0.00" 
                  className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-all"
                  required
                />
              </div>
              <button 
                type="submit"
                disabled={transferApi.loading}
                className="w-full py-3 bg-blue-600 text-white rounded-xl font-bold hover:bg-blue-700 transition-all shadow-lg shadow-blue-200 flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {transferApi.loading ? 'Processing...' : (
                  <>
                    <Send className="w-4 h-4" />
                    Complete Transfer
                  </>
                )}
              </button>
              
              <div aria-live="polite" className="mt-2">
                {transferStatus === 'success' && (
                  <div role="status" className="p-3 bg-emerald-50 text-emerald-700 rounded-xl text-xs font-bold text-center animate-in zoom-in-95 duration-300">
                    Transfer successfully authorized!
                  </div>
                )}
                {transferStatus === 'error' && (
                  <div role="alert" className="p-3 bg-rose-50 text-rose-700 rounded-xl text-xs font-bold text-center animate-in zoom-in-95 duration-300">
                    Transaction failed. Please contact your branch.
                  </div>
                )}
              </div>
            </form>
          </div>

          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
            <h2 className="font-bold text-slate-900 mb-4 flex items-center gap-2">
              <History className="w-5 h-5 text-slate-400" />
              Recent Activity
            </h2>
            <div className="space-y-4">
              {[
                { label: 'Payment to shop.com', value: '-$124.50', date: 'Yesterday' },
                { label: 'Direct Deposit', value: '+$3,200.00', date: '2 days ago' },
                { label: 'ATM Withdrawal', value: '-$40.00', date: '3 days ago' },
              ].map((act, i) => (
                <div key={i} className="flex justify-between items-start border-b border-slate-50 pb-3 last:border-0">
                  <div>
                    <p className="text-sm font-bold text-slate-800">{act.label}</p>
                    <p className="text-[10px] text-slate-400 uppercase tracking-wider">{act.date}</p>
                  </div>
                  <span className="text-sm font-mono font-bold text-slate-900">{act.value}</span>
                </div>
              ))}
            </div>
            <button className="w-full mt-4 py-2 text-xs font-bold text-blue-600 hover:underline">View Transaction History</button>
          </div>
        </div>
      </div>
    </div>
  );
};
