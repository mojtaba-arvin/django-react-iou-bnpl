import {
  List,
  Datagrid,
  TextField,
  NumberField,
  FunctionField,
  DateField,
  Pagination,
  useListContext,
  LinearProgress as RaLinearProgress,
  useTranslate,
  TopToolbar,
  CreateButton,
} from 'react-admin';
import type { ShowProps } from 'react-admin';
import { Chip, LinearProgress, Box, Typography } from '@mui/material';
import type { ChipProps } from '@mui/material';
import type { Plan } from '../../../domain/plan/entities/plan.entity';

const statusColors: Record<string, ChipProps['color']> = {
  active: 'success',
  completed: 'info',
  cancelled: 'error',
};

const ProgressBarField = ({ record }: { record?: Plan }) => {
  if (!record) return null;

  const percentage = parseFloat(record.progress.percentage.toFixed(2));

  return (
    <Box display="flex" alignItems="center">
      <Box width="100%" mr={1}>
        <LinearProgress variant="determinate" value={percentage} />
      </Box>
      <Box minWidth={35}>{percentage}%</Box>
    </Box>
  );
};

interface PlanListProps extends ShowProps {
  showCreateButton?: boolean;
  showCustomerEmail?: boolean;
}

export const PlanList = ({
  showCreateButton = false,
  showCustomerEmail = false,
}: PlanListProps) => {
  const translate = useTranslate();
  const ListActions = () => (
    <TopToolbar>
      <CreateButton label={translate('Create Plan')} />
    </TopToolbar>
  );

  const PlanListInner = () => {
    const { isLoading } = useListContext<Plan>();

    if (isLoading) return <RaLinearProgress />;

    return (
      <Datagrid rowClick="show" bulkActionButtons={false}>
        <TextField source="id" sortable={false} />
        <FunctionField
          label={translate('Plan')}
          render={(record: Plan) => record.template_plan.name}
        />
        <DateField
          source="start_date"
          label={translate('Start Date')}
          sortable={false}
        />
        <FunctionField
          label={translate('Status')}
          render={(record: Plan) => (
            <Chip
              label={record.status}
              color={statusColors[record.status] || 'default'}
            />
          )}
        />
        <FunctionField
          label={translate('Progress')}
          render={(record: Plan) => (
            <div>
              {record.progress.paid}/{record.progress.total} installments
              <ProgressBarField record={record} />
            </div>
          )}
        />
        <FunctionField
          label={translate('Next Due Date')}
          render={(record: Plan) =>
            record.progress.next_due_date ? (
              <DateField source="progress.next_due_date" showTime={false} />
            ) : (
              <Typography>-</Typography>
            )
          }
        />
        <FunctionField
          label={translate('Days Remaining')}
          render={(record: Plan) =>
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
            label={translate('Email')}
            sortable={false}
          />
        )}
      </Datagrid>
    );
  };

  return (
    <List
      resource="plans"
      pagination={<Pagination rowsPerPageOptions={[5, 10]} />}
      perPage={10}
      actions={showCreateButton ? <ListActions /> : undefined}
    >
      <PlanListInner />
    </List>
  );
};
