import { formatCurrency } from '../currency-formatter.util';

describe('formatCurrency', () => {
  it('formats valid number with default USD and en-US', () => {
    expect(formatCurrency(1234.5)).toBe('$1,234.50');
  });

  it('formats valid string with custom currency and locale', () => {
    expect(formatCurrency('1000', 'EUR', 'de-DE')).toBe('1.000,00 €');
  });

  it('returns fallback for null, undefined, or invalid number', () => {
    expect(formatCurrency(null)).toBe('-');
    expect(formatCurrency(undefined)).toBe('-');
    expect(formatCurrency('abc')).toBe('-');
  });

  it('returns custom fallback message for invalid input', () => {
    expect(formatCurrency('NaN', 'USD', 'en-US', { invalidAmountMessage: 'Invalid' })).toBe('Invalid');
  });

  it('handles negative numbers correctly', () => {
    expect(formatCurrency(-250)).toBe('-$250.00');
  });
});
