import { useEffect, useState } from 'react';
import api from '../api';
import { Activity, Battery, MapPin, AlertCircle } from 'lucide-react';

export default function Dashboard() {
  const [summary, setSummary] = useState<any>(null);
  const [peak, setPeak] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    Promise.all([
      api.get('/analytics/summary'),
      api.get('/analytics/peak')
    ])
    .then(([sumRes, peakRes]) => {
      setSummary(sumRes.data);
      setPeak(peakRes.data);
      setLoading(false);
    })
    .catch(err => {
      setError(err.message || 'Failed to load dashboard data');
      setLoading(false);
    });
  }, []);

  if (loading) return <div className="flex justify-center py-20 text-gray-500">Loading dashboard...</div>;
  if (error) return <div className="p-4 bg-red-50 text-red-600 rounded-lg border border-red-200 flex gap-2 items-center"><AlertCircle size={20}/> {error}</div>;
  if (!summary || !peak) return <div className="text-gray-500 py-20 text-center">No data available.</div>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500 mt-2">Overview of the commercial EV charging dataset (Sep 2021 - Sep 2022).</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm flex flex-col justify-between">
          <div className="flex items-center gap-3 text-gray-500 mb-2">
            <Activity className="text-blue-500" /> Total Sessions
          </div>
          <div className="text-3xl font-bold">{summary.total_sessions.toLocaleString()}</div>
        </div>
        
        <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm flex flex-col justify-between">
          <div className="flex items-center gap-3 text-gray-500 mb-2">
            <Battery className="text-green-500" /> Total Energy (kWh)
          </div>
          <div className="text-3xl font-bold">{(summary.total_demand_kwh / 1000).toFixed(1)}k</div>
        </div>

        <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm flex flex-col justify-between">
          <div className="flex items-center gap-3 text-gray-500 mb-2">
            <MapPin className="text-purple-500" /> Unique Locations
          </div>
          <div className="text-3xl font-bold">{summary.unique_locations}</div>
        </div>

        <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm flex flex-col justify-between">
          <div className="flex items-center gap-3 text-gray-500 mb-2">
            <Activity className="text-orange-500" /> Avg Demand / Session
          </div>
          <div className="text-3xl font-bold">{summary.avg_demand_kwh} <span className="text-lg text-gray-500 font-normal">kWh</span></div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
          <h2 className="text-xl font-bold mb-4 border-b pb-2 text-gray-800">Peak Highlights</h2>
          <ul className="space-y-4">
            <li className="flex justify-between">
              <span className="text-gray-600">Busiest Hour (Sessions)</span>
              <span className="font-semibold">{peak.busiest_hour_by_sessions}:00 ({peak.busiest_hour_sessions_count})</span>
            </li>
            <li className="flex justify-between">
              <span className="text-gray-600">Peak Demand Hour</span>
              <span className="font-semibold">{peak.peak_hour_by_total_demand}:00</span>
            </li>
            <li className="flex justify-between">
              <span className="text-gray-600">Peak Day of Week</span>
              <span className="font-semibold">{peak.peak_day_of_week}</span>
            </li>
            <li className="flex justify-between">
              <span className="text-gray-600">Busiest Month</span>
              <span className="font-semibold">{peak.peak_month}</span>
            </li>
          </ul>
        </div>

        <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
          <h2 className="text-xl font-bold mb-4 border-b pb-2 text-gray-800">Charger Types</h2>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">Slow Chargers (AC)</span>
                <span className="font-semibold">{summary.slow_charger_sessions.toLocaleString()} sessions</span>
              </div>
              <div className="w-full bg-gray-100 rounded-full h-2">
                <div className="bg-blue-400 h-2 rounded-full" style={{ width: `${(summary.slow_charger_sessions / summary.total_sessions) * 100}%` }}></div>
              </div>
            </div>
            
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">Fast Chargers (DC)</span>
                <span className="font-semibold">{summary.fast_charger_sessions.toLocaleString()} sessions</span>
              </div>
              <div className="w-full bg-gray-100 rounded-full h-2">
                <div className="bg-orange-400 h-2 rounded-full" style={{ width: `${(summary.fast_charger_sessions / summary.total_sessions) * 100}%` }}></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
