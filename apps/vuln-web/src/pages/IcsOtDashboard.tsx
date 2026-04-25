import React, { useState, useEffect } from 'react';
import { 
  Settings, 
  Cpu, 
  Activity, 
  Terminal, 
  ShieldAlert,
  Box,
  Binary,
  Lock,
  Info
} from 'lucide-react';
import { VulnerabilityModal } from '../components/VulnerabilityModal';
import { HintChip } from '../components/HintChip';
import { useApi } from '../hooks/useApi';
import { useVulnerabilityInfo } from '../hooks/useVulnerabilityInfo';

export const IcsOtDashboard: React.FC = () => {
  const { loading, request } = useApi();
  const { info: icsInfo } = useVulnerabilityInfo('ics_ot');
  const [systems, setSystems] = useState<any[]>([]);
  const [controllers, setControllers] = useState<any[]>([]);
  const [showInfo, setShowInfo] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      const sysData = await request('/api/ics/scada/systems');
      if (sysData) setSystems(sysData.scada_systems || []);
      
      const ctrlData = await request('/api/ics/controllers/status');
      if (ctrlData) setControllers(ctrlData.controllers || []);
    };
    fetchData();
  }, [request]);

  return (
    <div className="container mx-auto px-4 py-8">
      <VulnerabilityModal
          isOpen={showInfo}
          onClose={() => setShowInfo(false)}
          info={icsInfo}
        />
      
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold text-slate-900 flex items-center gap-3 underline decoration-blue-500/30">
              <Cpu className="w-8 h-8 text-blue-600" />
              Industrial Command Center
            </h1>
            <button 
              onClick={() => setShowInfo(true)}
              className="p-1.5 text-blue-600 bg-blue-50 rounded-full hover:bg-blue-100 transition-colors"
              aria-label="View Vulnerability Info"
            >
              <Info className="w-5 h-5" />
            </button>
          </div>
          <p className="text-slate-500 font-mono text-sm tracking-tight mt-1">OT/ICS Operational Intelligence Interface</p>
        </div>
        <div className="flex gap-3">
          <button id="ics-cli-btn" className="flex items-center gap-2 px-4 py-2 bg-slate-900 text-white rounded shadow-sm text-sm font-bold hover:bg-slate-800 transition-all">
            <Terminal className="w-4 h-4" />
            Modbus CLI
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded shadow-sm text-sm font-bold hover:bg-blue-700 transition-all">
            <ShieldAlert className="w-4 h-4" />
            Security Override
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-8">
          {/* Main SCADA Inventory */}
          <div className="bg-white rounded-xl overflow-hidden shadow-sm border border-slate-200">
            <div className="p-4 border-b border-slate-100 bg-slate-50 flex items-center justify-between">
              <h2 className="font-bold text-slate-700 flex items-center gap-2 text-xs uppercase tracking-widest">
                <Box className="w-4 h-4 text-blue-500" />
                System Inventory
              </h2>
              <span className="text-[10px] font-bold text-slate-400">Total Nodes: {systems.length}</span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-slate-50 text-slate-500 uppercase text-[10px] font-bold">
                  <tr>
                    <th className="p-4">System ID</th>
                    <th className="p-4">Model / Vendor</th>
                    <th className="p-4">Location</th>
                    <th className="p-4">Status</th>
                    <th className="p-4 text-right">Access</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {loading ? (
                    <tr><td colSpan={5} className="p-12 text-center text-slate-400 italic">Scanning OT network...</td></tr>
                  ) : (
                    systems.map((sys) => (
                      <tr key={sys.system_id} className="hover:bg-slate-50 transition-colors">
                        <td className="p-4 font-mono text-xs font-bold text-slate-900">{sys.system_id}</td>
                        <td className="p-4">
                          <div className="font-medium text-slate-900">{sys.model}</div>
                          <div className="text-[10px] text-slate-500">{sys.vendor}</div>
                        </td>
                        <td className="p-4 text-slate-600">{sys.location}</td>
                        <td className="p-4">
                          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700 text-[10px] font-bold">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                            {sys.status}
                          </span>
                        </td>
                        <td className="p-4 text-right">
                          <button className="text-blue-600 font-bold text-xs hover:underline">Launch HMI</button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Controllers Table */}
          <div className="bg-slate-900 rounded-xl overflow-hidden shadow-2xl border border-slate-800 relative">
            <div className="absolute top-4 right-4">
               <HintChip label="BOLA" onClick={() => setShowInfo(true)} />
            </div>
            <div className="p-4 border-b border-slate-800 flex items-center justify-between">
              <h2 className="font-bold text-slate-200 flex items-center gap-2 font-mono text-xs uppercase tracking-widest">
                <Settings className="w-4 h-4 text-blue-400" />
                PLC Status Matrix
              </h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-slate-800/50 text-slate-500">
                  <tr>
                    <th className="p-4">PLC ID</th>
                    <th className="p-4">CPU %</th>
                    <th className="p-4">Memory</th>
                    <th className="p-4">Active Loops</th>
                    <th className="p-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {controllers.map((ctrl) => (
                    <tr key={ctrl.controller_id} className="text-slate-300 hover:bg-blue-500/5 transition-colors">
                      <td className="p-4 font-bold text-blue-400">{ctrl.controller_id}</td>
                      <td className="p-4">
                        <div className="flex items-center gap-2">
                          <div className="w-12 bg-slate-800 h-1 rounded-full overflow-hidden">
                            <div className="bg-blue-500 h-full" style={{ width: `${ctrl.cpu_usage}%` }} />
                          </div>
                          {ctrl.cpu_usage.toFixed(1)}%
                        </div>
                      </td>
                      <td className="p-4">
                        <div className="flex items-center gap-2">
                          <div className="w-12 bg-slate-800 h-1 rounded-full overflow-hidden">
                            <div className="bg-emerald-500 h-full" style={{ width: `${ctrl.memory_usage}%` }} />
                          </div>
                          {ctrl.memory_usage.toFixed(1)}%
                        </div>
                      </td>
                      <td className="p-4 text-slate-500">{ctrl.active_loops}</td>
                      <td className="p-4 text-right">
                        <button className="text-[10px] bg-slate-800 px-2 py-1 rounded border border-slate-700 hover:bg-slate-700">Debug</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div className="space-y-8">
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <h2 className="font-bold text-slate-900 mb-4 flex items-center gap-2 text-xs uppercase tracking-widest">
              <Activity className="w-4 h-4 text-red-500" />
              Safety Systems
            </h2>
            <div className="space-y-4">
              <div className="p-4 bg-emerald-50 border border-emerald-100 rounded-lg">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-xs font-bold text-emerald-800 uppercase">Emergency Shutdown</span>
                  <span className="text-[10px] font-bold text-emerald-600">ARMED</span>
                </div>
                <p className="text-[10px] text-emerald-700">Safety Instrumented System (SIS) is operational.</p>
              </div>
              <button className="w-full py-2 bg-red-50 text-red-600 border border-red-100 rounded-lg text-xs font-bold hover:bg-red-100 transition-all">
                Manual SIS Bypass
              </button>
            </div>
          </div>

          <div className="bg-slate-50 p-6 rounded-xl border border-slate-200 border-dashed relative">
            <div className="absolute top-4 right-4">
               <HintChip label="RCE" onClick={() => setShowInfo(true)} />
            </div>
            <h2 className="font-bold text-slate-900 mb-4 flex items-center gap-2 font-mono text-xs uppercase tracking-widest">
              <Binary className="w-4 h-4 text-slate-500" />
              Register Manipulator
            </h2>
            <div className="space-y-3">
              <input type="text" placeholder="Register Address (e.g. 40001)" className="w-full p-2 bg-white border border-slate-200 rounded text-xs font-mono" />
              <input type="number" placeholder="Value" className="w-full p-2 bg-white border border-slate-200 rounded text-xs font-mono" />
              <button className="w-full py-2 bg-slate-900 text-white rounded font-bold text-xs hover:bg-slate-800 transition-all">
                Write Register
              </button>
            </div>
          </div>

          <div className="p-6 bg-blue-600 rounded-xl text-white shadow-lg">
            <h2 className="font-bold mb-2 flex items-center gap-2">
              <Lock className="w-4 h-4" />
              Isolation Status
            </h2>
            <p className="text-xs text-blue-100 mb-4 leading-relaxed">
              Network segment is currently bridged to the corporate IT domain for maintenance.
            </p>
            <div className="w-full bg-blue-700 h-2 rounded-full overflow-hidden">
              <div className="bg-white h-full w-3/4" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
