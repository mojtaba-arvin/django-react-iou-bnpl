import { useState } from 'react';
import { useNotify, Notification, useTranslate } from 'react-admin';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Card,
  CardContent,
  TextField,
  Typography,
  Link,
} from '@mui/material';
import type { RegisterPageProps } from './register.types';
import { apiClient } from '../../infrastructure/http/api-client.client';
import { BackToHomeButton } from '../components/back-to-home-button.component';
import { PublicLayout } from '../components/public-layout.component';

export const RegisterPage: React.FC<RegisterPageProps> = ({
  userType,
  loginPath,
  isMobile = false,
  onBack,
}) => {
  const translate = useTranslate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const notify = useNotify();
  const navigate = useNavigate();

  const validate = () => {
    const newErrors: Record<string, string> = {};

    if (!email) {
      newErrors.email = translate('Email is required');
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = translate('Email is invalid');
    }

    if (!password) {
      newErrors.password = translate('Password is required');
    } else if (password.length < 8) {
      newErrors.password = translate('Password must be at least 8 characters');
    }

    if (password !== confirmPassword) {
      newErrors.confirmPassword = translate('Passwords do not match');
    }

    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) {
      notify('ra.message.invalid_form', { type: 'error' });
      return;
    }

    try {
      await apiClient.register({ email, password, user_type: userType });
      notify(translate('Registration successful! Please log in.'), {
        type: 'success',
      });
      navigate(loginPath);
    } catch (error: unknown) {
      // react-admin HttpError
      const errorBody = (error as { body?: { errors?: Record<string, string>; message?: string } })?.body;
      if (errorBody?.errors) {
        setErrors((prev) => ({ ...prev, ...errorBody.errors }));
        // Use react-admin's default invalid form message

        notify('ra.message.invalid_form', { type: 'error' });
      } else {
        notify(errorBody?.message ?? translate('Registration failed'), { type: 'error' });
      }
    }
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
            variant="h4"
            gutterBottom
            sx={{
              mb: isMobile ? 3 : 4,
              fontWeight: 600,
              fontSize: isMobile ? '1.75rem' : '2.125rem',
            }}
          >
            {translate('Create Account')}
          </Typography>

          <form onSubmit={(e) => { void handleSubmit(e); }}>
            <Box sx={{ mb: isMobile ? 2.5 : 3 }}>
              <TextField
                fullWidth
                label={translate('Email')}
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                error={!!errors.email}
                helperText={errors.email}
                required
                variant="outlined"
                size={isMobile ? 'small' : 'medium'}
              />
            </Box>

            <Box sx={{ mb: isMobile ? 2.5 : 3 }}>
              <TextField
                fullWidth
                label={translate('Password')}
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                error={!!errors.password}
                helperText={errors.password}
                required
                variant="outlined"
                size={isMobile ? 'small' : 'medium'}
              />
            </Box>

            <Box sx={{ mb: isMobile ? 3 : 4 }}>
              <TextField
                fullWidth
                label={translate('Confirm Password')}
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                error={!!errors.confirmPassword}
                helperText={errors.confirmPassword}
                required
                variant="outlined"
                size={isMobile ? 'small' : 'medium'}
              />
            </Box>

            <Button
              fullWidth
              type="submit"
              variant="contained"
              size={isMobile ? 'medium' : 'large'}
              sx={{
                py: isMobile ? 1.5 : 2,
                mb: isMobile ? 2 : 3,
                borderRadius: 1,
                textTransform: 'none',
                fontWeight: 500,
              }}
            >
              {translate('Sign Up')}
            </Button>

            <Typography
              variant="body2"
              sx={{
                color: 'text.secondary',
              }}
            >
              {translate('Already have an account? ')}
              <Link
                href={loginPath}
                underline="hover"
                sx={{
                  cursor: 'pointer',
                  fontWeight: 500,
                }}
              >
                {translate('Sign in')}
              </Link>
            </Typography>
          </form>
        </CardContent>
      </Card>
      <Notification />
    </PublicLayout>
  );
};

export const createRegisterPage = (props: RegisterPageProps): React.FC => {
  return () => <RegisterPage {...props} />;
};
