/**
 * passwordGenerator.ts - Cryptographically secure password generation
 */

export function generatePassword(
  length: number,
  options: { uppercase: boolean; lowercase: boolean; digits: boolean; symbols: boolean }
): string {
  const charsets = {
    uppercase: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
    lowercase: 'abcdefghijklmnopqrstuvwxyz',
    digits: '0123456789',
    symbols: '!@#$%^&*()_+-=[]{}|;:,.<>?'
  };

  let charset = '';
  if (options.uppercase) charset += charsets.uppercase;
  if (options.lowercase) charset += charsets.lowercase;
  if (options.digits) charset += charsets.digits;
  if (options.symbols) charset += charsets.symbols;

  if (charset === '') {
    charset = charsets.lowercase; // Fallback
  }

  const randomValues = new Uint32Array(length);
  window.crypto.getRandomValues(randomValues);

  let password = '';
  for (let i = 0; i < length; i++) {
    password += charset[randomValues[i] % charset.length];
  }

  return password;
}
