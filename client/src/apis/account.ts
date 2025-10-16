import apiClient from '@apis/apiClient';
import { type User, type LoginResponse } from '@/types/accountsType';

// 인증 관련 API

// 이메일 로그인
export const login = async (email: string, password: string): Promise<LoginResponse> => {
  const response = await apiClient.post<LoginResponse>('/auth/login/email', {
    email,
    password,
  });
  return response.data;
};

// 사용자 관련 API
// 내 정보 조회
export const me = async (): Promise<User> => {
  const response = await apiClient.get<User>('/users/me');
  return response.data;
};

export const signUp = async (
  email: string,
  password: string,
  name: string,
  birth_date: string,
  gender: string,
  height: string,
  weight: string,
): Promise<User> => {
  const response = await apiClient.post<User>('/auth/signup/email', {
    email,
    password,
    name,
    birth_date,
    gender,
    height: parseInt(height),
    weight: parseInt(weight),
  });
  return response.data;
};
