export interface RegisterPageProps {
  loginPath: string;
  userType: 'customer' | 'merchant';
  isMobile?: boolean;
  onBack?: () => void;
}
