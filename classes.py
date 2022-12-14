import sqlalchemy as sq
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import functions


Base = declarative_base()
engine = sq.create_engine('postgresql://lackate@localhost:5432/vkinder',
                          client_encoding='utf8')
Session = sessionmaker(bind=engine)

session = Session()
connection = engine.connect()


class User(Base):
    __tablename__ = 'user'
    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    vk_id = sq.Column(sq.Integer, unique=True)


class DatingUser(Base):
    __tablename__ = 'dating_user'
    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    vk_id = sq.Column(sq.Integer, unique=True)
    first_name = sq.Column(sq.String)
    second_name = sq.Column(sq.String)
    city = sq.Column(sq.String)
    link = sq.Column(sq.String)
    id_user = sq.Column(sq.Integer, sq.ForeignKey('user.id', ondelete='CASCADE'))


class Photos(Base):
    __tablename__ = 'photos'
    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    link_photo = sq.Column(sq.String)
    count_likes = sq.Column(sq.Integer)
    id_dating_user = sq.Column(sq.Integer, sq.ForeignKey('dating_user.id', ondelete='CASCADE'))


def delete_db_favorites(ids):
    current_user = session.query(DatingUser).filter_by(vk_id=ids).first()
    session.delete(current_user)
    session.commit()


def check_db_master(ids):
    return session.query(User).filter_by(vk_id=ids).first()


def check_db_user(ids):
    return session.query(DatingUser).filter_by(vk_id=ids).first()


def check_db_favorites(ids):
    current_users_id = session.query(User).filter_by(vk_id=ids).first()
    return session.query(DatingUser).filter_by(id_user=current_users_id.id).all()


def register_user(vk_id):
    try:
        new_user = User(
            vk_id=vk_id
        )
        session.add(new_user)
        session.commit()
        return True
    except (IntegrityError, InvalidRequestError):
        return False


def add_user(event_id, vk_id, first_name, second_name, city, link, id_user):
    try:
        new_user = DatingUser(
            vk_id=vk_id,
            first_name=first_name,
            second_name=second_name,
            city=city,
            link=link,
            id_user=id_user
        )
        session.add(new_user)
        session.commit()
        functions.write_msg(event_id,
                            '?????????????? ???????????????? ?? ??????????????????')
        return True
    except (IntegrityError, InvalidRequestError):
        functions.write_msg(event_id,
                            '???????????????????????? ?????? ?? ??????????????????.')
        return False


def add_user_photos(event_id, link_photo, count_likes, id_dating_user):
    try:
        new_user = Photos(
            link_photo=link_photo,
            count_likes=count_likes,
            id_dating_user=id_dating_user
        )
        session.add(new_user)
        session.commit()
        functions.write_msg(event_id,
                            '???????? ???????????????????????? ?????????????????? ?? ??????????????????')
        return True
    except (IntegrityError, InvalidRequestError):
        functions.write_msg(event_id,
                            '?????? ?????????????????? ?? ??????????????????')
        return False


if __name__ == '__main__':
    Base.metadata.create_all(engine)
