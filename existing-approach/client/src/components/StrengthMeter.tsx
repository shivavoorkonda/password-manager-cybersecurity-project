import React from 'react';
import { ruleBasedStrength, zxcvbnStrength, StrengthResult } from '../lib/strengthChecker';

interface StrengthMeterProps {
  password: string;
}

const colors = ['bg-red-500', 'bg-orange-500', 'bg-yellow-500', 'bg-blue-500', 'bg-green-500'];

const Meter = ({ result, title }: { result: StrengthResult; title: string }) => {
  return (
    <div className="flex-1">
      <div className="flex justify-between items-center mb-1">
        <span className="text-xs font-semibold text-gray-300">{title}</span>
        <span className="text-xs font-bold" style={{ color: result.score > 0 ? 'inherit' : 'gray' }}>
          {result.label}
        </span>
      </div>
      <div className="flex space-x-1 h-2">
        {[0, 1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className={`flex-1 rounded-full ${
              i <= result.score && result.score > 0 ? colors[result.score] : 'bg-gray-700'
            }`}
          ></div>
        ))}
      </div>
      {result.crackTime && (
        <div className="text-[10px] text-gray-400 mt-1">Est. crack time: {result.crackTime}</div>
      )}
    </div>
  );
};

export const StrengthMeter: React.FC<StrengthMeterProps> = ({ password }) => {
  if (!password) return null;

  const ruleResult = ruleBasedStrength(password);
  const zxcResult = zxcvbnStrength(password);

  return (
    <div className="mt-2 space-y-3 p-3 bg-gray-800 rounded border border-gray-700">
      <div className="flex space-x-4">
        <Meter result={ruleResult} title="Rule-based (Naive)" />
        <Meter result={zxcResult} title="zxcvbn (Realistic)" />
      </div>
      
      {zxcResult.feedback.length > 0 && (
        <div className="text-xs text-gray-400 mt-2">
          <strong>Tip:</strong> {zxcResult.feedback.join(' ')}
        </div>
      )}
    </div>
  );
};
