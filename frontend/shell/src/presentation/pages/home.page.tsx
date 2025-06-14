import { PublicLayout, useGlobalSettings } from '@bnpl/shared';
import { useTranslate } from 'react-admin';
import { Box, Button, Card, CardContent, Typography } from '@mui/material';

export const HomePage = ({ isMobile }: { isMobile: boolean }) => {
  const translate = useTranslate();
  const { customerBasePath, merchantBasePath, loginPath } =
    useGlobalSettings();

  return (
    <PublicLayout isMobile={isMobile}>
      <Card sx={{ borderRadius: 2, boxShadow: 3 }}>
        <CardContent sx={{ textAlign: 'center', py: { xs: 3, sm: 4 } }}>
          <Typography
            variant="h4"
            gutterBottom
            sx={{ mb: { xs: 3, sm: 4 }, fontWeight: 600 }}
          >
            {translate('Welcome to BNPL Platform')}
          </Typography>
          <Typography
            variant="body1"
            sx={{
              mb: { xs: 4, sm: 5 },
              fontSize: { xs: '0.9rem', sm: '1rem' },
            }}
          >
            {translate('Please select your account type to continue')}
          </Typography>

          <Box
            sx={{
              display: 'flex',
              flexDirection: { xs: 'column', sm: 'row' },
              justifyContent: 'center',
              gap: 2,
            }}
          >
            <Button
              variant="contained"
              size={isMobile ? 'medium' : 'large'}
              fullWidth={isMobile}
              href={`${customerBasePath}${loginPath}`}
              sx={{ minWidth: { sm: 200 }, py: { xs: 1.5, sm: 2 } }}
            >
              {translate('I\'m a Customer')}
            </Button>

            <Button
              variant="outlined"
              size={isMobile ? 'medium' : 'large'}
              fullWidth={isMobile}
              href={`${merchantBasePath}${loginPath}`}
              sx={{ minWidth: { sm: 200 }, py: { xs: 1.5, sm: 2 } }}
            >
              {translate('I\'m a Merchant')}
            </Button>
          </Box>
        </CardContent>
      </Card>
    </PublicLayout>
  );
};
