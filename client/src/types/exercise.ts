export interface Exercise {
  exercise_id: number;
  name: string;
  calorie: number;
  calorie_description: string;
  thumbnail_url: string;
  target_image_url: string;
  howto_image_url: string;
  category: Category;
  levels: Level[];
}

export interface Category {
  category_id: number;
  name: string;
}

export interface Level {
  level_id: number;
  level: number;
  target_sets: number;
  target_reps: number;
  rest_seconds: number;
  experience_points: number;
  is_locked: boolean;
  is_completed: boolean;
}

export interface postSessionResponse {
  message: string;
  session_id: number;
}

export interface SessionDetail {
  session_id: number;
  user_id: number;
  exercise_id: number;
  level_id: number;
  status: string;
  current_set: number;
  current_set_reps: number;
  total_reps_completed: number;
  total_reps_failed: number;
  total_calories_burned: number;
  duration_seconds: number;
  start_time: string;
  end_time: string | null;
  last_pause_time: string | null;
  total_pause_duration: number;
  exercise: Exercise;
  level: Level;
}

export interface SocketInfo {
  socket_session_id: string;
  websocket_url: string;
  connection_status: string;
}

export interface SessionDetailResponse {
  message: string;
  session: SessionDetail;
  socket_info: SocketInfo;
}

export interface exerciseMessage {
  type: string;
  data: {
    failed_detected: boolean;
    rep_detected: boolean;
    set_completed: boolean;
    workout_completed: boolean;
    feedback_message: string;
    session: SessionDetail;
  };
}
