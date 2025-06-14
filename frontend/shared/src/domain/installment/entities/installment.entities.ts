export interface BaseInstallment {
  id: number;
  amount: string;
  due_date: string;
  status: 'pending' | 'paid' | 'late' | 'failed';
  sequence_number: number;
  paid_at: string | null;
}
