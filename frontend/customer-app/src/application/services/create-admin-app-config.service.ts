import type { RemoteAppSetup, AdminAppOptions } from '@bnpl/shared';
import { createAdminAppConfig } from '@bnpl/shared';
import { InstallmentList } from '../../presentation/components/installment-list.component';
import { default as PlanList } from '../../presentation/components/plan-list.component';
import { default as PlanShow } from '../../presentation/components/plan-show.component';

export default ({ onBack, basename = '' }: RemoteAppSetup) =>
  createAdminAppConfig({
    onBack,
    basename,
    userType: 'customer',
    resources: [
      {
        name: 'installments',
        list: InstallmentList,
        props: { options: {} },
      },
      {
        name: 'plans',
        list: PlanList,
        show: PlanShow,
        props: { options: { label: 'Installment Plans' } },
      },
    ],
  } as AdminAppOptions);
