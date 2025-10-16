export interface User {
  user_id: number;
  email: string;
  name: string;
  profile_image_url: string;
  birth_date: string;
  gender: string;
  height: number;
  weight: number;
  created_at: string;
}

export interface LoginResponse {
  user: User;
  access_token: string;
  token_type: string;
}

// API 에러 응답 타입
export interface ApiError {
  message: string;
  code: string;
  details?: Record<string, unknown>;
}

// API 응답 래퍼 타입
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}
