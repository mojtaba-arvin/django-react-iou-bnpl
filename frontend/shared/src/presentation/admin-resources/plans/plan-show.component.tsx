import {
  Show,
  SimpleShowLayout,
  TextField,
  DateField,
  FunctionField,
  ArrayField,
  Datagrid,
  NumberField,
  useRecordContext,
  Labeled,
  useTranslate,
} from 'react-admin';
import type { ShowProps } from 'react-admin';
import { Box, Chip, Typography, LinearProgress } from '@mui/material';
import type { ChipProps } from '@mui/material';
import type { BaseInstallment } from '../../../domain/installment/entities/installment.entities';
import { formatCurrency } from '../../../utils/currency-formatter.util';
import { useGlobalSettings } from '../../../infrastructure/context/global-settings.context';

const statusColors: Record<string, ChipProps['color']> = {
  // installment plan
  active: 'success',
  completed: 'info',
  defaulted: 'error',
  // installment
  pending: 'info',
  paid: 'success',
  late: 'warning',
  failed: 'error',
};

const PlanTitle = () => {
  const record = useRecordContext<{
    id?: string | number;
    template_plan?: { name?: string };
  }>();
  const translate = useTranslate();

  return record ? (
    <Typography variant="h5">
      {translate('Plan')} #{record.id} - {record.template_plan?.name}
    </Typography>
  ) : null;
};

const ProgressBar = ({ value }: { value: number }) => {
  const percentage = Math.floor(value * 100) / 100;
  return (
    <Box display="flex" alignItems="center">
      <Box width="100%" mr={1}>
        <LinearProgress variant="determinate" value={value} />
      </Box>
      <Box minWidth={35}>
        <Typography
          variant="body2"
          color="textSecondary"
        >{`${percentage}%`}</Typography>
      </Box>
    </Box>
  );
};

interface PlanShowProps extends ShowProps {
  showCustomerEmail?: boolean;
}

export const PlanShow = ({ showCustomerEmail = false }: PlanShowProps) => {
  const translate = useTranslate();
  const { currency, locale } = useGlobalSettings();

  return (
    <Show title={<PlanTitle />}>
      <SimpleShowLayout>
        <TextField source="id" label={translate('ID')} />

        <FunctionField
          label={translate('Plan Name')}
          render={(record: { template_plan?: { name?: string } }) => record.template_plan?.name}
        />

        <DateField source="start_date" label={translate('Start Date')} />

        <FunctionField
          label={translate('Status')}
          render={(record: { status: keyof typeof statusColors }) => (
            <Chip
              label={record.status}
              color={statusColors[record.status] || 'default'}
              onClick={(e) => e.stopPropagation()}
            />
          )}
        />

        <Labeled label={translate('Progress')}>
          <FunctionField
            render={(record: { progress: { paid: number; total: number; percentage: number } }) => (
              <Box>
                <Typography variant="body1">
                  {record.progress.paid}/{record.progress.total}{' '}
                  {translate('installments paid')}
                </Typography>
                <ProgressBar value={record.progress.percentage} />
              </Box>
            )}
          />
        </Labeled>

        <FunctionField
          label={translate('Total Amount')}
          render={(record: { template_plan?: { total_amount?: string } }) =>
            `${parseFloat(record.template_plan?.total_amount ?? '0').toLocaleString(
              locale,
              {
                style: 'currency',
                currency: currency,
              }
            )}`
          }
        />

        <FunctionField
          label={translate('Installment Details')}
          render={(record: { template_plan?: { installment_count?: number; installment_period?: number } }) => (
            <Typography>
              {record.template_plan?.installment_count} ×{' '}
              {translate('installments')}
              {translate(', every')} {record.template_plan?.installment_period}{' '}
              {translate('days')}
            </Typography>
          )}
        />

        <FunctionField
          label={translate('Next Due Date')}
          render={(record: { progress: { next_due_date?: string } }) =>
            record.progress.next_due_date ? (
              <DateField source="progress.next_due_date" showTime={false} />
            ) : (
              <Typography>-</Typography>
            )
          }
        />

        <FunctionField
          label={translate('Days Remaining')}
          render={(record: { progress: { days_remaining?: number } }) =>
            record.progress.days_remaining ? (
              <NumberField source="progress.days_remaining" />
            ) : (
              <Typography>-</Typography>
            )
          }
        />

        {showCustomerEmail && (
          <TextField
            source="customer_email"
            label={translate('Customer Email')}
            sortable={false}
          />
        )}

        <ArrayField source="installments" label={translate('Installments')}>
          <Datagrid bulkActionButtons={false} rowClick={false}>
            <NumberField source="sequence_number" label={translate('#')} />

            <DateField
              source="due_date"
              label={translate('Due Date')}
              showTime={false}
            />

            <FunctionField
              label={translate('Amount')}
              render={(record: BaseInstallment) =>
                formatCurrency(record.amount, currency, locale, {
                  invalidAmountMessage: translate('Invalid amount'),
                })
              }
            />

            <DateField
              source="paid_at"
              label={translate('Paid At')}
              showTime={true}
            />

            <FunctionField
              label={translate('Status')}
              render={(record: BaseInstallment) => (
                <Chip
                  label={record.status}
                  color={statusColors[record.status] || 'default'}
                  size="small"
                  onClick={(e) => e.stopPropagation()}
                />
              )}
            />
          </Datagrid>
        </ArrayField>
      </SimpleShowLayout>
    </Show>
  );
};
