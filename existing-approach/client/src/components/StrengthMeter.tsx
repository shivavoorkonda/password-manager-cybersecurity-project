import React, { useEffect, useState } from 'react';
import { ruleBasedStrength, zxcvbnStrength, StrengthResult } from '../lib/strengthChecker';

interface StrengthMeterProps { password: string; }
interface AnalysisResult {
  breach_check: { breached?: boolean; count?: number; error?: string };
  ml_model: { label: string; confidence: number | null; model: string | null };
  consensus: { label: 'weak' | 'medium' | 'strong'; ml_available: boolean };
}
interface Recommendation { password: string; label: string; confidence: number; }

const colors = ['bg-red-500', 'bg-orange-500', 'bg-yellow-500', 'bg-blue-500', 'bg-green-500'];
const badgeClasses = { weak: 'bg-red-950 text-red-300 border-red-700', medium: 'bg-yellow-950 text-yellow-300 border-yellow-700', strong: 'bg-green-950 text-green-300 border-green-700' };

// Classifier probabilities are not guarantees. Avoid displaying a misleading
// absolute "100% confidence" when the model returns an exact 1.0.
const formatModelProbability = (confidence: number | null): string => {
  if (confidence === null) return 'n/a';
  if (confidence >= 0.995) return 'very high (≥99%)';
  return `${(confidence * 100).toFixed(1)}%`;
};

const Meter = ({ result, title }: { result: StrengthResult; title: string }) => (
  <div className="flex-1"><div className="flex justify-between items-center mb-1"><span className="text-xs font-semibold text-gray-300">{title}</span><span className="text-xs font-bold">{result.label}</span></div><div className="flex space-x-1 h-2">{[0, 1, 2, 3, 4].map(i => <div key={i} className={`flex-1 rounded-full ${i <= result.score && result.score > 0 ? colors[result.score] : 'bg-gray-700'}`} />)}</div>{result.crackTime && <div className="text-[10px] text-gray-400 mt-1">zxcvbn estimate: {result.crackTime}</div>}</div>
);

export const StrengthMeter: React.FC<StrengthMeterProps> = ({ password }) => {
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [mlError, setMlError] = useState('');
  const [recommendations, setRecommendations] = useState<Recommendation[] | null>(null);
  const [recoLoading, setRecoLoading] = useState(false);
  const [visible, setVisible] = useState<Set<number>>(new Set());
  const [copyStatus, setCopyStatus] = useState('');

  useEffect(() => {
    setAnalysis(null); setMlError(''); setRecommendations(null); setVisible(new Set()); setCopyStatus('');
    if (!password) return;
    const controller = new AbortController();
    const timer = window.setTimeout(async () => {
      try {
        const response = await fetch('/ml-api/analyze', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ password }), signal: controller.signal });
        const body = await response.json();
        if (!response.ok) throw new Error(body.error || `ML service returned ${response.status}`);
        setAnalysis(body);
        if (body.ml_model?.label === 'weak' || body.ml_model?.label === 'medium') {
          setRecoLoading(true);
          try {
            const recommendationResponse = await fetch('/ml-api/recommend', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ password }), signal: controller.signal });
            const recommendationBody = await recommendationResponse.json();
            if (!recommendationResponse.ok) throw new Error(recommendationBody.error || 'Recommendations unavailable');
            setRecommendations(recommendationBody.recommendations || []);
          } catch { if (!controller.signal.aborted) setRecommendations([]); }
          finally { if (!controller.signal.aborted) setRecoLoading(false); }
        }
      } catch (error) { if (!controller.signal.aborted) setMlError(error instanceof Error ? error.message : 'ML analysis unavailable'); }
    }, 600);
    return () => { window.clearTimeout(timer); controller.abort(); };
  }, [password]);

  if (!password) return null;
  const ruleResult = ruleBasedStrength(password);
  const zxcResult = zxcvbnStrength(password);
  const breach = analysis?.breach_check;
  const consensus = analysis?.consensus;
  const copyRecommendation = async (value: string) => {
    try { await navigator.clipboard.writeText(value); setCopyStatus('Copied to clipboard.'); }
    catch { setCopyStatus('Copy failed; select the suggestion manually.'); }
  };

  return <div className="mt-2 space-y-3 p-3 bg-gray-800 rounded border border-gray-700">
    <div className="flex space-x-4"><Meter result={ruleResult} title="Rule-based" /><Meter result={zxcResult} title="zxcvbn" /></div>
    <div className="text-xs text-gray-300" aria-live="polite"><strong>ML model:</strong>{' '}{analysis ? `${analysis.ml_model.model || 'ML'}: ${analysis.ml_model.label} (${formatModelProbability(analysis.ml_model.confidence)} model probability)` : mlError || 'Analyzing…'}</div>
    {consensus && <div className="flex items-center gap-2 text-xs" aria-live="polite"><strong className={`rounded border px-2 py-1 uppercase tracking-wide ${consensus.ml_available ? badgeClasses[consensus.label] : 'bg-gray-700 text-gray-200 border-gray-500'}`}>{consensus.ml_available ? consensus.label : 'ML unavailable'}</strong>{!consensus.ml_available && <span className="text-gray-400">Using zxcvbn until the local ML service is available.</span>}</div>}
    <div className="text-xs text-gray-300" aria-live="polite"><strong>Have I Been Pwned:</strong>{' '}{breach ? (breach.error ? breach.error : breach.breached ? `Found in known breaches (${(breach.count || 0).toLocaleString()} occurrences).` : 'No match found.') : mlError || 'Checking…'}</div>
    {(recoLoading || recommendations) && <section className="space-y-2 rounded border border-green-800 bg-green-950/20 p-3" aria-live="polite"><h3 className="text-sm font-semibold text-green-200">Recommended stronger alternatives</h3>{recoLoading && <p className="text-xs text-gray-300">Creating model-validated suggestions…</p>}{recommendations?.map((recommendation, index) => <div key={`${recommendation.password}-${index}`} className="flex flex-wrap items-center gap-2 text-xs text-gray-200"><code className="rounded bg-gray-950 px-2 py-1">{visible.has(index) ? recommendation.password : '••••••••••••••••'}</code><span className="rounded bg-green-900 px-2 py-1 text-green-200">Strong ✓ {formatModelProbability(recommendation.confidence)}</span><button type="button" className="rounded border border-gray-600 px-2 py-1 hover:bg-gray-700" onClick={() => setVisible(current => { const next = new Set(current); next.has(index) ? next.delete(index) : next.add(index); return next; })}>{visible.has(index) ? 'Hide' : 'Show'}</button><button type="button" className="rounded border border-gray-600 px-2 py-1 hover:bg-gray-700" onClick={() => void copyRecommendation(recommendation.password)}>Copy</button></div>)}{recommendations?.length === 0 && <p className="text-xs text-gray-400">No validated suggestion was available. Try the password generator instead.</p>}<p className="text-[10px] text-gray-400">Suggestions keep your style but add length and random characters to resist dictionary attacks.</p>{copyStatus && <p className="text-[10px] text-gray-300">{copyStatus}</p>}</section>}
    <p className="text-[10px] text-gray-500">Model probability is not a guarantee that a password is secure. ML analysis sends the password to the local service on this computer. HIBP receives only a 5-character SHA-1 prefix; the password itself is not sent to HIBP.</p>
    {zxcResult.feedback.length > 0 && <div className="text-xs text-gray-400"><strong>Tip:</strong> {zxcResult.feedback.join(' ')}</div>}
  </div>;
};
