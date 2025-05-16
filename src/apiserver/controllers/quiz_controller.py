# controllers/quiz_controller.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, aliased
from sqlalchemy import delete, case, func
from sqlalchemy.sql import exists
from uuid import UUID
import random

from apiserver.db.database import get_db
from apiserver.models.quiz_model import Quiz
from apiserver.models.quiz_config_model import QuizConfig
from apiserver.models.question_model import Question
from apiserver.models.choice_model import Choice
from apiserver.models.user_model import User
from apiserver.models.quiz_attempt_model import QuizAttempt
from apiserver.models.answer_model import Answer
from apiserver.schemas.quiz_schema import QuizCreate, QuizUpdate, QuizOut, QuizDetailOut, QuizAttemptCreate
from apiserver.dependencies.auth import get_current_user, admin_required

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])

# 1. 관리자 퀴즈 생성
@router.post("/", response_model=QuizOut)
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
    return quiz

# 2. 사용자/관리자 퀴즈 목록 조회 + 페이징
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
                (func.count(attempt_alias.id) > 0, True),
                else_=False
            ).label("attempted")
        )
        .outerjoin(attempt_alias, Quiz.id == attempt_alias.quiz_id)
        .group_by(Quiz.id)
        .offset(skip)
        .limit(limit)
        .options(selectinload(Quiz.config))
    )

    result = await db.execute(stmt)

    quizzes_with_attempted = [
        {**quiz.__dict__, "attempted": attempted}
        for quiz, attempted in result.all()
    ]

    return quizzes_with_attempted

# 3. 관리자 퀴즈 수정
@router.patch("/{quiz_id}", response_model=QuizOut)
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

    update_fields = quiz_data.model_dump(exclude_unset=True)
    
    # 일반 필드 업데이트
    for key, value in update_fields.items():
        if key != "questions":
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
    return quiz

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
        await db.execute(delete(Choice).where(Choice.question_id.in_(question_ids)))
        await db.execute(delete(Question).where(Question.id.in_(question_ids)))

    await db.execute(delete(QuizConfig).where(QuizConfig.quiz_id == quiz_id))
    await db.execute(delete(QuizAttempt).where(QuizAttempt.quiz_id == quiz_id))
    await db.execute(delete(Quiz).where(Quiz.id == quiz_id))

    await db.commit()

# 5. 사용자/관리자 퀴즈 상세 조회 + 랜덤 문제 + 페이징
@router.get("/{quiz_id}", response_model=QuizDetailOut)
async def get_quiz_questions(
    quiz_id: UUID,
    page: int = 1,
    per_page: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = (
        select(
            Quiz,
            exists().where(QuizAttempt.quiz_id == Quiz.id).label("attempted")
        )
        .where(Quiz.id == quiz_id)
        .options(selectinload(Quiz.config))
    )

    result = await db.execute(stmt)
    row = result.first()

    quiz = row[0]
    attempted = row[1]

    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

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

    selected_questions = questions[:config.num_questions]

    total_pages = (len(selected_questions) + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page

    data = []
    for question in selected_questions[start:end]:
        choices = question.choices
        if config.shuffle_choices:
            random.shuffle(choices)
        data.append({
            "id": question.id,
            "content": question.content,
            "correct_choice_id": question.correct_choice_id if current_user.is_admin else None,
            "choices": [
                {
                    "id": choice.id, 
                    "content": choice.content,
                } for choice in choices
            ]
        })

    return {
        "id": quiz.id,
        "title": quiz.title,
        "description": quiz.description,
        "attempted": attempted,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "questions": data
    }

# 6. 퀴즈 응시 및 제출 데모
# @router.post("/{quiz_id}/attempt")
# async def submit_attempt(
#     quiz_id: UUID,
#     attempt_data: QuizAttemptCreate,
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     quiz = await db.get(Quiz, quiz_id)
#     if not quiz:
#         raise HTTPException(status_code=404, detail="Quiz not found")

#     attempt = QuizAttempt(user_id=current_user.id, quiz_id=quiz_id)
#     db.add(attempt)
#     await db.flush()

#     total_score = 0
#     for ans in attempt_data.answer:
#         question:Question = await db.get(Question, ans.question_id)
#         is_correct = question.correct_choice_id == ans.choice_id
#         if is_correct:
#             total_score += 1

#         db.add(Answer(
#             attempt_id=attempt.id,
#             question_id=ans.question_id,
#             choice_id=ans.choice_id,
#             is_correct=is_correct,
#         ))

#     attempt.score = total_score
#     await db.commit()
#     return {"attempt_id": attempt.id, "score": total_score}
