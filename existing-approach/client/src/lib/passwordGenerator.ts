/**
 * passwordGenerator.ts - Cryptographically secure password generation
 */

export function generatePassword(
  length: number,
  options: { uppercase: boolean; lowercase: boolean; digits: boolean; symbols: boolean }
): string {
  if (!Number.isInteger(length) || length < 1 || length > 1024) {
    throw new RangeError('Password length must be an integer from 1 to 1024.');
  }
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

  // Reject values outside the largest multiple of the alphabet length to
  // avoid the modulo bias caused by randomValue % charset.length.
  const alphabetSize = charset.length;
  const cutoff = Math.floor(0x100000000 / alphabetSize) * alphabetSize;
  const password: string[] = [];
  while (password.length < length) {
    const values = new Uint32Array(Math.min(128, length - password.length + 16));
    window.crypto.getRandomValues(values);
    for (const value of values) {
      if (value < cutoff) password.push(charset[value % alphabetSize]);
      if (password.length === length) break;
    }
  }
  return password.join('');
}
