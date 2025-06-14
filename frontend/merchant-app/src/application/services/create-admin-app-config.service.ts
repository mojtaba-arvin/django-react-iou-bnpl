import { createAdminAppConfig } from '@bnpl/shared';
import type { RemoteAppSetup, AdminAppOptions } from '@bnpl/shared';
import { default as PlanList } from '../../presentation/components/plan-list.component';
import { default as PlanShow } from '../../presentation/components/plan-show.component';
import { Dashboard } from '../../presentation/components/dashboard.component';
import { PlanCreate } from '../../presentation/components/plan-create.component';

export default ({ onBack, basename = '' }: RemoteAppSetup) =>
  createAdminAppConfig({
    onBack,
    basename,
    userType: 'merchant',
    dashboard: Dashboard as React.ComponentType,
    resources: [
      {
        name: 'plans',
        list: PlanList as React.ComponentType,
        show: PlanShow as React.ComponentType,
        create: PlanCreate as React.ComponentType,
        props: { options: { label: 'Installment Plans' } },
      },
    ],
  } as AdminAppOptions);
