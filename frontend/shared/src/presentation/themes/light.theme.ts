import { defaultTheme } from 'react-admin';
import { createTheme } from '@mui/material/styles';

export const lightTheme = createTheme({
  ...defaultTheme,
  palette: {
    mode: 'light',
    primary: {
      main: '#ce7500',
    },
    secondary: {
      main: '#4a4a4a',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
  },
});
