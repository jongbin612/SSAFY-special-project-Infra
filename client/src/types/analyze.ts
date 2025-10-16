import type { Exercise } from './exercise';

export interface BodyAnalysisResponse {
  predicted_body_type: 'skinny' | 'ordinary' | 'overweight' | 'hulk';
  confidence: number;
  processing_time_seconds: number;
  message: string;
  recommendations: Exercise[];
  body_type_image_url: string;
}
