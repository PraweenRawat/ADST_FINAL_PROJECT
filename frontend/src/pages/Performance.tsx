import { useEffect, useState } from 'react';
import api from '../api';
import { AlertCircle, CheckCircle } from 'lucide-react';

export default function Performance() {
  const [info, setInfo] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api.get('/model-info')
      .then(res => {
        setInfo(res.data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message || 'Failed to fetch model info');
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="text-gray-500 py-20 text-center">Loading model metrics...</div>;
  if (error) return <div className="text-red-500 p-4 flex gap-2"><AlertCircle/>{error}</div>;

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Model Performance</h1>
        <p className="text-gray-500 mt-2">Metrics for the active {info.model_name} pipeline.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Test Metrics */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="bg-green-50 px-6 py-4 border-b border-green-100 flex items-center gap-2">
            <CheckCircle className="text-green-600" size={20} />
            <h3 className="font-bold text-green-900">Final Test Set Metrics</h3>
          </div>
          <div className="p-6 space-y-4">
            <div className="flex justify-between border-b pb-2">
              <span className="text-gray-600">Mean Absolute Error (MAE)</span>
              <span className="font-bold text-gray-900">{info.test_metrics.MAE.toFixed(4)} kWh</span>
            </div>
            <div className="flex justify-between border-b pb-2">
              <span className="text-gray-600">Root Mean Sq Error (RMSE)</span>
              <span className="font-bold text-gray-900">{info.test_metrics.RMSE.toFixed(4)} kWh</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">R-Squared (R²)</span>
              <span className="font-bold text-gray-900">{info.test_metrics.R2.toFixed(4)}</span>
            </div>
          </div>
        </div>

        {/* Validation Metrics */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="bg-blue-50 px-6 py-4 border-b border-blue-100 flex items-center gap-2">
            <CheckCircle className="text-blue-600" size={20} />
            <h3 className="font-bold text-blue-900">Validation Set Metrics</h3>
          </div>
          <div className="p-6 space-y-4">
            <div className="flex justify-between border-b pb-2">
              <span className="text-gray-600">Mean Absolute Error (MAE)</span>
              <span className="font-bold text-gray-900">{info.validation_metrics.MAE.toFixed(4)} kWh</span>
            </div>
            <div className="flex justify-between border-b pb-2">
              <span className="text-gray-600">Root Mean Sq Error (RMSE)</span>
              <span className="font-bold text-gray-900">{info.validation_metrics.RMSE.toFixed(4)} kWh</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">R-Squared (R²)</span>
              <span className="font-bold text-gray-900">{info.validation_metrics.R2.toFixed(4)}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm space-y-6">
        <div>
          <h2 className="text-xl font-bold border-b pb-2 mb-4">Pipeline Details</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-sm text-gray-500">Model Name</div>
              <div className="font-medium text-gray-900">{info.model_name}</div>
            </div>
            <div>
              <div className="text-sm text-gray-500">Target Variable</div>
              <div className="font-medium text-gray-900">{info.target}</div>
            </div>
            <div>
              <div className="text-sm text-gray-500">Training Period</div>
              <div className="font-medium text-gray-900">{info.training_period}</div>
            </div>
            <div>
              <div className="text-sm text-gray-500">Test Period</div>
              <div className="font-medium text-gray-900">{info.test_period}</div>
            </div>
          </div>
        </div>

        <div>
          <h2 className="text-lg font-bold mb-2">Expected Input Features</h2>
          <div className="flex flex-wrap gap-2">
            {info.expected_features.map((feat: string) => (
              <span key={feat} className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm font-mono border border-gray-200">
                {feat}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
