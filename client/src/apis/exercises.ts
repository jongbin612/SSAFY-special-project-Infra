import apiClient from '@apis/apiClient';
import type { Exercise, postSessionResponse, SessionDetailResponse } from '@/types/exercise';

// 서버가 image를 절대 URL로 내려준다고 했으니 그대로 반환
export async function getExercises(): Promise<Exercise[]> {
  const { data } = await apiClient.get<Exercise[]>('/exercises/');
  return data;
}

export async function getExerciseDetail(exerciseId: string): Promise<Exercise> {
  const { data } = await apiClient.get<Exercise>(`/exercises/${exerciseId}`);
  return data;
}

export async function postSession(
  exerciseId: number,
  level: number = 1,
): Promise<postSessionResponse> {
  const { data } = await apiClient.post<postSessionResponse>(`/workouts/start`, {
    exercise_id: exerciseId,
    level,
  });
  return data;
}

export async function getSessionDetail(sessionId: string): Promise<SessionDetailResponse> {
  const { data } = await apiClient.get<SessionDetailResponse>(`/workouts/${sessionId}`);
  return data;
}
