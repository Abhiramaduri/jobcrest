import {
  IndianRupee,
  DollarSign,
  Euro,
  PoundSterling,
  JapaneseYen,
  Coins,
  Banknote,
} from 'lucide-react';

/**
 * Currencies directory with symbols, full names, country flags, and matching icons.
 */
export const CURRENCIES = [
  {
    code: 'INR',
    symbol: '₹',
    name: 'Indian Rupee',
    country: 'India',
    flag: '🇮🇳',
    icon: IndianRupee,
    formatLocale: 'en-IN',
    popular: true,
  },
  {
    code: 'USD',
    symbol: '$',
    name: 'US Dollar',
    country: 'United States',
    flag: '🇺🇸',
    icon: DollarSign,
    formatLocale: 'en-US',
    popular: true,
  },
  {
    code: 'EUR',
    symbol: '€',
    name: 'Euro',
    country: 'European Union',
    flag: '🇪🇺',
    icon: Euro,
    formatLocale: 'de-DE',
    popular: true,
  },
  {
    code: 'GBP',
    symbol: '£',
    name: 'British Pound',
    country: 'United Kingdom',
    flag: '🇬🇧',
    icon: PoundSterling,
    formatLocale: 'en-GB',
    popular: true,
  },
  {
    code: 'AED',
    symbol: 'د.إ',
    name: 'UAE Dirham',
    country: 'United Arab Emirates',
    flag: '🇦🇪',
    icon: Banknote,
    formatLocale: 'en-AE',
    popular: true,
  },
  {
    code: 'CAD',
    symbol: 'C$',
    name: 'Canadian Dollar',
    country: 'Canada',
    flag: '🇨🇦',
    icon: DollarSign,
    formatLocale: 'en-CA',
    popular: true,
  },
  {
    code: 'AUD',
    symbol: 'A$',
    name: 'Australian Dollar',
    country: 'Australia',
    flag: '🇦🇺',
    icon: DollarSign,
    formatLocale: 'en-AU',
    popular: true,
  },
  {
    code: 'SGD',
    symbol: 'S$',
    name: 'Singapore Dollar',
    country: 'Singapore',
    flag: '🇸🇬',
    icon: DollarSign,
    formatLocale: 'en-SG',
    popular: true,
  },
  {
    code: 'JPY',
    symbol: '¥',
    name: 'Japanese Yen',
    country: 'Japan',
    flag: '🇯🇵',
    icon: JapaneseYen,
    formatLocale: 'ja-JP',
  },
  {
    code: 'CHF',
    symbol: 'CHF',
    name: 'Swiss Franc',
    country: 'Switzerland',
    flag: '🇨🇭',
    icon: Banknote,
    formatLocale: 'de-CH',
  },
  {
    code: 'SAR',
    symbol: '﷼',
    name: 'Saudi Riyal',
    country: 'Saudi Arabia',
    flag: '🇸🇦',
    icon: Banknote,
    formatLocale: 'ar-SA',
  },
  {
    code: 'QAR',
    symbol: 'QR',
    name: 'Qatari Riyal',
    country: 'Qatar',
    flag: '🇶🇦',
    icon: Banknote,
    formatLocale: 'ar-QA',
  },
  {
    code: 'CNY',
    symbol: '¥',
    name: 'Chinese Yuan',
    country: 'China',
    flag: '🇨🇳',
    icon: JapaneseYen,
    formatLocale: 'zh-CN',
  },
  {
    code: 'KRW',
    symbol: '₩',
    name: 'South Korean Won',
    country: 'South Korea',
    flag: '🇰🇷',
    icon: Coins,
    formatLocale: 'ko-KR',
  },
  {
    code: 'BRL',
    symbol: 'R$',
    name: 'Brazilian Real',
    country: 'Brazil',
    flag: '🇧🇷',
    icon: Banknote,
    formatLocale: 'pt-BR',
  },
  {
    code: 'ZAR',
    symbol: 'R',
    name: 'South African Rand',
    country: 'South Africa',
    flag: '🇿🇦',
    icon: Banknote,
    formatLocale: 'en-ZA',
  },
  {
    code: 'SEK',
    symbol: 'kr',
    name: 'Swedish Krona',
    country: 'Sweden',
    flag: '🇸🇪',
    icon: Coins,
    formatLocale: 'sv-SE',
  },
  {
    code: 'NZD',
    symbol: 'NZ$',
    name: 'New Zealand Dollar',
    country: 'New Zealand',
    flag: '🇳🇿',
    icon: DollarSign,
    formatLocale: 'en-NZ',
  },
  {
    code: 'MYR',
    symbol: 'RM',
    name: 'Malaysian Ringgit',
    country: 'Malaysia',
    flag: '🇲🇾',
    icon: Banknote,
    formatLocale: 'ms-MY',
  },
  {
    code: 'THB',
    symbol: '฿',
    name: 'Thai Baht',
    country: 'Thailand',
    flag: '🇹🇭',
    icon: Coins,
    formatLocale: 'th-TH',
  },
  {
    code: 'IDR',
    symbol: 'Rp',
    name: 'Indonesian Rupiah',
    country: 'Indonesia',
    flag: '🇮🇩',
    icon: Banknote,
    formatLocale: 'id-ID',
  },
  {
    code: 'PHP',
    symbol: '₱',
    name: 'Philippine Peso',
    country: 'Philippines',
    flag: '🇵🇭',
    icon: Coins,
    formatLocale: 'en-PH',
  },
  {
    code: 'KWD',
    symbol: 'KD',
    name: 'Kuwaiti Dinar',
    country: 'Kuwait',
    flag: '🇰🇼',
    icon: Banknote,
    formatLocale: 'ar-KW',
  },
  {
    code: 'OMR',
    symbol: 'OMR',
    name: 'Omani Rial',
    country: 'Oman',
    flag: '🇴🇲',
    icon: Banknote,
    formatLocale: 'ar-OM',
  },
  {
    code: 'BHD',
    symbol: 'BD',
    name: 'Bahraini Dinar',
    country: 'Bahrain',
    flag: '🇧🇭',
    icon: Banknote,
    formatLocale: 'ar-BH',
  },
  {
    code: 'VND',
    symbol: '₫',
    name: 'Vietnamese Dong',
    country: 'Vietnam',
    flag: '🇻🇳',
    icon: Coins,
    formatLocale: 'vi-VN',
  },
  {
    code: 'NGN',
    symbol: '₦',
    name: 'Nigerian Naira',
    country: 'Nigeria',
    flag: '🇳🇬',
    icon: Banknote,
    formatLocale: 'en-NG',
  },
  {
    code: 'EGP',
    symbol: 'E£',
    name: 'Egyptian Pound',
    country: 'Egypt',
    flag: '🇪🇬',
    icon: Banknote,
    formatLocale: 'ar-EG',
  },
];

export const POPULAR_CURRENCIES = CURRENCIES.filter((c) => c.popular);

/**
 * Retrieve currency definition by ISO code or symbol.
 */
export const getCurrency = (code) => {
  if (!code) return CURRENCIES[0]; // INR as default
  const upper = String(code).toUpperCase().trim();

  const byCode = CURRENCIES.find((c) => c.code === upper);
  if (byCode) return byCode;

  const bySymbol = CURRENCIES.find((c) => c.symbol === code);
  if (bySymbol) return bySymbol;

  return {
    code: upper,
    symbol: upper,
    name: upper,
    country: 'Global',
    flag: '🌐',
    icon: Banknote,
    formatLocale: 'en-US',
  };
};

/**
 * Get currency symbol with fallback.
 */
export const getCurrencySymbol = (code) => {
  const curr = getCurrency(code);
  return curr ? curr.symbol : (code || '₹');
};

/**
 * Get matching Lucide icon component.
 */
export const getCurrencyIcon = (code) => {
  const curr = getCurrency(code);
  return curr?.icon || Banknote;
};

/**
 * Format salary range with respective currency symbol and number formatting.
 */
export const formatSalaryWithCurrency = (min, max, currencyCode) => {
  const curr = getCurrency(currencyCode);
  const symbol = curr.symbol;
  const locale = curr.formatLocale || 'en-US';

  const formatNum = (val) => {
    if (val === null || val === undefined || val === '' || isNaN(Number(val))) return '';
    return Number(val).toLocaleString(locale);
  };

  const hasMin = min !== null && min !== undefined && min !== '' && !isNaN(Number(min));
  const hasMax = max !== null && max !== undefined && max !== '' && !isNaN(Number(max));

  if (hasMin && hasMax) {
    return `${symbol} ${formatNum(min)} - ${formatNum(max)}`;
  }
  if (hasMin) {
    return `${symbol} ${formatNum(min)}+`;
  }
  if (hasMax) {
    return `Up to ${symbol} ${formatNum(max)}`;
  }
  return 'Competitive';
};
