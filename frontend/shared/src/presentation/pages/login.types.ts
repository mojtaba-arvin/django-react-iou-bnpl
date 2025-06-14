export interface LoginPageProps {
  registerPath: string;
  userType: 'customer' | 'merchant';
  isMobile?: boolean;
  onBack?: () => void;
}
