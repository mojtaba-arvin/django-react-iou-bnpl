import { useState } from 'react';
import { useLogin, useNotify, Notification, useTranslate } from 'react-admin';
import {
  Box,
  Button,
  Card,
  CardContent,
  TextField,
  Typography,
  Link,
} from '@mui/material';
import { BackToHomeButton } from '../components/back-to-home-button.component';
import { LoginPageProps } from './login.types';
import { PublicLayout } from '../components/public-layout.component';

export const LoginPage: React.FC<LoginPageProps> = ({
  registerPath,
  userType,
  isMobile = false,
  onBack,
}) => {
  const translate = useTranslate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const login = useLogin();
  const notify = useNotify();

  const validate = () => {
    const newErrors: Record<string, string> = {};
    // no need yet
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) return;

    login({ username: email, password, user_type: userType }).catch(
      (error: { message?: string }) => {
        notify(error.message || translate('Invalid email or password'), {
          type: 'error',
        });
      }
    );
  };

  return (
    <PublicLayout isMobile={isMobile}>
      {onBack && <BackToHomeButton onClick={onBack} />}
      <Card
        sx={{
          borderRadius: 2,
          boxShadow: 3,
          border: '1px solid',
          borderColor: 'divider',
        }}
      >
        <CardContent
          sx={{
            textAlign: 'center',
            py: isMobile ? 3 : 4,
            px: isMobile ? 2 : 4,
          }}
        >
          <Typography
            variant='h4'
            gutterBottom
            sx={{
              mb: isMobile ? 3 : 4,
              fontWeight: 600,
              fontSize: isMobile ? '1.75rem' : '2.125rem',
            }}
          >
            {translate('Sign In')}
          </Typography>

          <form onSubmit={handleSubmit}>
            <Box sx={{ mb: isMobile ? 2.5 : 3 }}>
              <TextField
                fullWidth
                label={translate('Email')}
                type='email'
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                error={!!errors.email}
                helperText={errors.email}
                required
                variant='outlined'
                size={isMobile ? 'small' : 'medium'}
              />
            </Box>

            <Box sx={{ mb: isMobile ? 2.5 : 3 }}>
              <TextField
                fullWidth
                label={translate('Password')}
                type='password'
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                error={!!errors.password}
                helperText={errors.password}
                required
                variant='outlined'
                size={isMobile ? 'small' : 'medium'}
              />
            </Box>

            <Button
              fullWidth
              type='submit'
              variant='contained'
              size={isMobile ? 'medium' : 'large'}
              sx={{
                py: isMobile ? 1.5 : 2,
                mb: isMobile ? 2 : 3,
                borderRadius: 1,
                textTransform: 'none',
                fontWeight: 500,
              }}
            >
              {translate('Sign In')}
            </Button>

            <Typography
              variant='body2'
              sx={{
                color: 'text.secondary',
              }}
            >
              {translate('Don\'t have an account? ')}
              <Link
                href={registerPath}
                underline='hover'
                sx={{
                  cursor: 'pointer',
                  fontWeight: 500,
                }}
              >
                {translate('Sign up')}
              </Link>
            </Typography>
          </form>
        </CardContent>
      </Card>
      <Notification />
    </PublicLayout>
  );
};

export const createLoginPage = (props: LoginPageProps): React.FC => {
  return () => <LoginPage {...props} />;
};
