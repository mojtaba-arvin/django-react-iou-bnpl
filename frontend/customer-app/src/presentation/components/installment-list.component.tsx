import {
  List,
  Datagrid,
  TextField,
  NumberField,
  FunctionField,
  SelectInput,
  Pagination,
  useListContext,
  LinearProgress,
  useTranslate,
} from 'react-admin';
import { Chip } from '@mui/material';
import type { ChipProps } from '@mui/material';
import {
  FormattedDateTimeField,
  CustomerFacingInstallment,
  useGlobalSettings,
} from '@bnpl/shared';
import { PayButton } from './pay-button.component';

const statusColors: Record<string, ChipProps['color']> = {
  pending: 'info',
  paid: 'success',
  late: 'warning',
  failed: 'error',
};

const InstallmentFilters = [
  <SelectInput
    key="status"
    source="status"
    label="Status"
    choices={[
      { id: 'all', name: 'All' },
      { id: 'upcoming', name: 'Upcoming' },
      { id: 'past', name: 'Past' },
    ]}
    alwaysOn
  />,
];

export const InstallmentListInner = () => {
  const { data: _data, isLoading } = useListContext<CustomerFacingInstallment>();
  const translate = useTranslate();
  const { currency, locale } = useGlobalSettings();

  if (isLoading) return <LinearProgress />;

  return (
    <Datagrid rowClick="show" bulkActionButtons={false}>
      <TextField source="id" sortable={false} />
      <FormattedDateTimeField
        source="due_date"
        label={translate('Due Date')}
        sortable={false}
        locale={locale}
        invalidDateMessage={translate('Invalid date')}
      />
      <NumberField
        source="amount"
        options={{
          style: 'currency',
          currency: currency,
          locale: locale,
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        }}
        label={translate('Amount')}
        sortable={false}
      />
      <FormattedDateTimeField
        source="paid_at"
        label={translate('Paid At')}
        sortable={false}
        locale={locale}
        invalidDateMessage={translate('Invalid date')}
      />
      <FunctionField
        source="status"
        label={translate('Status')}
        render={(record: CustomerFacingInstallment) => (
          <Chip
            label={translate(record.status)}
            color={statusColors[record.status.toLowerCase()] || 'default'}
            size="small"
            onClick={(e) => e.stopPropagation()}
          />
        )}
        sortable={false}
      />
      <FunctionField
        label={translate('Plan')}
        render={(record: CustomerFacingInstallment) => (
          <span>
            #{record.subscription_id} - {record.template_plan_name}
          </span>
        )}
        sortable={false}
      />
      <NumberField
        source="sequence_number"
        label={translate('Seq No.')}
        sortable={false}
      />
      <FunctionField
        label={translate('Actions')}
        render={(_record: CustomerFacingInstallment) => <PayButton />}
      />
    </Datagrid>
  );
};

export const InstallmentList = () => {
  return (
    <List
      filters={InstallmentFilters}
      pagination={<Pagination rowsPerPageOptions={[5, 10]} />}
      perPage={10}
      filterDefaultValues={{ status: 'all' }}
      storeKey={false}
    >
      <InstallmentListInner />
    </List>
  );
};
