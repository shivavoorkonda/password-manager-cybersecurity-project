/**
 * crypto.ts - Cryptographic operations for zero-knowledge architecture.
 * Uses Web Crypto API for secure operations.
 */

// Helper to convert ArrayBuffer to Base64
function bufferToBase64(buffer: ArrayBuffer): string {
  const bytes = new Uint8Array(buffer);
  let binary = '';
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}

// Copy into an owned ArrayBuffer because Web Crypto rejects views whose backing
// type could be SharedArrayBuffer under current TypeScript DOM definitions.
function toArrayBuffer(data: Uint8Array): ArrayBuffer {
  const copy = new Uint8Array(data.length);
  copy.set(data);
  return copy.buffer;
}

// Helper to convert Base64 to Uint8Array
function base64ToBuffer(base64: string): ArrayBuffer {
  const binary_string = atob(base64);
  const len = binary_string.length;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i++) {
    bytes[i] = binary_string.charCodeAt(i);
  }
  return bytes.buffer;
}

/**
 * Derives an AES-256-GCM encryption key from a master password and salt.
 * Uses PBKDF2 with HMAC-SHA256 and 600,000 iterations.
 */
export async function deriveKey(masterPassword: string, salt: Uint8Array, iterations: number = 600000): Promise<CryptoKey> {
  const enc = new TextEncoder();
  const keyMaterial = await window.crypto.subtle.importKey(
    'raw',
    enc.encode(masterPassword),
    'PBKDF2',
    false,
    ['deriveBits', 'deriveKey']
  );

  return window.crypto.subtle.deriveKey(
    {
      name: 'PBKDF2',
      salt: toArrayBuffer(salt),
      iterations: iterations,
      hash: 'SHA-256'
    },
    keyMaterial,
    { name: 'AES-GCM', length: 256 },
    false,
    ['encrypt', 'decrypt']
  );
}

/**
 * Generates a random 16-byte salt.
 */
export function generateSalt(): Uint8Array {
  const salt = new Uint8Array(16);
  window.crypto.getRandomValues(salt);
  return salt;
}

/**
 * Hashes the master password for server-side authentication verification.
 * This is deliberately different from the encryption key derivation.
 */
export async function hashMasterPassword(password: string, salt: Uint8Array): Promise<string> {
  const enc = new TextEncoder();
  const keyMaterial = await window.crypto.subtle.importKey(
    'raw',
    enc.encode(password),
    'PBKDF2',
    false,
    ['deriveBits']
  );

  // Different iteration count or salt could be used to separate auth from encryption
  const hashBuffer = await window.crypto.subtle.deriveBits(
    {
      name: 'PBKDF2',
      salt: toArrayBuffer(salt),
      iterations: 100000,
      hash: 'SHA-256'
    },
    keyMaterial,
    256
  );

  return bufferToBase64(hashBuffer);
}

/**
 * Encrypts a plaintext string using AES-256-GCM.
 */
export async function encrypt(plaintext: string, key: CryptoKey): Promise<{ciphertext: string, iv: string, salt?: string}> {
  const iv = new Uint8Array(12);
  window.crypto.getRandomValues(iv);

  const enc = new TextEncoder();
  const encodedPlaintext = enc.encode(plaintext);

  const ciphertextBuffer = await window.crypto.subtle.encrypt(
    {
      name: 'AES-GCM',
      iv: toArrayBuffer(iv)
    },
    key,
    encodedPlaintext
  );

  return {
    ciphertext: bufferToBase64(ciphertextBuffer),
    iv: bufferToBase64(toArrayBuffer(iv))
  };
}

/**
 * Decrypts a ciphertext string using AES-256-GCM.
 */
export async function decrypt(ciphertext: string, ivBase64: string, key: CryptoKey): Promise<string> {
  const ciphertextBuffer = base64ToBuffer(ciphertext);
  const iv = base64ToBuffer(ivBase64);

  const decryptedBuffer = await window.crypto.subtle.decrypt(
    {
      name: 'AES-GCM',
      iv
    },
    key,
    ciphertextBuffer
  );

  const dec = new TextDecoder();
  return dec.decode(decryptedBuffer);
}
