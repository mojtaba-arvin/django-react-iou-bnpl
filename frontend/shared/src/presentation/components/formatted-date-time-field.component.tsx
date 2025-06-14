import { FunctionField } from 'react-admin';

interface FormattedDateTimeFieldProps {
  source: string;
  label?: string;
  sortable?: boolean;
  locale?: string;
  invalidDateMessage?: string;
}

export const FormattedDateTimeField = ({
  source,
  label,
  sortable,
  locale = 'en-US',
  invalidDateMessage = 'Invalid date',
}: FormattedDateTimeFieldProps) => (
  <FunctionField
    source={source}
    label={label}
    sortable={sortable}
    render={(record: Record<string, unknown>) => {
      const raw = record && typeof record === 'object' ? (record as Record<string, unknown>)[source] : undefined;
      if (!raw) return '-';

      if (
        typeof raw !== 'string' &&
        typeof raw !== 'number' &&
        !(raw instanceof Date)
      ) {
        return invalidDateMessage;
      }
      const date = new Date(raw as string | number | Date);
      if (isNaN(date.getTime())) return invalidDateMessage;

      const dateFormatter = new Intl.DateTimeFormat(locale, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        timeZone: 'UTC',
      });

      const timeFormatter = new Intl.DateTimeFormat(locale, {
        hour: '2-digit',
        minute: '2-digit',
        hour12: true,
        timeZone: 'UTC',
      });

      return (
        <span>
          {dateFormatter.format(date)}
          <br />
          {timeFormatter.format(date)}
        </span>
      );
    }}
  />
);
