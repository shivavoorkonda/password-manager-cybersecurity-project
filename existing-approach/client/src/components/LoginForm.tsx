import React, { useState } from 'react';
import { ShieldAlert } from 'lucide-react';

interface LoginFormProps {
  onLogin: (password: string) => void;
}

export const LoginForm: React.FC<LoginFormProps> = ({ onLogin }) => {
  const [password, setPassword] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (password.trim()) {
      onLogin(password);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-900 px-4">
      <div className="max-w-md w-full bg-gray-800 rounded-lg shadow-xl border border-gray-700 overflow-hidden">
        <div className="p-8">
          <div className="flex justify-center mb-6">
            <div className="bg-blue-900 p-3 rounded-full">
              <ShieldAlert size={40} className="text-blue-400" />
            </div>
          </div>
          <h2 className="text-2xl font-bold text-center text-white mb-2">Zero-Knowledge Vault</h2>
          <p className="text-gray-400 text-center mb-8 text-sm">
            Your master password never leaves your device. It is used locally to encrypt and decrypt your vault.
          </p>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Master Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                placeholder="Enter your master password"
                required
                autoFocus
              />
            </div>
            <button
              type="submit"
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded focus:outline-none focus:shadow-outline transition-colors"
            >
              Unlock Vault
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
