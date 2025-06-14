export interface RegisterPayload {
  email: string;
  password: string;
  user_type: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface LoginParams {
  username: string;
  password: string;
  user_type?: string;
}
