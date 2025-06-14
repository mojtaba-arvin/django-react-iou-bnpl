import { Button } from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { useTranslate } from 'react-admin';

interface HomeButtonProps {
  onClick: () => void;
}

export const BackToHomeButton = ({ onClick }: HomeButtonProps) => {
  const translate = useTranslate();
  return (
    <Button
      startIcon={<ArrowBackIcon />}
      onClick={onClick}
      sx={{
        mb: 2,
        alignSelf: 'flex-start',
        textTransform: 'none',
        color: 'text.secondary',
        '&:hover': {
          color: 'text.primary',
        },
      }}
    >
      {translate('Home')}
    </Button>
  );
};
