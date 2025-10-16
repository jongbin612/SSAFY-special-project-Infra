# app/core/init_db.py

from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.core.database import Base, engine
from app.models.exercise import ExerciseModel
from app.models.exercise_category import ExerciseCategoryModel
from app.models.exercise_level import ExerciseLevelModel
from app.models.user import UserModel

settings = get_settings()


def init_db():
    """데이터베이스 초기화"""
    # 모든 테이블 생성
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


def init_sample_data():
    """샘플 데이터 초기화"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # 운동 카테고리
        categories_data = [
            {"name": "가슴"},
            {"name": "등"},
            {"name": "어깨"},
            {"name": "하체"},
            {"name": "복근"},
        ]

        created_categories = {}
        for category_data in categories_data:
            # 중복 확인
            existing = (
                db.query(ExerciseCategoryModel).filter(ExerciseCategoryModel.name == category_data["name"]).first()
            )

            if not existing:
                category = ExerciseCategoryModel(name=category_data["name"])
                db.add(category)
                db.flush()  # ID 생성을 위해 flush
                created_categories[category_data["name"]] = category.category_id
                print(f"Created category: {category_data['name']} (ID: {category.category_id})")
            else:
                created_categories[category_data["name"]] = existing.category_id
                print(f"Category already exists: {category_data['name']} (ID: {existing.category_id})")

        db.commit()

        exercises_data = [
            {
                "name": "푸시업",
                "calorie": 4.5,
                "category": "가슴",
                "thumbnail_url": settings.static_url + "images/exercises/pushup/thumbnail.png",
                "target_image_url": settings.static_url + "images/exercises/pushup/target.png",
                "howto_image_url": settings.static_url + "images/exercises/pushup/howto.png",
            },
            {
                "name": "스쿼트",
                "calorie": 6.0,
                "category": "하체",
                "thumbnail_url": settings.static_url + "images/exercises/squat/thumbnail.png",
                "target_image_url": settings.static_url + "images/exercises/squat/target.png",
                "howto_image_url": settings.static_url + "images/exercises/squat/howto.png",
            },
            {
                "name": "플랭크",
                "calorie": 3.0,
                "category": "복근",
                "thumbnail_url": settings.static_url + "images/exercises/plank/thumbnail.png",
                "target_image_url": settings.static_url + "images/exercises/plank/target.png",
                "howto_image_url": settings.static_url + "images/exercises/plank/howto.png",
            },
            {
                "name": "풀업",
                "calorie": 8.0,
                "category": "등",
                "thumbnail_url": settings.static_url + "images/exercises/pullup/thumbnail.png",
                "target_image_url": settings.static_url + "images/exercises/pullup/target.png",
                "howto_image_url": settings.static_url + "images/exercises/pullup/howto.png",
            },
            {
                "name": "런지",
                "calorie": 5.5,
                "category": "하체",
                "thumbnail_url": settings.static_url + "images/exercises/lunge/thumbnail.png",
                "target_image_url": settings.static_url + "images/exercises/lunge/target.png",
                "howto_image_url": settings.static_url + "images/exercises/lunge/howto.png",
            },
            {
                "name": "딥스",
                "calorie": 6.5,
                "category": "가슴",
                "thumbnail_url": settings.static_url + "images/exercises/dips/thumbnail.png",
                "target_image_url": settings.static_url + "images/exercises/dips/target.png",
                "howto_image_url": settings.static_url + "images/exercises/dips/howto.png",
            },
            {
                "name": "덤벨 로우",
                "calorie": 4.0,
                "category": "등",
                "thumbnail_url": settings.static_url + "images/exercises/dumbbell-row/thumbnail.png",
                "target_image_url": settings.static_url + "images/exercises/dumbbell-row/target.png",
                "howto_image_url": settings.static_url + "images/exercises/dumbbell-row/howto.png",
            },
            {
                "name": "덤벨 숄더 프레스",
                "calorie": 5.0,
                "category": "어깨",
                "thumbnail_url": settings.static_url + "images/exercises/dumbbell-shoulder-press/thumbnail.png",
                "target_image_url": settings.static_url + "images/exercises/dumbbell-shoulder-press/target.png",
                "howto_image_url": settings.static_url + "images/exercises/dumbbell-shoulder-press/howto.png",
            },
            {
                "name": "덤벨 래터럴 레이즈",
                "calorie": 3.5,
                "category": "어깨",
                "thumbnail_url": settings.static_url + "images/exercises/dumbbell-lateral-raise/thumbnail.png",
                "target_image_url": settings.static_url + "images/exercises/dumbbell-lateral-raise/target.png",
                "howto_image_url": settings.static_url + "images/exercises/dumbbell-lateral-raise/howto.png",
            },
            {
                "name": "Ab 휠 롤아웃",
                "calorie": 7.0,
                "category": "복근",
                "thumbnail_url": settings.static_url + "images/exercises/ab-wheel-rollout/thumbnail.png",
                "target_image_url": settings.static_url + "images/exercises/ab-wheel-rollout/target.png",
                "howto_image_url": settings.static_url + "images/exercises/ab-wheel-rollout/howto.png",
            },
        ]

        created_exercises = []
        for i, exercise_data in enumerate(exercises_data, 1):
            existing = db.query(ExerciseModel).filter(ExerciseModel.name == exercise_data["name"]).first()

            if not existing:
                category_id = created_categories[exercise_data["category"]]
                exercise = ExerciseModel(
                    name=exercise_data["name"],
                    calorie=exercise_data["calorie"],
                    category_id=category_id,
                    thumbnail_url=exercise_data["thumbnail_url"],
                    target_image_url=exercise_data["target_image_url"],
                    howto_image_url=exercise_data["howto_image_url"],
                )
                db.add(exercise)
                db.flush()
                created_exercises.append(exercise)
                print(
                    f"Created exercise: {exercise_data['name']} (ID: {exercise.exercise_id}) - Category: {exercise_data['category']}"
                )
            else:
                created_exercises.append(existing)
                print(f"Exercise already exists: {exercise_data['name']} (ID: {existing.exercise_id})")

        db.commit()

        # 운동 레벨 데이터 - 기본 설정: 3회 3세트, 휴식 10초, 레벨 3까지
        for exercise in created_exercises:
            for level in range(1, 4):  # 레벨 1-3
                # 중복 확인
                existing_level = (
                    db.query(ExerciseLevelModel)
                    .filter(ExerciseLevelModel.exercise_id == exercise.exercise_id, ExerciseLevelModel.level == level)
                    .first()
                )

                if not existing_level:
                    # 기본 설정
                    target_sets = 3
                    target_reps = 3 + (level - 1)  # 레벨 1: 3회, 레벨 2: 4회, 레벨 3: 5회
                    rest_seconds = 10
                    experience_points = 10 * level  # 레벨당 10 경험치

                    exercise_level = ExerciseLevelModel(
                        exercise_id=exercise.exercise_id,
                        level=level,
                        target_sets=target_sets,
                        target_reps=target_reps,
                        rest_seconds=rest_seconds,
                        experience_points=experience_points,
                    )

                    db.add(exercise_level)
                    print(
                        f"Created level {level} for {exercise.name}: {target_sets}세트 x {target_reps}회 (휴식: {rest_seconds}초)"
                    )

        db.commit()
        print("Sample data created successfully!")

        # 생성된 데이터 요약 출력
        print("\n=== 생성된 샘플 데이터 요약 ===")
        categories_count = db.query(ExerciseCategoryModel).count()
        exercises_count = db.query(ExerciseModel).count()
        levels_count = db.query(ExerciseLevelModel).count()

        print(f"카테고리: {categories_count}개")
        print(f"운동: {exercises_count}개")
        print(f"운동 레벨: {levels_count}개")

        # 카테고리별 운동 분류 출력
        print("\n=== 카테고리별 운동 분류 ===")
        for category_name, category_id in created_categories.items():
            category_exercises = [ex for ex in created_exercises if ex.category_id == category_id]
            print(f"\n{category_name} ({len(category_exercises)}개):")
            for exercise in category_exercises:
                print(f"  - {exercise.name} (ID: {exercise.exercise_id})")

        # 첫 3개 운동의 레벨 정보 출력
        print("\n=== 주요 운동별 레벨 정보 ===")
        for exercise in created_exercises[:3]:
            levels = (
                db.query(ExerciseLevelModel)
                .filter(ExerciseLevelModel.exercise_id == exercise.exercise_id)
                .order_by(ExerciseLevelModel.level)
                .all()
            )

            print(f"\n{exercise.name} (ID: {exercise.exercise_id}, {exercise.calorie} cal/rep):")
            for level in levels:
                print(
                    f"  레벨 {level.level}: {level.target_sets}세트 x {level.target_reps}회 (휴식: {level.rest_seconds}초, 경험치: {level.experience_points})"
                )

    except Exception as e:
        db.rollback()
        print(f"Error creating sample data: {e}")
        raise e
    finally:
        db.close()


def create_test_user():
    """테스트용 사용자 생성"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # 테스트 사용자 확인
        existing_user = db.query(UserModel).filter(UserModel.email == "test@test.com").first()

        if not existing_user:
            from passlib.context import CryptContext

            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

            test_user = UserModel(
                email="test@test.com",
                password_hash=pwd_context.hash("test1234"),
                name="테스트 사용자",
                profile_image_url=settings.static_url + "images/profiles/default.png",
            )

            db.add(test_user)
            db.commit()
            print("Test user created: test@test.com / test1234")
        else:
            print("Test user already exists: test@test.com")

    except Exception as e:
        db.rollback()
        print(f"Error creating test user: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    init_sample_data()
    create_test_user()
