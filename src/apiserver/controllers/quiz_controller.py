# controllers/quiz_controller.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, aliased
from sqlalchemy import delete, case, func, literal
from sqlalchemy.sql import exists
from uuid import UUID
import random
from datetime import datetime

from apiserver.db.database import get_db
from apiserver.models.quiz_model import Quiz
from apiserver.models.quiz_config_model import QuizConfig
from apiserver.models.question_model import Question
from apiserver.models.choice_model import Choice
from apiserver.models.user_model import User
from apiserver.models.quiz_attempt_model import QuizAttempt
from apiserver.models.answer_model import Answer
from apiserver.schemas.quiz_schema import QuizCreate, QuizUpdate, QuizUpdateResponse, AnswerSave, QuizOut, QuizDetailOut
from apiserver.dependencies.auth import get_current_user, admin_required

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])

# 1. 관리자 퀴즈 생성
@router.post("/")
async def create_quiz(
    quiz_data: QuizCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    quiz = Quiz(
        title=quiz_data.title, 
        description=quiz_data.description,
        created_by=current_user.id
    )
    db.add(quiz)
    await db.flush()

    config = QuizConfig(
        quiz_id=quiz.id,
        num_questions=quiz_data.num_questions,
        shuffle_questions=quiz_data.shuffle_questions,
        shuffle_choices=quiz_data.shuffle_choices,
    )
    db.add(config)
    await db.flush()

    for question_data in quiz_data.questions:
        question = Question(
            quiz_id=quiz.id,
            content=question_data.content,
        )
        db.add(question)
        await db.flush()

        for choice_data in question_data.choices:
            choice = Choice(
                question_id=question.id,
                content=choice_data.content,
            )
            db.add(choice)
            await db.flush()
            if choice_data.is_correct:
                correct_choice_id = choice.id

        if correct_choice_id:
            question.correct_choice_id = correct_choice_id

        db.add(question)
        await db.flush()

    await db.commit()
    await db.refresh(quiz)
    return {
        "id": quiz.id,
        "message": "Successfully Created"
    }

# # 2. 사용자/관리자 퀴즈 목록 조회 + 페이징
@router.get("/", response_model=list[QuizOut])
async def list_quizzes(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attempt_alias = aliased(QuizAttempt)

    stmt = (
        select(
            Quiz,
            case(
                (
                    exists().where(
                        (attempt_alias.quiz_id == Quiz.id) &
                        (attempt_alias.user_id == current_user.id)
                    ),
                    literal(True)
                ),
                else_=literal(False)
            ).label("attempted")
        )
        .options(selectinload(Quiz.config))
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(stmt)

    quizzes_with_attempted = []
    for quiz, attempted in result.all():
        setattr(quiz, "attempted", attempted)

        if not current_user.is_admin:
            # 일반 사용자라면 config를 None 처리하여 제외
            quiz.config = None

        quizzes_with_attempted.append(quiz)

    return quizzes_with_attempted

# 3. 관리자 퀴즈 수정
@router.patch("/{quiz_id}", response_model=QuizUpdateResponse)
async def update_quiz(
    quiz_id: UUID,
    quiz_data: QuizUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    result = await db.execute(select(Quiz).where(Quiz.id == quiz_id))
    quiz = result.scalar_one_or_none()

    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    quiz.update_at = datetime.now()

    update_fields = quiz_data.model_dump(exclude_unset=True)
    
    result = await db.execute(select(QuizConfig).where(QuizConfig.quiz_id == quiz_id))
    quizConfig = result.scalar_one_or_none()

    if not quizConfig:
        raise HTTPException(status_code=404, detail="quizConfig not found")

    # 일반 필드 업데이트
    for key, value in update_fields.items():
        if key == 'questions':
            continue
        if key == 'num_questions' or key == 'shuffle_questions' or key == 'shuffle_choices':
            setattr(quizConfig, key, value)
        else:
            setattr(quiz, key, value)

    # 질문과 선택지 업데이트
    if "questions" in update_fields:
        # 기존 질문 및 선택지 삭제
        await db.execute(delete(Choice).where(Choice.question_id.in_(
            select(Question.id).where(Question.quiz_id == quiz_id)
        )))
        await db.execute(delete(Question).where(Question.quiz_id == quiz_id))

        for question_data in quiz_data.questions:
            question = Question(
                quiz_id=quiz.id,
                content=question_data.content,
            )
            db.add(question)
            await db.flush()

            for choice_data in question_data.choices:
                choice = Choice(
                    question_id=question.id,
                    content=choice_data.content,
                )
                db.add(choice)
                await db.flush()

                if choice_data.is_correct:
                    question.correct_choice_id = choice.id

            await db.flush()

    await db.commit()
    await db.refresh(quiz)
    return {
        'quiz_id': quiz_id,
        "message": "Successfully Update "
    }

# 4. 관리자 퀴즈 삭제
@router.delete("/{quiz_id}", status_code=204)
async def delete_quiz(
    quiz_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    # 퀴즈 존재 여부 확인
    quiz = await db.get(Quiz, quiz_id, options=[selectinload(Quiz.questions)])
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    # 질문 ID 목록 조회
    question_ids = [q.id for q in quiz.questions]

    # 순서대로 삭제
    if question_ids:
        await db.execute(delete(Answer).where(Answer.question_id.in_(question_ids)))
        await db.execute(delete(Choice).where(Choice.question_id.in_(question_ids)))
        await db.execute(delete(Question).where(Question.id.in_(question_ids)))

    await db.execute(delete(QuizConfig).where(QuizConfig.quiz_id == quiz_id))
    await db.execute(delete(QuizAttempt).where(QuizAttempt.quiz_id == quiz_id))
    await db.execute(delete(Quiz).where(Quiz.id == quiz_id))

    await db.commit()

# 5.퀴즈 응시
@router.post("/{quiz_id}/attempt")
async def attempt_quiz(
    quiz_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    result = await db.execute(
        select(Quiz)
        .options(selectinload(Quiz.config))
        .where(Quiz.id == quiz_id)
    )
    quiz = result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    def convert_uuid_to_str(data):
        if isinstance(data, dict):
            return {k: convert_uuid_to_str(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [convert_uuid_to_str(i) for i in data]
        elif isinstance(data, UUID):
            return str(data)
        elif hasattr(data, 'model_dump'):  # 예외 대비
            return convert_uuid_to_str(data.model_dump())
        else:
            return data

    config = quiz.config
    if not config:
        raise HTTPException(status_code=400, detail="Quiz config not found")

    result = await db.execute(
        select(Question)
        .where(Question.quiz_id == quiz_id)
        .options(selectinload(Question.choices))
    )
    questions = result.scalars().all()

    if config.shuffle_questions:
        random.shuffle(questions)

    print(questions)

    def serialize_question(question: Question):
        if config.shuffle_choices:
            random.shuffle(question.choices)
        return {
            "id": str(question.id),
            "content": question.content,
            "correct_choice_id": str(question.correct_choice_id) if question.correct_choice_id else None,
            "choices": [
                {
                    "id": str(choice.id),
                    "question_id": str(choice.id),
                    "content": choice.content,
                } for choice in question.choices
            ]
    }

    questions_as_dict = [serialize_question(q) for q in questions[:config.num_questions]]

    # 새로운 응시 생성
    attempt = QuizAttempt(
        user_id=current_user.id, 
        quiz_id=quiz_id,
        questions=questions_as_dict
    )
    db.add(attempt)
    await db.flush()

    await db.commit()
    return {
        "attempt_id": attempt.id, 
        "message": "Succesfully Attempt"
    }

# 6. 퀴즈 상세 조회 + 랜덤 문제 + 페이징
@router.get("/{quiz_id}", response_model=QuizDetailOut)
async def get_quiz_questions(
    quiz_id: UUID,
    page: int = 1,
    per_page: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Quiz)
        .options(selectinload(Quiz.config))
        .where(Quiz.id == quiz_id)
    )
    quiz = result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    config = quiz.config
    if not config:
        raise HTTPException(status_code=400, detail="Quiz config not found")

    result = await db.execute(
        select(QuizAttempt)
        .where(QuizAttempt.user_id == current_user.id)
        .where(QuizAttempt.quiz_id == quiz_id)
    )
    attempt = result.scalar_one_or_none()
    if not attempt:
        raise HTTPException(status_code=404, detail="Quiz attempt not found")

    questions = attempt.questions

    total_pages = (len(questions) + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page

    # 저장된 답변 불러오기
    result = await db.execute(
        select(Answer).where(Answer.attempt_id == attempt.id)
    )
    answers = result.scalars().all()

    data = []
    for question in questions[start:end]:
        choices = question["choices"]
        if config.shuffle_choices:
            random.shuffle(choices)
        data.append({
            "id": question["id"],
            "content": question["content"],
            "correct_choice_id": None,
            "choices": [
                {
                    "id": choice["id"], 
                    "content": choice["content"],
                    "selected": True if next((ans for ans in answers if str(ans.choice_id) == str(choice["id"])), None) else False,
                } for choice in choices
            ]
        })

    return {
        "id": quiz.id,
        "title": quiz.title,
        "description": quiz.description,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "questions": data
    }

# 5.응시내용 임시저장
@router.post("/{quiz_id}/answer")
async def save_quiz_answers(
    quiz_id: UUID,
    answer_data: AnswerSave,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    result = await db.execute(
        select(Quiz)
        .options(selectinload(Quiz.config))
        .where(Quiz.id == quiz_id)
    )
    quiz = result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    existing_attempt = await db.execute(
        select(QuizAttempt).where(
            QuizAttempt.quiz_id == quiz_id,
            QuizAttempt.user_id == current_user.id
        )
    )

    attempt = existing_attempt.scalar_one_or_none()

    # 이전 답안 삭제 후 다시 저장
    await db.execute(
        delete(Answer).where(Answer.attempt_id == attempt.id)
    )

    for ans in answer_data.answer:
        db.add(Answer(
            attempt_id=attempt.id,
            question_id=ans.question_id,
            choice_id=ans.choice_id,
            is_correct=False  # 제출이 아니므로 아직 판단하지 않음
        ))

    await db.commit()
    return {
        "attempt_id": attempt.id, 
        "message": "Successfully Saved"
    }

# 7.퀴즈 제출
@router.post("/{quiz_id}/submit")
async def submit_quiz_attempt(
    quiz_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 기존 응시 내역 확인
    result = await db.execute(
        select(QuizAttempt).where(
            QuizAttempt.quiz_id == quiz_id,
            QuizAttempt.user_id == current_user.id
        )
    )
    attempt = result.scalar_one_or_none()
    if not attempt:
        raise HTTPException(status_code=404, detail="No saved attempt found")
    if attempt.submitted_at:
        raise HTTPException(status_code=400, detail="Already attempted")


    # 저장된 답변 불러오기
    result = await db.execute(
        select(Answer).where(Answer.attempt_id == attempt.id)
    )
    answers = result.scalars().all()

    total_score = 0
    for ans in answers:
        question: Question = await db.get(Question, ans.question_id)
        is_correct = question.correct_choice_id == ans.choice_id
        if is_correct:
            total_score += 1
        db.add(ans)

    attempt.score = total_score
    attempt.submitted_at = datetime.now()
    await db.commit()
    return {
        "attempt_id": attempt.id, 
        "score": total_score,
        "submitted_at": attempt.submitted_at
    }
