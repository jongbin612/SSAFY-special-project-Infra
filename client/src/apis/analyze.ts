import apiClient from '@apis/apiClient';
import type { BodyAnalysisResponse } from '@/types/analyze';

export const postBodyAnalysis = async (image: File) => {
  const formData = new FormData();
  formData.append('file', image);
  const response = await apiClient.post<BodyAnalysisResponse>('/analysis/types', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};
