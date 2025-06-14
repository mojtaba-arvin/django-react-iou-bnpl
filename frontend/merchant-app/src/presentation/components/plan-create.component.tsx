import { calculateInstallments } from '@bnpl/shared';
import { Box, Divider, Typography } from '@mui/material';
import React, { useEffect, useState } from 'react';
import {
  Create,
  SimpleForm,
  TextInput,
  NumberInput,
  DateInput,
  required,
  FormDataConsumer,
  useTranslate,
  email,
  AutocompleteInput,
  ReferenceInput,
} from 'react-admin';
import { Labeled } from 'ra-ui-materialui';

interface InstallmentPreview {
  sequence: number;
  amount: number;
  dueDate: string;
}

export const PlanCreate: React.FC = () => {
  const translate = useTranslate();
  const [installmentPreview, setInstallmentPreview] = useState<InstallmentPreview[]>([]);

  return (
    <Create>
      <SimpleForm>
        <FormDataConsumer>
          {({ formData }) => {
            useEffect(() => {
              if (
                formData.total_amount > 0 &&
                formData.installment_count > 0 &&
                formData.installment_period > 0 &&
                formData.start_date
              ) {
                const preview = calculateInstallments(
                  formData.total_amount.toString(),
                  formData.installment_count,
                  formData.installment_period,
                  formData.start_date
                );
                setInstallmentPreview(
                  preview.map(item => ({
                    ...item,
                    amount: Number(item.amount),
                  }))
                );
              } else {
                setInstallmentPreview([]);
              }
            }, [formData.total_amount, formData.installment_count, formData.installment_period, formData.start_date]);

            return null;
          }}
        </FormDataConsumer>

        <TextInput
          source="name"
          label={translate('Plan Name')}
          validate={[required()]}
          fullWidth
        />
        <NumberInput
          source="total_amount"
          label={translate('Total Amount')}
          validate={[required()]}
          min={1}
          fullWidth
        />
        <NumberInput
          source="installment_count"
          label={translate('Installment Count')}
          validate={[required()]}
          fullWidth
          min={1}
          max={36}
        />
        <NumberInput
          source="installment_period"
          label={translate('Installment Period (days)')}
          fullWidth
          min={1}
          max={365}
          defaultValue={30}
        />
        <ReferenceInput
          source="customer_email"
          label={translate('Customer Email')}
          reference="customers/eligible"
          perPage={10}
          filterToQuery={(searchText: string) => ({ email: searchText })}
        >
          <Labeled>
            <AutocompleteInput
              source="customer_email"
              optionText="email"
              optionValue="email"
              validate={[required(), email()]}
              fullWidth
            />
          </Labeled>
        </ReferenceInput>
        <DateInput
          source="start_date"
          label={translate('Start Date (First Installment Date)')}
          defaultValue={new Date().toISOString().split('T')[0]}
          fullWidth
        />

        {installmentPreview.length > 0 && (
          <Box mt={2} sx={{ border: '1px solid #eee', borderRadius: '4px', p: 2 }}>
            <Typography variant="h6" gutterBottom>
              {translate('Installment Preview')}
            </Typography>
            <Divider sx={{ my: 1 }} />
            <Box>
              {installmentPreview.map((item) => (
                <Box
                  key={item.sequence}
                  mb={1}
                  pb={1}
                  sx={{ borderBottom: '1px solid #f5f5f5' }}
                >
                  <Typography variant="body1">
                    <strong>
                      {translate('Installment')} #{item.sequence}:
                    </strong>
                  </Typography>
                  <Typography variant="body2">
                    {translate('Amount')}: ${item.amount}
                  </Typography>
                  <Typography variant="body2">
                    {translate('Due Date')}: {item.dueDate}
                  </Typography>
                </Box>
              ))}
            </Box>
          </Box>
        )}
      </SimpleForm>
    </Create>
  );
};