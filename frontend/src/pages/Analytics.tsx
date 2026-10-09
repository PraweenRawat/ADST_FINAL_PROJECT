import { useEffect, useState } from 'react';
import api from '../api';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';
import { AlertCircle } from 'lucide-react';

export default function Analytics() {
  const [hourly, setHourly] = useState([]);
  const [location, setLocation] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    Promise.all([
      api.get('/analytics/hourly'),
      api.get('/analytics/location')
    ])
    .then(([hourRes, locRes]) => {
      setHourly(hourRes.data);
      setLocation(locRes.data.slice(0, 10)); // Top 10
      setLoading(false);
    })
    .catch(err => {
      setError(err.message || 'Failed to load analytics');
      setLoading(false);
    });
  }, []);

  if (loading) return <div className="text-gray-500 py-20 text-center">Loading charts...</div>;
  if (error) return <div className="text-red-500 p-4 flex gap-2"><AlertCircle/>{error}</div>;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Peak Analytics</h1>
        <p className="text-gray-500 mt-2">Data-driven analysis from the actual historical dataset.</p>
      </div>

      {/* Hourly Chart */}
      <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
        <h2 className="text-xl font-bold mb-6 text-gray-800">Total Demand by Hour of Day (kWh)</h2>
        <div className="h-[400px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={hourly} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#eee" />
              <XAxis dataKey="hour" tickFormatter={(v) => `${v}:00`} stroke="#888" />
              <YAxis stroke="#888" />
              <Tooltip 
                formatter={(value: any) => [`${Number(value).toLocaleString()} kWh`, 'Total Demand']}
                labelFormatter={(label) => `${label}:00`}
              />
              <Bar dataKey="total_demand_kwh" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Location Chart */}
      <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
        <h2 className="text-xl font-bold mb-6 text-gray-800">Top 10 Locations by Total Demand</h2>
        <div className="h-[400px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart layout="vertical" data={location} margin={{ top: 5, right: 30, left: 80, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#eee" />
              <XAxis type="number" stroke="#888" />
              <YAxis dataKey="Location" type="category" stroke="#888" tick={{fontSize: 12}} width={120} />
              <Tooltip formatter={(value: any) => [`${Number(value).toLocaleString()} kWh`, 'Total Demand']} />
              <Bar dataKey="total_demand_kwh" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
