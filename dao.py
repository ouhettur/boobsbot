from models import *
from sqlalchemy.orm import sessionmaker, load_only
from sqlalchemy import create_engine, and_
from config import logindb, passdb, dbhost, dbname
import datetime
from sqlalchemy.sql import func

engine = create_engine(
    f'postgresql://{logindb}:{passdb}@{dbhost}/{dbname}',
    echo=True)

Session = sessionmaker(bind=engine)
Session.configure(bind=engine)

session = Session()


def is_telegram_id_exists(telegram_id: int) -> bool:
    query = session.query(User) \
        .filter(User.telegram_id == telegram_id)
    return session.query(query.exists()).scalar()


def add_chat_by_telegram(telegram_id: int, name: str):
    session.add(User(telegram_id=telegram_id,
                     created_at=datetime.datetime.utcnow(),
                     chat_name=name
                     )
                )
    session.commit()


def add_user_by_telegram(telegram_id: int, first_name: str, last_name: str, login: str, language_code: str):
    session.add(User(telegram_id=telegram_id,
                     created_at=datetime.datetime.utcnow(),
                     first_name=first_name,
                     last_name=last_name,
                     login=login,
                     language_code=language_code
                     )
                )
    session.commit()


def find_user_id_by_telegram_id(telegram_id: int) -> int:
    user = session.query(User) \
        .filter(User.telegram_id == telegram_id) \
        .first()
    return user.id


def save_img(user_id: int, img_name: str, media_type: str, telegram_file_id: str):
    session.add(
        Img(
            user_id=user_id,
            created_at=datetime.datetime.utcnow(),
            archived_at=None,
            sum_rating=0,
            name=img_name,
            media_type=media_type,
            count_rating=0,
            rank=0,
            telegram_file_id=telegram_file_id,
            reports_count=0
        )
    )
    session.query(User) \
        .filter(User.id == user_id) \
        .update({'upload_rating': (User.upload_rating + 1)})
    session.commit()


def find_random_available_media(user_id: int) -> Img:
    subquery = session.query(Show.img_id) \
        .filter(Show.user_id == user_id) \
        .subquery()

    return session.query(Img) \
        .filter(and_(Img.user_id != user_id, ~Img.id.in_(subquery), Img.archived_at == None)) \
        .order_by(func.random()) \
        .first()


def find_top_media(user_id: int, count=10) -> list:
    subquery = session.query(Show).filter(Show.user_id == user_id).subquery()
    return session.query(Img.id, Img.user_id, Img.telegram_file_id, Img.count_rating, Img.sum_rating, Img.media_type,
                         subquery.c.rating) \
        .outerjoin(subquery, subquery.c.img_id == Img.id) \
        .order_by(Img.sum_rating.desc(), Img.count_rating) \
        .limit(count)


def save_show(img_id: int, user_id: int):
    session.add(Show(img_id=img_id,
                     user_id=user_id,
                     rating=None,
                     created_at=datetime.datetime.utcnow(),
                     rated_at=None,
                     ))
    session.commit()


def put_show_mark(img_id: int, mark: int, user_id: int):
    session.query(Show) \
        .filter(Show.user_id == user_id) \
        .filter(Show.img_id == img_id) \
        .update({'rating': mark, 'rated_at': datetime.datetime.utcnow()})
    session.query(User) \
        .filter(User.id == user_id) \
        .update({'view_rating': (User.view_rating + 1)})
    session.query(Img) \
        .filter(Img.id == img_id) \
        .update({'sum_rating': (Img.sum_rating + mark), 'count_rating': (Img.count_rating + 1)})
    session.commit()


def put_report(img_id=int, user_id=int):
    session.query(User) \
        .filter(User.id == user_id) \
        .update({'view_rating': (User.view_rating + 1)})
    session.query(Show) \
        .filter(Show.user_id == user_id) \
        .filter(Show.img_id == img_id) \
        .update({'reported_at': datetime.datetime.utcnow()})
    session.query(Img) \
        .filter(Img.id == img_id) \
        .update({'reports_count': (Img.reports_count + 1)})
    session.commit()


def count_user_upload(user_id: int) -> int:
    return session.query(Img) \
        .filter(Img.user_id == user_id) \
        .count()


def count_user_img_liked(user_id: int) -> int:
    return session.query(Img) \
        .outerjoin(Show, Show.img_id == Img.id) \
        .filter(Img.user_id == user_id) \
        .filter(Show.rating == 1) \
        .count()


def count_user_img_disliked(user_id: int) -> int:
    return session.query(Img) \
        .outerjoin(Show, Show.img_id == Img.id) \
        .filter(Img.user_id == user_id) \
        .filter(Show.rating == -1) \
        .count()


def count_user_img_reported(user_id: int) -> int:
    return session.query(Img) \
        .outerjoin(Show, Show.img_id == Img.id) \
        .filter(Img.user_id == user_id) \
        .filter(Show.reported_at != None) \
        .count()


def place_in_upload_rating(user_id: int) -> int:
    subquery = session.query(User.id.label("id"),
                             func.rank().over(order_by=func.coalesce(func.sum(Img.sum_rating), 0).desc()).label("rnk")) \
        .outerjoin(Img, User.id == Img.user_id) \
        .group_by(User.id).subquery()
    return session.query(subquery.c.rnk).filter(subquery.c.id == user_id).first()


def count_user_img_archived(user_id: int) -> int:
    return session.query(Img) \
        .filter(Img.user_id == user_id) \
        .filter(Img.archived_at != None) \
        .count()


def find_random_media(count: int) -> list:
    return session.query(Img) \
        .filter(Img.archived_at == None) \
        .options(load_only('telegram_file_id', 'media_type')) \
        .offset(
        func.floor(
            func.random() *
            session.query(func.count(Img.telegram_file_id))
        )
    ).limit(count).all()


def find_user_role(telegram_id: int) -> str:
    user = session.query(User) \
        .filter(User.telegram_id == telegram_id) \
        .first()
    return user.role


def count_reported_img() -> int:
    return session.query(Img) \
        .filter(Img.reports_count > 0) \
        .filter(Img.archived_at == None) \
        .count()


def all_reported_img() -> list:
    return session.query(Img) \
        .filter(Img.reports_count > 0) \
        .filter(Img.archived_at == None) \
        .all()


def justify_img(img_id: int):
    session.query(Img) \
        .filter(Img.id == img_id) \
        .update({'reports_count': 0})
    session.commit()


def archive_img(img_id: int):
    session.query(Img) \
        .filter(Img.id == img_id) \
        .update({'archived_at': datetime.datetime.utcnow()})
    session.commit()


def save_inline_query(query: str, telegram_id: int):
    session.add(InlineQuery(query=query,
                            telegram_id=telegram_id,
                            created_at=datetime.datetime.utcnow()
                            )
                )
    session.commit()
