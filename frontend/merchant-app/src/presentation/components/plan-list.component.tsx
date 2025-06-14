import { PlanList } from '@bnpl/shared';

export default (props: React.ComponentProps<typeof PlanList>) => (
  <PlanList showCreateButton showCustomerEmail {...props} />
);
