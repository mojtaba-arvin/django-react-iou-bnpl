// Calculate installment preview using integer arithmetic for cents
export const calculateInstallments = (
  totalAmount: string,
  count: number,
  period: number,
  startDate: string
) => {
  if (!totalAmount || !count || !period || !startDate) return [];

  const total = parseFloat(totalAmount);
  if (total <= 0 || count <= 0) return [];

  // Convert to cents to avoid floating point errors
  const totalCents = Math.round(total * 100);
  const baseCents = Math.floor(totalCents / count);
  const remainder = totalCents % count; // Extra cents to distribute

  const installments = [];
  const start = new Date(startDate);

  for (let seq = 1; seq <= count; seq++) {
    // Add extra cent to first 'remainder' installments
    const cents = baseCents + (seq <= remainder ? 1 : 0);
    const amount = cents / 100;

    const dueDate = new Date(start);
    dueDate.setDate(dueDate.getDate() + period * (seq - 1));

    installments.push({
      sequence: seq,
      amount: amount.toFixed(2),
      dueDate: dueDate.toISOString().split('T')[0],
    });
  }

  return installments;
};
