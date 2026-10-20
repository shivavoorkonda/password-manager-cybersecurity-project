/**
 * strengthChecker.ts - Password strength checking utilities
 */
import zxcvbn from 'zxcvbn';

export interface StrengthResult {
  score: number;
  label: string;
  feedback: string[];
  guesses?: number;
  crackTime?: string;
}

/**
 * Naive rule-based approach commonly taught but flawed
 */
export function ruleBasedStrength(password: string): StrengthResult {
  let score = 0;
  const feedback: string[] = [];

  if (password.length === 0) return { score: 0, label: 'Very Weak', feedback: ['Password is empty'] };

  // Length check
  if (password.length >= 12) score += 1;
  else if (password.length < 8) feedback.push('Use at least 8 characters');
  
  // Character classes
  if (/[A-Z]/.test(password)) score += 1;
  else feedback.push('Add uppercase letters');
  
  if (/[a-z]/.test(password)) score += 1;
  else feedback.push('Add lowercase letters');
  
  if (/[0-9]/.test(password)) score += 1;
  else feedback.push('Add numbers');
  
  if (/[^A-Za-z0-9]/.test(password)) score += 1;
  else feedback.push('Add symbols');

  // Cap at 4
  score = Math.min(4, Math.floor(score * 4 / 5)); // Roughly map 0-5 to 0-4 scale

  const labels = ['Very Weak', 'Weak', 'Fair', 'Strong', 'Very Strong'];
  
  return {
    score,
    label: labels[score],
    feedback
  };
}

/**
 * Modern realistic strength check using zxcvbn
 */
export function zxcvbnStrength(password: string): StrengthResult {
  if (!password) return { score: 0, label: 'Very Weak', feedback: ['Password is empty'], guesses: 0, crackTime: 'instantly' };
  
  const result = zxcvbn(password);
  const labels = ['Very Weak', 'Weak', 'Fair', 'Strong', 'Very Strong'];
  
  const feedback = [];
  if (result.feedback.warning) feedback.push(result.feedback.warning);
  feedback.push(...result.feedback.suggestions);
  
  return {
    score: result.score,
    label: labels[result.score],
    feedback,
    guesses: result.guesses,
    crackTime: String(result.crack_times_display.offline_slow_hashing_1e4_per_second)
  };
}
