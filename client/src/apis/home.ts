// client/src/apis/home.ts
import apiClient from '@apis/apiClient';
import type { Exercise } from '@/types/exercise';

export interface HomeFeed {
  recent: Exercise[];
  hot: Exercise[];
}

export async function getHomeFeed(): Promise<HomeFeed> {
  const { data } = await apiClient.get<HomeFeed>('/home/'); // 실제 경로에 맞게 변경
  return data;
}
