import React, { useState, useRef, useEffect } from 'react';
import {
  Search,
  Check,
  ChevronDown,
  Globe,
  Coins,
  Sparkles,
} from 'lucide-react';
import { CURRENCIES, POPULAR_CURRENCIES, getCurrency } from '../../utils/currencies';

export const CurrencySelector = ({
  value = 'INR',
  onChange,
  name = 'salary_currency',
  register,
  label = 'Salary Currency',
  error,
  helperText,
  showQuickPills = true,
  className = '',
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const dropdownRef = useRef(null);
  const searchInputRef = useRef(null);

  const selectedCurrency = getCurrency(value);

  // Close dropdown on outside click
  useEffect(() => {
    const handleOutsideClick = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    if (isOpen) {
      document.addEventListener('mousedown', handleOutsideClick);
      // Auto focus search input when opened
      setTimeout(() => searchInputRef.current?.focus(), 50);
    }
    return () => {
      document.removeEventListener('mousedown', handleOutsideClick);
    };
  }, [isOpen]);

  // Filter currencies
  const filteredCurrencies = CURRENCIES.filter((curr) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase().trim();
    return (
      curr.code.toLowerCase().includes(q) ||
      curr.name.toLowerCase().includes(q) ||
      curr.symbol.toLowerCase().includes(q) ||
      (curr.country && curr.country.toLowerCase().includes(q))
    );
  });

  const handleSelect = (code) => {
    if (onChange) {
      onChange(code);
    }
    setIsOpen(false);
    setSearchQuery('');
  };

  return (
    <div className={`space-y-2 ${className}`} ref={dropdownRef}>
      {/* Label and Selected Info */}
      <div className="flex items-center justify-between">
        <label className="text-xs font-semibold tracking-wide text-ink-muted uppercase flex items-center gap-1.5">
          <span>{label}</span>
          <span className="text-[10px] text-wine-burgundy font-bold px-1.5 py-0.5 bg-wine-tint rounded">
            {selectedCurrency.code} ({selectedCurrency.symbol})
          </span>
        </label>
        <span className="text-[11px] text-ink-subtle hidden sm:inline">
          {selectedCurrency.country}
        </span>
      </div>

      {/* Main Trigger Button */}
      <div className="relative">
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          className={`w-full bg-white border rounded-xl px-3.5 py-2.5 text-left flex items-center justify-between transition-all duration-200 outline-none
            ${isOpen ? 'border-wine-deep ring-2 ring-wine-burgundy/15' : 'border-sand-border hover:border-wine-burgundy/40'}
            ${error ? 'border-status-error' : ''}`}
        >
          <div className="flex items-center gap-2.5 min-w-0">
            <span className="text-lg leading-none" role="img" aria-label={selectedCurrency.name}>
              {selectedCurrency.flag}
            </span>
            <div className="w-6 h-6 rounded-lg bg-sand-canvas border border-sand-border flex items-center justify-center text-xs font-bold text-wine-deep flex-shrink-0">
              {selectedCurrency.symbol}
            </div>
            <div className="truncate">
              <span className="text-sm font-bold text-ink-charcoal mr-1.5">
                {selectedCurrency.code}
              </span>
              <span className="text-xs text-ink-muted truncate">
                — {selectedCurrency.name}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-1.5 text-ink-subtle flex-shrink-0">
            <ChevronDown className={`w-4 h-4 transition-transform duration-200 ${isOpen ? 'rotate-180 text-wine-deep' : ''}`} />
          </div>
        </button>

        {/* Hidden select for standard forms and react-hook-form fallback */}
        <select
          name={name}
          value={value}
          onChange={(e) => handleSelect(e.target.value)}
          {...(register ? register(name) : {})}
          className="sr-only"
          tabIndex={-1}
          aria-hidden="true"
        >
          {CURRENCIES.map((c) => (
            <option key={c.code} value={c.code}>
              {c.code} - {c.name} ({c.symbol})
            </option>
          ))}
        </select>

        {/* Dropdown Menu Popover */}
        {isOpen && (
          <div className="absolute left-0 right-0 top-full mt-2 bg-white rounded-2xl border border-sand-border shadow-wine-lg p-2.5 z-50 space-y-2 animate-in fade-in duration-150">
            {/* Search Input */}
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-3 text-ink-subtle" />
              <input
                ref={searchInputRef}
                type="text"
                placeholder="Search by code (INR, USD), name, or symbol..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-sand-canvas/50 border border-sand-border rounded-xl pl-9 pr-3.5 py-2 text-xs text-ink-charcoal placeholder:text-ink-subtle/70 focus:outline-none focus:border-wine-deep focus:bg-white transition-all"
              />
            </div>

            {/* List */}
            <div className="max-h-60 overflow-y-auto space-y-1 pr-1 divide-y divide-sand-border/30">
              {filteredCurrencies.length === 0 ? (
                <div className="p-4 text-center text-xs text-ink-muted">
                  No currency found matching &quot;{searchQuery}&quot;
                </div>
              ) : (
                filteredCurrencies.map((curr) => {
                  const isSelected = curr.code === selectedCurrency.code;
                  return (
                    <button
                      key={curr.code}
                      type="button"
                      onClick={() => handleSelect(curr.code)}
                      className={`w-full flex items-center justify-between p-2 rounded-xl text-left transition-all ${
                        isSelected
                          ? 'bg-wine-deep text-white font-medium shadow-wine-sm'
                          : 'hover:bg-wine-tint text-ink-charcoal'
                      }`}
                    >
                      <div className="flex items-center gap-2.5 min-w-0">
                        <span className="text-base" role="img" aria-label={curr.country}>
                          {curr.flag}
                        </span>
                        <div
                          className={`w-6 h-6 rounded-lg flex items-center justify-center text-xs font-bold flex-shrink-0 ${
                            isSelected
                              ? 'bg-white/20 text-white'
                              : 'bg-sand-canvas text-wine-deep border border-sand-border'
                          }`}
                        >
                          {curr.symbol}
                        </div>
                        <div className="truncate">
                          <span className={`text-xs font-bold mr-1.5 ${isSelected ? 'text-white' : 'text-ink-charcoal'}`}>
                            {curr.code}
                          </span>
                          <span className={`text-[11px] truncate ${isSelected ? 'text-white/80' : 'text-ink-muted'}`}>
                            {curr.name}
                          </span>
                        </div>
                      </div>

                      {isSelected && (
                        <Check className="w-4 h-4 text-white flex-shrink-0 ml-2" />
                      )}
                    </button>
                  );
                })
              )}
            </div>
          </div>
        )}
      </div>

      {/* Popular Currencies Quick Select Pills */}
      {showQuickPills && (
        <div className="pt-1">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-[11px] font-semibold text-ink-muted">
              Frequently Used:
            </span>
            <button
              type="button"
              onClick={() => setIsOpen(true)}
              className="text-[11px] font-semibold text-wine-deep hover:underline"
            >
              Browse all ({CURRENCIES.length})
            </button>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {POPULAR_CURRENCIES.map((curr) => {
              const isSelected = curr.code === selectedCurrency.code;
              return (
                <button
                  key={curr.code}
                  type="button"
                  onClick={() => handleSelect(curr.code)}
                  className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-semibold border transition-all ${
                    isSelected
                      ? 'bg-wine-deep text-white border-wine-deep shadow-xs'
                      : 'bg-white text-ink-charcoal border-sand-border hover:bg-wine-tint hover:border-wine-burgundy/40'
                  }`}
                  title={`${curr.name} (${curr.country})`}
                >
                  <span>{curr.flag}</span>
                  <span className={isSelected ? 'text-white' : 'text-wine-deep'}>
                    {curr.symbol}
                  </span>
                  <span>{curr.code}</span>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {error && <p className="text-xs text-status-error font-medium">{error}</p>}
      {!error && helperText && <p className="text-xs text-ink-subtle">{helperText}</p>}
    </div>
  );
};

export default CurrencySelector;
