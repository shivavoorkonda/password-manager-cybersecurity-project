import React, { useState } from 'react';
import { X } from 'lucide-react';
import { PasswordGenerator } from './PasswordGenerator';
import { StrengthMeter } from './StrengthMeter';

interface AddPasswordFormProps {
  onSave: (entry: any) => void;
  onCancel: () => void;
}

export const AddPasswordForm: React.FC<AddPasswordFormProps> = ({ onSave, onCancel }) => {
  const [site, setSite] = useState('');
  const [url, setUrl] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [category, setCategory] = useState('Login');
  const [notes, setNotes] = useState('');
  
  const [showGenerator, setShowGenerator] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave({ site, url, username, password, category, notes });
  };

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50">
      <div className="bg-gray-800 rounded-lg border border-gray-700 w-full max-w-lg shadow-2xl flex flex-col max-h-[90vh]">
        <div className="flex justify-between items-center p-4 border-b border-gray-700">
          <h2 className="text-xl font-bold">Add New Password</h2>
          <button onClick={onCancel} className="text-gray-400 hover:text-white">
            <X size={24} />
          </button>
        </div>
        
        <div className="p-4 overflow-y-auto">
          <form id="add-pwd-form" onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Site Name *</label>
                <input
                  type="text"
                  required
                  value={site}
                  onChange={(e) => setSite(e.target.value)}
                  className="w-full px-3 py-2 bg-gray-900 border border-gray-600 rounded focus:ring-blue-500 focus:border-blue-500"
                  placeholder="e.g. Google"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Category</label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full px-3 py-2 bg-gray-900 border border-gray-600 rounded focus:ring-blue-500 focus:border-blue-500"
                >
                  <option>Login</option>
                  <option>Finance</option>
                  <option>Email</option>
                  <option>Social</option>
                  <option>Work</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">URL</label>
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className="w-full px-3 py-2 bg-gray-900 border border-gray-600 rounded focus:ring-blue-500 focus:border-blue-500"
                placeholder="https://"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Username / Email</label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-3 py-2 bg-gray-900 border border-gray-600 rounded focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <div className="flex justify-between items-end mb-1">
                <label className="block text-sm font-medium text-gray-300">Password *</label>
                <button 
                  type="button"
                  onClick={() => setShowGenerator(!showGenerator)}
                  className="text-xs text-blue-400 hover:text-blue-300"
                >
                  {showGenerator ? 'Hide Generator' : 'Show Generator'}
                </button>
              </div>
              <input
                type="text"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-3 py-2 bg-gray-900 border border-gray-600 rounded font-mono focus:ring-blue-500 focus:border-blue-500"
              />
              
              <StrengthMeter password={password} />
              
              {showGenerator && (
                <PasswordGenerator onGenerate={setPassword} />
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Notes</label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="w-full px-3 py-2 bg-gray-900 border border-gray-600 rounded focus:ring-blue-500 focus:border-blue-500"
                rows={2}
              ></textarea>
            </div>
          </form>
        </div>
        
        <div className="p-4 border-t border-gray-700 flex justify-end gap-3">
          <button 
            type="button" 
            onClick={onCancel}
            className="px-4 py-2 border border-gray-600 rounded text-gray-300 hover:bg-gray-700"
          >
            Cancel
          </button>
          <button 
            type="submit" 
            form="add-pwd-form"
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded font-medium"
          >
            Save Password
          </button>
        </div>
      </div>
    </div>
  );
};
