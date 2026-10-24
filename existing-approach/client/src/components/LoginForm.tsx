import React, { useState } from 'react';
import { ShieldAlert } from 'lucide-react';

interface LoginFormProps {
  onLogin: (email: string, password: string, createAccount: boolean) => void;
}

export const LoginForm: React.FC<LoginFormProps> = ({ onLogin }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [createAccount, setCreateAccount] = useState(false);
  const [formError, setFormError] = useState('');

  const useDemoCredentials = () => {
    setEmail('demo@vault.local');
    setPassword('DemoVault-Only-2026!');
    setConfirmPassword('');
    setCreateAccount(false);
    setFormError('');
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setFormError('');
    if (createAccount && password !== confirmPassword) {
      setFormError('Master passwords do not match.');
      return;
    }
    if (email.trim() && password.trim()) {
      onLogin(email, password, createAccount);
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
          <h2 className="text-2xl font-bold text-center text-white mb-2">{createAccount ? 'Create Local Vault' : 'Zero-Knowledge Vault'}</h2>
          <p className="text-gray-400 text-center mb-8 text-sm">
            Your email and master password remain on this device. They identify and encrypt a local browser vault; no online account is created.
          </p>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Gmail / Email Address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                placeholder="yourname@gmail.com"
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
            {createAccount && <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Confirm Master Password</label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                placeholder="Re-enter your master password"
                required
              />
            </div>}
            {formError && <p className="text-sm text-red-400" role="alert">{formError}</p>}
            <button
              type="submit"
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded focus:outline-none focus:shadow-outline transition-colors"
            >
              {createAccount ? 'Create Local Vault' : 'Unlock Vault'}
            </button>
          </form>
          <button
            type="button"
            onClick={() => { setCreateAccount(current => !current); setConfirmPassword(''); setFormError(''); }}
            className="mt-4 w-full text-sm font-medium text-blue-300 hover:text-blue-200"
          >
            {createAccount ? 'Already have a local vault? Log in' : 'New here? Create an account'}
          </button>
          <div className="mt-6 rounded-md border border-blue-800 bg-blue-950/40 p-4 text-sm">
            <div className="mb-2 flex items-center justify-between gap-3">
              <h3 className="font-semibold text-blue-200">Demo Credentials</h3>
              <button type="button" onClick={useDemoCredentials} className="rounded border border-blue-500 px-2 py-1 text-xs font-medium text-blue-200 hover:bg-blue-900">
                Use demo
              </button>
            </div>
            <p className="text-gray-300"><strong>Gmail / Email:</strong> demo@vault.local</p>
            <p className="mt-1 text-gray-300"><strong>Master password:</strong> DemoVault-Only-2026!</p>
            <p className="mt-3 text-xs text-gray-400">For demonstration only. This creates or opens a separate local browser vault; it is not an online account.</p>
          </div>
        </div>
      </div>
    </div>
  );
};
