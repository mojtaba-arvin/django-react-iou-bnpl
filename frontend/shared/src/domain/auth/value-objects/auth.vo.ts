export interface Tokens {
  access: string;
  refresh: string;
}

export interface JwtDecoded {
  user_type: string;
  email: string;
  exp: number;
  iat: number;
  jti: string;
  token_type: string;
}
