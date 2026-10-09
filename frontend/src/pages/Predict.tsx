import { useEffect, useState } from 'react';
import api from '../api';
import { Activity, AlertCircle } from 'lucide-react';

export default function Predict() {
  const [prediction, setPrediction] = useState<number | null>(null);
  const [modelPerf, setModelPerf] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [formData, setFormData] = useState({
    hour: 18,
    day_of_week: 6,
    month: 8,
    is_weekend: 1,
    ChargerType: 1,
    ChargerCompany: 1,
    Location: 'public area'
  });

  const LOCATIONS = [
    'apartment', 'public area', 'resort', 'hotel', 'company', 
    'public institution', 'public parking lot', 'market', 'camping', 
    'restaurant', 'sightseeing', 'golf', 'accommodation', 'bus garage'
  ];

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const [predRes, perfRes] = await Promise.all([
        api.post('/predict', {
          hour: Number(formData.hour),
          day_of_week: Number(formData.day_of_week),
          month: Number(formData.month),
          is_weekend: Number(formData.is_weekend),
          ChargerType: Number(formData.ChargerType),
          ChargerCompany: Number(formData.ChargerCompany),
          Location: formData.Location
        }),
        api.get('/model-performance')
      ]);
      
      setPrediction(predRes.data.predicted_kwh);
      setModelPerf(perfRes.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Prediction failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Predict Demand</h1>
        <p className="text-gray-500 mt-2">Enter charging session properties to predict energy consumption.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column - Predictor Form */}
        <div className="lg:col-span-2 space-y-8">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <form onSubmit={handlePredict} className="grid grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Hour of Day (0-23)</label>
                <input type="number" min="0" max="23" 
                  className="w-full p-2.5 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  value={formData.hour} onChange={e => setFormData({...formData, hour: e.target.value as any})} required />
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Day of Week (0=Mon, 6=Sun)</label>
                <input type="number" min="0" max="6" 
                  className="w-full p-2.5 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  value={formData.day_of_week} onChange={e => setFormData({...formData, day_of_week: e.target.value as any})} required />
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Month (1-12)</label>
                <input type="number" min="1" max="12" 
                  className="w-full p-2.5 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  value={formData.month} onChange={e => setFormData({...formData, month: e.target.value as any})} required />
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Is Weekend?</label>
                <select className="w-full p-2.5 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  value={formData.is_weekend} onChange={e => setFormData({...formData, is_weekend: e.target.value as any})}>
                  <option value={0}>No (0)</option>
                  <option value={1}>Yes (1)</option>
                </select>
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Charger Type</label>
                <select className="w-full p-2.5 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  value={formData.ChargerType} onChange={e => setFormData({...formData, ChargerType: e.target.value as any})}>
                  <option value={0}>Slow/AC (0)</option>
                  <option value={1}>Fast/DC (1)</option>
                </select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Charger Company</label>
                <select className="w-full p-2.5 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  value={formData.ChargerCompany} onChange={e => setFormData({...formData, ChargerCompany: e.target.value as any})}>
                  <option value={0}>Company 0</option>
                  <option value={1}>Company 1</option>
                </select>
              </div>

              <div className="col-span-2 space-y-2">
                <label className="text-sm font-medium text-gray-700">Location Category</label>
                <select className="w-full p-2.5 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  value={formData.Location} onChange={e => setFormData({...formData, Location: e.target.value})}>
                  {LOCATIONS.map(loc => <option key={loc} value={loc}>{loc}</option>)}
                </select>
              </div>

              <div className="col-span-2 mt-4">
                <button type="submit" disabled={loading}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-xl shadow transition disabled:opacity-50 disabled:cursor-not-allowed">
                  {loading ? 'Processing...' : 'Predict Energy Demand'}
                </button>
              </div>
              
              {error && (
                <div className="col-span-2 text-red-600 bg-red-50 p-3 rounded-lg border border-red-200 flex items-center gap-2">
                  <AlertCircle size={20}/> {error}
                </div>
              )}
            </form>
          </div>
        </div>

        {/* Right Column - Results Display */}
        <div className="space-y-6">
          <div className={`p-8 rounded-xl border ${prediction !== null ? 'bg-blue-50 border-blue-200' : 'bg-white border-gray-100 shadow-sm'}`}>
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">Prediction Result</h3>
            
            {prediction !== null ? (
              <div className="space-y-6">
                <div>
                  <div className="text-gray-700 font-medium mb-1">Predicted Energy Demand:</div>
                  <div className="text-3xl font-extrabold text-blue-900">
                    {prediction.toFixed(2)} <span className="text-xl text-blue-700 font-normal">kWh/session</span>
                  </div>
                </div>
                
                {modelPerf?.test && (
                  <div className="space-y-3 text-base text-gray-700 border-t border-blue-200 pt-6">
                    <div className="flex justify-between items-center bg-white p-2 rounded border border-blue-100">
                      <span className="font-medium">Model:</span>
                      <span className="font-bold text-gray-900">Random Forest</span>
                    </div>
                    <div className="flex justify-between items-center bg-white p-2 rounded border border-blue-100">
                      <span className="font-medium">Test MAE:</span>
                      <span className="font-bold text-gray-900">{modelPerf.test.MAE.toFixed(2)} kWh</span>
                    </div>
                    <div className="flex justify-between items-center bg-white p-2 rounded border border-blue-100">
                      <span className="font-medium">Test R²:</span>
                      <span className="font-bold text-gray-900">{modelPerf.test.R2.toFixed(3)}</span>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-gray-400 py-12 flex flex-col items-center justify-center border-2 border-dashed border-gray-200 rounded-lg">
                <Activity size={32} className="mb-2 opacity-50" />
                <p>Submit form to view prediction</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
