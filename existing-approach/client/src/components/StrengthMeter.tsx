import React, { useEffect, useState } from 'react';
import { ruleBasedStrength, zxcvbnStrength, StrengthResult } from '../lib/strengthChecker';
import { checkPasswordBreach } from '../../../../proposed-improvement/hibp-integration/hibp_check';

interface StrengthMeterProps {
  password: string;
}

interface MlResult {
  label: string;
  confidence: number;
  model: string;
}

const colors = ['bg-red-500', 'bg-orange-500', 'bg-yellow-500', 'bg-blue-500', 'bg-green-500'];

const Meter = ({ result, title }: { result: StrengthResult; title: string }) => (
  <div className="flex-1">
    <div className="flex justify-between items-center mb-1">
      <span className="text-xs font-semibold text-gray-300">{title}</span>
      <span className="text-xs font-bold">{result.label}</span>
    </div>
    <div className="flex space-x-1 h-2">
      {[0, 1, 2, 3, 4].map((i) => (
        <div key={i} className={`flex-1 rounded-full ${i <= result.score && result.score > 0 ? colors[result.score] : 'bg-gray-700'}`} />
      ))}
    </div>
    {result.crackTime && <div className="text-[10px] text-gray-400 mt-1">zxcvbn estimate: {result.crackTime}</div>}
  </div>
);

export const StrengthMeter: React.FC<StrengthMeterProps> = ({ password }) => {
  const [mlResult, setMlResult] = useState<MlResult | null>(null);
  const [mlError, setMlError] = useState('');
  const [breach, setBreach] = useState<{ breached: boolean; count: number } | null>(null);
  const [breachError, setBreachError] = useState('');

  useEffect(() => {
    setMlResult(null);
    setMlError('');
    setBreach(null);
    setBreachError('');
    if (!password) return;

    const controller = new AbortController();
    const timer = window.setTimeout(async () => {
      try {
        const response = await fetch('/ml-api/predict', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ password }),
          signal: controller.signal,
        });
        const body = await response.json();
        if (!response.ok) throw new Error(body.error || `ML service returned ${response.status}`);
        setMlResult({ label: body.label, confidence: body.confidence, model: body.model || 'ML' });
      } catch (error) {
        if (!controller.signal.aborted) setMlError(error instanceof Error ? error.message : 'ML analysis unavailable');
      }

      try {
        setBreach(await checkPasswordBreach(password, controller.signal));
      } catch (error) {
        if (!controller.signal.aborted) setBreachError(error instanceof Error ? error.message : 'Breach check unavailable');
      }
    }, 600);

    return () => {
      window.clearTimeout(timer);
      controller.abort();
    };
  }, [password]);

  if (!password) return null;

  const ruleResult = ruleBasedStrength(password);
  const zxcResult = zxcvbnStrength(password);

  return (
    <div className="mt-2 space-y-3 p-3 bg-gray-800 rounded border border-gray-700">
      <div className="flex space-x-4">
        <Meter result={ruleResult} title="Rule-based" />
        <Meter result={zxcResult} title="zxcvbn" />
      </div>
      <div className="text-xs text-gray-300" aria-live="polite">
        <strong>ML model:</strong>{' '}
        {mlResult ? `${mlResult.model}: ${mlResult.label} (${(mlResult.confidence * 100).toFixed(1)}% model confidence)` : mlError || 'Analyzing…'}
      </div>
      <div className="text-xs text-gray-300" aria-live="polite">
        <strong>Have I Been Pwned:</strong>{' '}
        {breach ? (breach.breached ? `Found in known breaches (${breach.count.toLocaleString()} occurrences).` : 'No match found.') : breachError || 'Checking…'}
      </div>
      <p className="text-[10px] text-gray-500">ML analysis sends the password to the local service on this computer. HIBP receives only a 5-character SHA-1 prefix; the password itself is not sent to HIBP.</p>
      {zxcResult.feedback.length > 0 && <div className="text-xs text-gray-400"><strong>Tip:</strong> {zxcResult.feedback.join(' ')}</div>}
    </div>
  );
};
