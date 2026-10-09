import { useEffect, useState } from 'react';

export default function About() {
  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Methodology</h1>
        <p className="text-gray-500 mt-2">Data pipeline and ML design choices.</p>
      </div>

      <div className="bg-white p-8 rounded-xl border border-gray-100 shadow-sm prose max-w-none">
        <h3 className="text-lg font-bold text-gray-800 border-b pb-2">Target Variable</h3>
        <p className="text-gray-600 mt-3 mb-6">
          The machine learning system predicts the total energy consumed during an EV charging session in kilowatt-hours (kWh).
        </p>

        <h3 className="text-lg font-bold text-gray-800 border-b pb-2">Feature Selection & Leakage Prevention</h3>
        <p className="text-gray-600 mt-3 mb-2">
          To strictly prevent target leakage, all features used by the model represent information mathematically guaranteed to be known at the exact moment a session starts. 
        </p>
        <ul className="list-disc pl-5 text-gray-600 mb-6 space-y-1">
          <li><strong>Included:</strong> Session start hour, day of week, month, weekend status, charger properties, location category.</li>
          <li><strong>Excluded:</strong> UserID and ChargerID were excluded to prevent memorization of ID-specific patterns and to guarantee generalizability. Duration was strictly excluded as it is unknown until the session terminates.</li>
        </ul>

        <h3 className="text-lg font-bold text-gray-800 border-b pb-2">Chronological Split</h3>
        <p className="text-gray-600 mt-3 mb-6">
          Data was split strictly chronologically (not randomly) to simulate a real-world production environment where past data is used to predict future usage.
        </p>

        <h3 className="text-lg font-bold text-gray-800 border-b pb-2">Model Interpretation (R²)</h3>
        <p className="text-gray-600 mt-3">
          The baseline context variables explain approximately 7.5% of total energy demand variance. This scientifically accurately reflects that physical demand is primarily driven by the individual EV's initial battery state-of-charge and driver needs—features purposely excluded because they are untracked. The pipeline establishes a baseline expectation load rather than a psychic pinpoint prediction.
        </p>
      </div>
    </div>
  );
}
