import React, { useState, useEffect } from 'react';
import { generatePassword } from '../lib/passwordGenerator';
import { Copy, RefreshCw } from 'lucide-react';

interface PasswordGeneratorProps {
  onGenerate: (password: string) => void;
}

export const PasswordGenerator: React.FC<PasswordGeneratorProps> = ({ onGenerate }) => {
  const [length, setLength] = useState(16);
  const [options, setOptions] = useState({
    uppercase: true,
    lowercase: true,
    digits: true,
    symbols: true,
  });
  const [currentPassword, setCurrentPassword] = useState('');

  const handleGenerate = () => {
    const pwd = generatePassword(length, options);
    setCurrentPassword(pwd);
    onGenerate(pwd);
  };

  // Generate initial password
  useEffect(() => {
    handleGenerate();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleCheckboxChange = (option: keyof typeof options) => {
    // Prevent unchecking the last option
    const activeCount = Object.values(options).filter(Boolean).length;
    if (activeCount === 1 && options[option]) return;

    setOptions((prev) => ({ ...prev, [option]: !prev[option] }));
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(currentPassword);
  };

  return (
    <div className="bg-gray-800 p-4 rounded-md border border-gray-700 mt-4">
      <div className="flex justify-between items-center mb-4 bg-gray-900 p-2 rounded">
        <span className="font-mono text-lg break-all mr-2">{currentPassword}</span>
        <div className="flex space-x-2 flex-shrink-0">
          <button
            type="button"
            onClick={handleGenerate}
            className="p-2 bg-gray-700 hover:bg-gray-600 rounded text-gray-300 transition-colors"
            title="Generate new"
          >
            <RefreshCw size={18} />
          </button>
          <button
            type="button"
            onClick={copyToClipboard}
            className="p-2 bg-blue-600 hover:bg-blue-500 rounded text-white transition-colors"
            title="Copy"
          >
            <Copy size={18} />
          </button>
        </div>
      </div>

      <div className="mb-4">
        <div className="flex justify-between mb-1">
          <label className="text-sm font-medium">Length</label>
          <span className="text-sm text-blue-400 font-bold">{length}</span>
        </div>
        <input
          type="range"
          min="8"
          max="128"
          value={length}
          onChange={(e) => setLength(parseInt(e.target.value))}
          className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
          onMouseUp={handleGenerate}
          onTouchEnd={handleGenerate}
        />
      </div>

      <div className="grid grid-cols-2 gap-2">
        {Object.entries(options).map(([key, value]) => (
          <label key={key} className="flex items-center space-x-2 cursor-pointer">
            <input
              type="checkbox"
              checked={value}
              onChange={() => {
                handleCheckboxChange(key as keyof typeof options);
                setTimeout(handleGenerate, 0);
              }}
              className="rounded bg-gray-700 border-gray-600 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm capitalize">{key}</span>
          </label>
        ))}
      </div>
    </div>
  );
};
