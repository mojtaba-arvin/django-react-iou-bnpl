export const maskEmail = (email: string): string => {
  const [username, domain] = email.split('@');
  if (!username || !domain) return email;

  // Show the first 3 characters of the username if possible, otherwise show as many as we have
  const visible = username.slice(0, 3);
  // Always mask with exactly 3 asterisks
  const maskedPart = '*'.repeat(3);

  return `${visible}${maskedPart}@${domain}`;
};
