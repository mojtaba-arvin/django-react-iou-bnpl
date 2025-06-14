import React, { useEffect, useState } from 'react';
import { Title, useDataProvider, useTranslate } from 'react-admin';
import {
  Card,
  CardContent,
  Typography,
  Stack,
  Skeleton,
  useTheme,
  Box,
  LinearProgress,
} from '@mui/material';
import { DashboardMetrics } from '@bnpl/shared';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';

export const Dashboard: React.FC = () => {
  const translate = useTranslate();
  const dataProvider = useDataProvider();
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const theme = useTheme();

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setLoading(true);
        // Explicitly type the response from dataProvider
        const response = await (dataProvider.getDashboardMetrics as () => Promise<{ data: DashboardMetrics }>)();
        setMetrics(response.data);
        setError(null);
      } catch (_err) {
        setError(
          translate(
            'Failed to load dashboard metrics. Please try again later.'
          )
        );
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
  }, [dataProvider, translate]);

  if (loading) {
    return (
      <Box sx={{ width: '100%' }}>
        <Title title="Merchant Dashboard" />
        <Stack direction="row" spacing={2} flexWrap="wrap" sx={{ mt: 2 }}>
          {[1, 2, 3, 4].map((item) => (
            <Skeleton
              key={item}
              variant="rectangular"
              width={200}
              height={120}
              sx={{ borderRadius: 2, flex: '1 1 200px' }}
            />
          ))}
        </Stack>
        <LinearProgress sx={{ mt: 2 }} />
      </Box>
    );
  }

  if (error) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          height: '200px',
          color: theme.palette.error.main,
          textAlign: 'center',
        }}
      >
        <ErrorOutlineIcon sx={{ fontSize: 60, mb: 2 }} />
        <Typography variant="h6">{error}</Typography>
      </Box>
    );
  }

  if (!metrics) {
    return null;
  }

  const cards = [
    {
      label: translate('Total Revenue'),
      value: `$${metrics.total_revenue.toFixed(2)}`,
      color: theme.palette.primary.main,
    },
    {
      label: translate('Success Rate'),
      value: `${metrics.success_rate}%`,
      color: theme.palette.success.main,
    },
    {
      label: translate('Overdue Count'),
      value: metrics.overdue_count.toString(),
      color: theme.palette.warning.main,
    },
    {
      label: translate('Active Plans'),
      value: metrics.active_plans.toString(),
      color: theme.palette.info.main,
    },
  ];

  return (
    <Box sx={{ p: 2 }}>
      <Title title={translate('Merchant Dashboard')} />
      <Typography variant="h5" sx={{ mb: 3 }} gutterBottom>
        {translate('Overview')}
      </Typography>

      <Stack
        direction="row"
        spacing={3}
        flexWrap="wrap"
        useFlexGap
        sx={{
          '& > *': {
            flex: { xs: '1 1 100%', sm: '1 1 200px', md: '1' },
            minWidth: { xs: '100%', sm: '200px' },
          },
        }}
      >
        {cards.map((metric, index) => (
          <Card
            key={index}
            sx={{
              borderRadius: 2,
              boxShadow: theme.shadows[3],
              transition: 'transform 0.2s, box-shadow 0.2s',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: theme.shadows[6],
              },
            }}
          >
            <CardContent>
              <Typography
                variant="subtitle1"
                color="text.secondary"
                gutterBottom
                sx={{ fontWeight: 500 }}
              >
                {metric.label}
              </Typography>
              <Typography
                variant="h4"
                sx={{
                  fontWeight: 700,
                  color: metric.color,
                }}
              >
                {metric.value}
              </Typography>
            </CardContent>
          </Card>
        ))}
      </Stack>
    </Box>
  );
};
