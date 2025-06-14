import {
  Button,
  useNotify,
  useRefresh,
  useRecordContext,
  useTranslate,
} from 'react-admin';
import { useDataProvider, DataProvider } from 'react-admin';
import { useState } from 'react';
import { CustomerFacingInstallment } from '@bnpl/shared';

type CustomDataProvider = DataProvider & {
  payInstallment: (id: CustomerFacingInstallment['id']) => Promise<void>;
};

export const PayButton = () => {
  const translate = useTranslate();
  const record = useRecordContext<CustomerFacingInstallment>();
  const dataProvider = useDataProvider() as CustomDataProvider;
  const notify = useNotify();
  const refresh = useRefresh();
  const [loading, setLoading] = useState(false);

  if (!record) return null;

  const handlePay = async () => {
    setLoading(true);
    try {
      await dataProvider.payInstallment(record.id);
      notify(translate('Installment paid successfully'), { type: 'success' });
      refresh();
    } catch (error: unknown) {
      const message =
        error instanceof Error
          ? error.message
          : translate('Failed to process payment');
      notify(message, {
        type: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Button
      label={translate('Pay Now')}
      onClick={() => { handlePay(); }}
      disabled={!record.is_payable || loading}
      color="primary"
      variant="contained"
      size="small"
    />
  );
};
