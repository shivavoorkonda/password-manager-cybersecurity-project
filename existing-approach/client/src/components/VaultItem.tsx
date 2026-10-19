import React, { useState } from 'react';
import { Copy, Eye, EyeOff, Globe, Star, Trash2 } from 'lucide-react';
import { VaultEntry } from '../App';

interface VaultItemProps {
  entry: VaultEntry;
  onDelete: (id: string) => void;
}

export const VaultItem: React.FC<VaultItemProps> = ({ entry, onDelete }) => {
  const [showPassword, setShowPassword] = useState(false);
  const [copied, setCopied] = useState(false);

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-gray-800 p-4 rounded-lg border border-gray-700 flex flex-col md:flex-row gap-4 hover:border-gray-500 transition-colors">
      <div className="flex-1">
        <div className="flex items-center gap-2 mb-1">
          {entry.url ? (
            <a href={entry.url} target="_blank" rel="noreferrer" className="text-blue-400 hover:underline flex items-center gap-1 font-bold">
              <Globe size={16} /> {entry.site}
            </a>
          ) : (
            <span className="font-bold text-gray-200">{entry.site}</span>
          )}
          {entry.category && (
            <span className="text-[10px] uppercase bg-gray-700 px-2 py-0.5 rounded text-gray-300">
              {entry.category}
            </span>
          )}
          <Star size={14} className="text-yellow-500 ml-auto md:hidden" />
        </div>
        
        <div className="text-sm text-gray-400 mb-2">{entry.username}</div>
        
        <div className="flex items-center gap-2">
          <div className="font-mono bg-gray-900 px-2 py-1 rounded text-sm flex-1 truncate">
            {showPassword ? entry.password : '••••••••••••••••'}
          </div>
          <button 
            onClick={() => setShowPassword(!showPassword)}
            className="text-gray-400 hover:text-white p-1"
          >
            {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
          </button>
          <button 
            onClick={() => copyToClipboard(entry.password)}
            className={`${copied ? 'text-green-400' : 'text-gray-400 hover:text-white'} p-1 transition-colors`}
            title="Copy password"
          >
            <Copy size={16} />
          </button>
        </div>
      </div>
      
      <div className="hidden md:flex flex-col items-end justify-between border-l border-gray-700 pl-4">
        <Star size={18} className="text-gray-600 hover:text-yellow-500 cursor-pointer transition-colors" />
        <button 
          onClick={() => onDelete(entry.id)}
          className="text-gray-500 hover:text-red-500 p-1 transition-colors"
          title="Delete entry"
        >
          <Trash2 size={16} />
        </button>
      </div>
    </div>
  );
};
