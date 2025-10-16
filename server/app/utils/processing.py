# utils/processing.py

import numpy as np


def preprocess_pushup(keypoints):
    try:
        if not keypoints or len(keypoints) < 33:
            print(f"Invalid keypoints length: {len(keypoints) if keypoints else 0}")
            return None

        idx = [0, 2, 6, 7, 8, 11, 12, 13, 14, 15, 16] + list(range(23, 33))

        data = []
        for i in idx:
            if i < len(keypoints):
                try:
                    # keypoints[i]는 [x, y, z, visibility] 리스트
                    point = keypoints[i]
                    data.extend([float(point[0]), float(point[1]), float(point[2])])  # x, y, z만 사용
                except Exception as point_error:
                    print(f"Error processing keypoint {i}: {point_error}")
                    data.extend([0.0, 0.0, 0.0])
            else:
                data.extend([0.0, 0.0, 0.0])

        # 21개 포인트 * 3차원 = 63
        arr = np.array([data], dtype=np.float32)
        return arr

    except Exception as e:
        print(f"Preprocessing error: {e}")
        return None


def preprocess_squat(keypoints):
    """스쿼트용 전처리"""
    indices = [0, 2, 6, 7, 8, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32]

    data = []
    for i in indices:
        point = keypoints[i]
        data.extend([float(point[0]), float(point[1]), float(point[2])])

    return np.array([data], dtype=np.float32)


def preprocess_situp(keypoints):
    """싯업용 전처리"""
    # 임시로 푸쉬업 전처리 사용
    return preprocess_pushup(keypoints)


def preprocess(keypoints, exercise_type: str = "pushup"):
    """운동 타입에 따른 전처리 선택"""
    if exercise_type == "pushup" or exercise_type == "푸쉬업":
        return preprocess_pushup(keypoints)
    elif exercise_type == "squat" or exercise_type == "스쿼트":
        return preprocess_squat(keypoints)
    elif exercise_type == "situp" or exercise_type == "싯업":
        return preprocess_situp(keypoints)
    else:
        # 기본값으로 푸쉬업 전처리 사용
        return preprocess_pushup(keypoints)
