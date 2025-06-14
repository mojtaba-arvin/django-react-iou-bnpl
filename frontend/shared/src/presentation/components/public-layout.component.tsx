import { ReactNode } from 'react';
import { Box, Container, CssBaseline } from '@mui/material';

interface PublicLayoutProps {
  children: ReactNode;
  isMobile?: boolean;
}

export const PublicLayout = ({ children, isMobile }: PublicLayoutProps) => (
  <Container
    maxWidth="sm"
    sx={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      minHeight: '100vh',
      p: isMobile ? 2 : 3,
    }}
  >
    <CssBaseline />
    <Box sx={{ width: '100%' }}>{children}</Box>
  </Container>
);
