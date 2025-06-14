import type { ApiResponse } from '../../../domain/common/types/api-response.type';
import type { BaseInstallment } from '../../../domain/installment/entities/installment.entities';

// export interface CustomerFacingInstallment extends RaRecord {
export interface CustomerFacingInstallment extends BaseInstallment {
  subscription_id: number;
  template_plan_id: number;
  template_plan_name: string;
  is_payable: boolean;
}

export interface PaymentResponse
  extends ApiResponse<CustomerFacingInstallment> { }
