import React, { useState, useEffect, useCallback } from 'react';
import { Search, Plus, LogOut, Shield, Download, Upload } from 'lucide-react';
import { LoginForm } from './components/LoginForm';
import { VaultItem } from './components/VaultItem';
import { AddPasswordForm } from './components/AddPasswordForm';
import { deriveKey, generateSalt, encrypt, decrypt } from './lib/crypto';

export interface VaultEntry {
  id: string;
  site: string;
  url: string;
  username: string;
  password: string;
  category: string;
  notes: string;
}

interface EncryptedVault {
  salt: string;
  entries: {
    id: string;
    ciphertext: string;
    iv: string;
  }[];
}

const INACTIVITY_TIMEOUT = 5 * 60 * 1000; // 5 minutes

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [cryptoKey, setCryptoKey] = useState<CryptoKey | null>(null);
  const [vault, setVault] = useState<VaultEntry[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [showAddForm, setShowAddForm] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Auto-lock timer
  const lockVault = useCallback(() => {
    setIsLoggedIn(false);
    setCryptoKey(null);
    setVault([]);
    setShowAddForm(false);
  }, []);

  useEffect(() => {
    let timeout: number;
    
    const resetTimer = () => {
      if (isLoggedIn) {
        window.clearTimeout(timeout);
        timeout = window.setTimeout(lockVault, INACTIVITY_TIMEOUT);
      }
    };

    if (isLoggedIn) {
      resetTimer();
      window.addEventListener('mousemove', resetTimer);
      window.addEventListener('keypress', resetTimer);
      window.addEventListener('click', resetTimer);
      window.addEventListener('scroll', resetTimer);
    }

    return () => {
      window.clearTimeout(timeout);
      window.removeEventListener('mousemove', resetTimer);
      window.removeEventListener('keypress', resetTimer);
      window.removeEventListener('click', resetTimer);
      window.removeEventListener('scroll', resetTimer);
    };
  }, [isLoggedIn, lockVault]);

  // Handle Login
  const handleLogin = async (masterPassword: string) => {
    try {
      setError(null);
      
      // Load encrypted vault from local storage
      const storedVaultRaw = localStorage.getItem('zk_vault');
      
      let key: CryptoKey;
      let decryptedVault: VaultEntry[] = [];
      
      if (storedVaultRaw) {
        const storedVault = JSON.parse(storedVaultRaw) as EncryptedVault;
        const salt = Uint8Array.from(atob(storedVault.salt), c => c.charCodeAt(0));
        key = await deriveKey(masterPassword, salt);
        
        // Attempt decryption to verify password
        try {
          const newVault = [];
          for (const entry of storedVault.entries) {
            const decryptedString = await decrypt(entry.ciphertext, entry.iv, key);
            newVault.push(JSON.parse(decryptedString));
          }
          decryptedVault = newVault;
        } catch (err) {
          throw new Error("Invalid master password or corrupted vault.");
        }
      } else {
        // Initialize new vault
        const salt = generateSalt();
        key = await deriveKey(masterPassword, salt);
        
        // Save empty structure to lock in the salt
        const emptyVault: EncryptedVault = {
          salt: btoa(String.fromCharCode(...salt)),
          entries: []
        };
        localStorage.setItem('zk_vault', JSON.stringify(emptyVault));
      }

      setCryptoKey(key);
      setVault(decryptedVault);
      setIsLoggedIn(true);
    } catch (err: any) {
      setError(err.message || "Failed to login");
    }
  };

  // Save changes to encrypted local storage
  const saveVault = async (newVault: VaultEntry[], key: CryptoKey) => {
    try {
      const storedVaultRaw = localStorage.getItem('zk_vault');
      if (!storedVaultRaw) throw new Error("Vault structure not found");
      
      const storedVault = JSON.parse(storedVaultRaw) as EncryptedVault;
      
      const encryptedEntries = await Promise.all(
        newVault.map(async (entry) => {
          const plaintext = JSON.stringify(entry);
          const { ciphertext, iv } = await encrypt(plaintext, key);
          return { id: entry.id, ciphertext, iv };
        })
      );
      
      const newStoredVault: EncryptedVault = {
        salt: storedVault.salt,
        entries: encryptedEntries
      };
      
      localStorage.setItem('zk_vault', JSON.stringify(newStoredVault));
      setVault(newVault);
    } catch (err) {
      console.error("Failed to save vault", err);
      setError("Failed to save changes.");
    }
  };

  const handleAddEntry = async (entryData: Omit<VaultEntry, 'id'>) => {
    if (!cryptoKey) return;
    
    const newEntry: VaultEntry = {
      ...entryData,
      id: crypto.randomUUID()
    };
    
    const newVault = [...vault, newEntry];
    await saveVault(newVault, cryptoKey);
    setShowAddForm(false);
  };

  const handleDeleteEntry = async (id: string) => {
    if (!cryptoKey) return;
    
    if (confirm("Are you sure you want to delete this password?")) {
      const newVault = vault.filter(e => e.id !== id);
      await saveVault(newVault, cryptoKey);
    }
  };

  // UI Filtering
  const filteredVault = vault.filter(entry => {
    const matchesSearch = entry.site.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          entry.username.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = categoryFilter === 'All' || entry.category === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  const categories = ['All', ...new Set(vault.map(e => e.category).filter(Boolean))];

  if (!isLoggedIn) {
    return (
      <>
        {error && (
          <div className="fixed top-4 left-1/2 -translate-x-1/2 bg-red-500 text-white px-4 py-2 rounded shadow-lg z-50">
            {error}
          </div>
        )}
        <LoginForm onLogin={handleLogin} />
      </>
    );
  }

  return (
    <div className="min-h-screen flex flex-col max-w-5xl mx-auto p-4 md:p-6">
      <header className="flex justify-between items-center mb-8 bg-gray-800 p-4 rounded-lg border border-gray-700">
        <div className="flex items-center gap-2 text-blue-400">
          <Shield size={28} />
          <h1 className="text-xl font-bold text-white hidden sm:block">ZK Vault</h1>
        </div>
        
        <div className="flex items-center gap-4">
          <button 
            onClick={() => setShowAddForm(true)}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded font-medium transition-colors"
          >
            <Plus size={18} /> <span className="hidden sm:inline">Add Password</span>
          </button>
          
          <button 
            onClick={lockVault}
            className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
            title="Lock Vault"
          >
            <LogOut size={20} />
          </button>
        </div>
      </header>

      <div className="flex flex-col md:flex-row gap-6 flex-1">
        {/* Sidebar */}
        <aside className="w-full md:w-64 flex flex-col gap-6">
          <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
            <h2 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3">Categories</h2>
            <ul className="space-y-1">
              {categories.map(cat => (
                <li key={cat}>
                  <button
                    onClick={() => setCategoryFilter(cat)}
                    className={`w-full text-left px-3 py-2 rounded text-sm ${
                      categoryFilter === cat ? 'bg-blue-900/50 text-blue-400' : 'text-gray-300 hover:bg-gray-700'
                    }`}
                  >
                    {cat}
                  </button>
                </li>
              ))}
            </ul>
          </div>
          
          <div className="bg-gray-800 p-4 rounded-lg border border-gray-700 mt-auto">
            <div className="text-xs text-gray-500 text-center">
              Vault auto-locks after 5 minutes of inactivity.
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 flex flex-col">
          <div className="mb-6 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={20} />
            <input
              type="text"
              placeholder="Search passwords..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-blue-500"
            />
          </div>

          <div className="flex-1 space-y-3">
            {filteredVault.length === 0 ? (
              <div className="text-center py-12 bg-gray-800 rounded-lg border border-gray-700 border-dashed">
                <Shield size={48} className="mx-auto text-gray-600 mb-4" />
                <h3 className="text-lg font-medium text-gray-300">No passwords found</h3>
                <p className="text-gray-500 text-sm mt-1">
                  {searchTerm || categoryFilter !== 'All' 
                    ? "Try adjusting your search or filters." 
                    : "Add your first password to get started."}
                </p>
              </div>
            ) : (
              filteredVault.map((entry) => (
                <VaultItem key={entry.id} entry={entry} onDelete={handleDeleteEntry} />
              ))
            )}
          </div>
        </main>
      </div>

      {showAddForm && (
        <AddPasswordForm 
          onSave={handleAddEntry} 
          onCancel={() => setShowAddForm(false)} 
        />
      )}
    </div>
  );
}
