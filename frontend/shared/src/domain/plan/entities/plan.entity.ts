import type { RaRecord } from 'react-admin';
import { BaseInstallment } from '../../installment/entities/installment.entities';

export interface Plan extends RaRecord {
  id: number; // InstallmentPlan Model id
  start_date: string;
  status: 'active' | 'completed' | 'defaulted'; // InstallmentPlan Model status
  template_plan: {
    id: number;
    name: string;
    total_amount: string;
    installment_count: number;
    installment_period: number;
  };
  progress: {
    paid: number;
    total: number;
    percentage: number;
    next_due_date: string;
    days_remaining: number;
  };
  installments: BaseInstallment[];
}
