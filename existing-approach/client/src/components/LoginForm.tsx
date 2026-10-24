import React, { useState } from 'react';
import { ShieldAlert } from 'lucide-react';

interface LoginFormProps {
  onLogin: (username: string, password: string) => void;
}

export const LoginForm: React.FC<LoginFormProps> = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const useDemoCredentials = () => {
    setUsername('demo@vault.local');
    setPassword('DemoVault-Only-2026!');
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (username.trim() && password.trim()) {
      onLogin(username, password);
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
                Vault Username
              </label>
              <input
                type="email"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                placeholder="name@example.com"
                required
                autoFocus
              />
            </div>
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
              />
            </div>
            <button
              type="submit"
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded focus:outline-none focus:shadow-outline transition-colors"
            >
              Unlock Vault
            </button>
          </form>
          <div className="mt-6 rounded-md border border-blue-800 bg-blue-950/40 p-4 text-sm">
            <div className="mb-2 flex items-center justify-between gap-3">
              <h3 className="font-semibold text-blue-200">Demo Credentials</h3>
              <button type="button" onClick={useDemoCredentials} className="rounded border border-blue-500 px-2 py-1 text-xs font-medium text-blue-200 hover:bg-blue-900">
                Use demo
              </button>
            </div>
            <p className="text-gray-300"><strong>Username:</strong> demo@vault.local</p>
            <p className="mt-1 text-gray-300"><strong>Master password:</strong> DemoVault-Only-2026!</p>
            <p className="mt-3 text-xs text-gray-400">For demonstration only. This creates or opens a separate local browser vault; it is not an online account.</p>
          </div>
        </div>
      </div>
    </div>
  );
};
