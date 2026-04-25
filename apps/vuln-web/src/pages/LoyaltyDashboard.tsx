import React, { useState, useEffect } from 'react';
import { 
  Trophy,
  Star,
  ArrowRightLeft,
  Clock,
  QrCode,
  Tag,
  Info
} from 'lucide-react';
import { VulnerabilityModal } from '../components/VulnerabilityModal';
import { HintChip } from '../components/HintChip';
import { useApi } from '../hooks/useApi';
import { useVulnerabilityInfo } from '../hooks/useVulnerabilityInfo';

export const LoyaltyDashboard: React.FC = () => {
  const { request } = useApi();
  const { info: loyaltyInfo } = useVulnerabilityInfo('loyalty');
  const [transferAmount, setTransferAmount] = useState('');
  const [showInfo, setShowInfo] = useState(false);
  const [points, setPoints] = useState(0);

  useEffect(() => {
    const fetchLoyaltyDetails = async () => {
      const data = await request(`/api/loyalty/program/details`);
      if (data) {
        // Just for demo, we'll use the enrollment bonus as the current balance
        setPoints(data.enrollment_bonus || 1000);
      }
    };
    fetchLoyaltyDetails();
  }, [request]);

  return (
    <div className="container mx-auto px-4 py-8">
      <VulnerabilityModal
          isOpen={showInfo}
          onClose={() => setShowInfo(false)}
          info={loyaltyInfo}
        />
      
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold text-slate-900 flex items-center gap-3">
              <Trophy className="w-8 h-8 text-indigo-600" />
              EliteRewards
            </h1>
            <button 
              onClick={() => setShowInfo(true)}
              className="p-1.5 text-indigo-600 bg-indigo-50 rounded-full hover:bg-indigo-100 transition-colors"
              aria-label="View Vulnerability Info"
            >
              <Info className="w-5 h-5" />
            </button>
          </div>
          <p className="text-slate-500 font-medium">Premier Status • Member since 2022</p>
        </div>
        <div className="flex gap-3">
          <button className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-bold hover:bg-indigo-700 transition-all shadow-md shadow-indigo-200">
            <QrCode className="w-4 h-4" />
            My Member Card
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-8">
          {/* Points Summary */}
          <div className="bg-gradient-to-br from-indigo-600 to-violet-700 rounded-3xl p-8 text-white shadow-xl relative overflow-hidden">
            <Star className="absolute -right-4 -top-4 w-32 h-32 text-white/10 rotate-12" />
            <div className="relative z-10">
              <p className="text-indigo-100 font-medium uppercase tracking-wider text-xs mb-2">Available Balance</p>
              <div className="flex items-baseline gap-2 mb-8">
                <span className="text-5xl font-extrabold tracking-tight">{points.toLocaleString()}</span>
                <span className="text-indigo-200 font-bold">PTS</span>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-white/10 backdrop-blur-md rounded-2xl p-4 border border-white/10">
                  <p className="text-indigo-100 text-[10px] font-bold uppercase mb-1">Lifetime Earned</p>
                  <p className="text-xl font-bold">85,400</p>
                </div>
                <div className="bg-white/10 backdrop-blur-md rounded-2xl p-4 border border-white/10">
                  <p className="text-indigo-100 text-[10px] font-bold uppercase mb-1">Est. Value</p>
                  <p className="text-xl font-bold">${(points * 0.01).toFixed(2)}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Transfers */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="p-6 border-b border-slate-100 bg-slate-50/50 flex justify-between items-center">
              <h2 className="font-bold text-slate-900 flex items-center gap-2">
                <ArrowRightLeft className="w-5 h-5 text-indigo-500" />
                Peer-to-Peer Transfer
              </h2>
              <HintChip label="Logic Manipulation" onClick={() => setShowInfo(true)} />
            </div>
            <div className="p-6">
              <p className="text-sm text-slate-500 mb-6 leading-relaxed">
                Instantly transfer points to another EliteRewards member. Transfers are final once processed.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="md:col-span-1">
                  <label className="block text-[10px] font-bold text-slate-400 uppercase mb-1">Recipient ID</label>
                  <input type="text" placeholder="Member ID" className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg text-sm" />
                </div>
                <div className="md:col-span-1">
                  <label className="block text-[10px] font-bold text-slate-400 uppercase mb-1">Amount</label>
                  <input 
                    id="loyalty-transfer-input"
                    type="number" 
                    placeholder="0" 
                    className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg text-sm"
                    value={transferAmount}
                    onChange={(e) => setTransferAmount(e.target.value)}
                  />
                </div>
                <div className="md:col-span-1 flex items-end">
                  <button className="w-full py-2 bg-indigo-600 text-white rounded-lg text-sm font-bold hover:bg-indigo-700 transition-all">
                    Send Points
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Recent History */}
        <div className="space-y-8">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden relative">
            <div className="p-4 border-b border-slate-100 bg-slate-50/50 flex justify-between items-center">
              <h2 className="font-bold text-slate-900 flex items-center gap-2 text-sm uppercase tracking-widest">
                <Clock className="w-4 h-4 text-indigo-500" />
                Recent Activity
              </h2>
              <HintChip label="BOLA" onClick={() => setShowInfo(true)} />
            </div>
            <div className="divide-y divide-slate-100">
              {[
                { label: 'Starbucks Coffee', date: 'Yesterday', pts: '+50', type: 'earn' },
                { label: 'Points Transfer', date: 'Dec 05', pts: '-1,200', type: 'spend' },
                { label: 'Monthly Bonus', date: 'Dec 01', pts: '+500', type: 'earn' },
                { label: 'Amazon Purchase', date: 'Nov 28', pts: '+210', type: 'earn' },
              ].map((item, i) => (
                <div key={i} className="p-4 flex items-center justify-between hover:bg-slate-50 transition-colors">
                  <div>
                    <p className="text-xs font-bold text-slate-900">{item.label}</p>
                    <p className="text-[10px] text-slate-400">{item.date}</p>
                  </div>
                  <span className={`text-xs font-bold ${item.type === 'earn' ? 'text-emerald-600' : 'text-slate-900'}`}>
                    {item.pts}
                  </span>
                </div>
              ))}
            </div>
            <div className="p-4 bg-slate-50 border-t border-slate-100">
              <button className="w-full py-2 border border-slate-200 rounded-lg text-[10px] font-bold text-slate-500 uppercase hover:bg-white transition-all">
                Export Full Statement
              </button>
            </div>
          </div>

          <div className="bg-indigo-50 rounded-2xl p-6 border border-indigo-100">
            <h2 className="font-bold text-indigo-900 mb-4 flex items-center gap-2 text-xs uppercase tracking-widest">
              <Tag className="w-4 h-4 text-indigo-500" />
              Special Offers
            </h2>
            <div className="space-y-3">
              <div className="bg-white p-3 rounded-xl border border-indigo-100 shadow-sm">
                <p className="text-[10px] font-bold text-indigo-600 uppercase mb-1">Double Points</p>
                <p className="text-xs font-bold text-slate-900">Holiday Shopping Event</p>
              </div>
              <div className="bg-white p-3 rounded-xl border border-indigo-100 shadow-sm opacity-60">
                <p className="text-[10px] font-bold text-slate-400 uppercase mb-1">Expired</p>
                <p className="text-xs font-bold text-slate-900">Refer a Friend Bonus</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
