import axios, { type AxiosError, type AxiosResponse } from 'axios';
import useUserStore from '@/stores/userStore';
import { toast } from 'sonner';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 10000,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request 인터셉터: 매 요청마다 최신 토큰 설정
apiClient.interceptors.request.use(
  (config) => {
    const token = useUserStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// Response 인터셉터: 에러 처리 및 토큰 만료 처리
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    const errorData = error.response?.data as { detail?: string } | undefined;

    if (error.response?.status === 403) {
      toast.error(errorData?.detail || '토큰이 만료되었습니다. 다시 로그인해주세요.');
      useUserStore.getState().logout();
    } else if (error.response?.status === 401) {
      toast.error(errorData?.detail || '이메일 또는 비밀번호가 올바르지 않습니다.');
    } else if (error.response?.status === 404) {
      toast.error(errorData?.detail || '존재하지 않는 리소스입니다.');
    } else if (error.response?.status === 422) {
      toast.error(errorData?.detail || '잘못된 요청입니다.');
    } else if (error.response?.status === 500) {
      toast.error(errorData?.detail || '서버 오류가 발생했습니다.');
    } else {
      if (typeof errorData?.detail === 'string') {
        toast.error(errorData?.detail);
      } else {
        toast.error('오류가 발생했습니다.');
      }
    }
    return Promise.reject(error);
  },
);

export default apiClient;
