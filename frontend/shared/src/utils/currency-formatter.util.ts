export const formatCurrency = (
  amount: number | string | undefined | null,
  currency: string = 'USD',
  locale: string = 'en-US',
  options?: {
    invalidAmountMessage?: string;
  }
): string => {
  if (amount === null || amount === undefined || isNaN(Number(amount))) {
    return options?.invalidAmountMessage || '-';
  }
  try {
    return Number(amount).toLocaleString(locale, {
      style: 'currency',
      currency,
    });
  } catch {
    return options?.invalidAmountMessage || '-';
  }
};
