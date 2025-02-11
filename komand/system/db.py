from sqlalchemy import create_engine
from sqlalchemy import event, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Interval, func, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import text
from params import DATABASE_URL, DATABASE_URL_async
from datetime import timedelta
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'    
    id         = Column(Integer,  primary_key = True,  index    = True)
    username   = Column(String,   unique      = False, index    = True)
    tg_id      = Column(String,   unique      = True,  nullable = True)
    role       = Column(String,   default     = 'user')
    created_at = Column(DateTime, default     = func.now())
    context    = Column(Integer,  default     = 0)
    timezone   = Column(Interval, default     = timedelta(hours=0))

    notes      = relationship("Note",    back_populates = "user")
    tasks      = relationship("Task",    back_populates = "user")
    messages   = relationship("Message", back_populates = "user")
    thoughts   = relationship("Thought", back_populates = "user")
    goals      = relationship("Goal",    back_populates = "user")


class Note(Base):
    __tablename__ = 'notes'
    id          = Column(Integer,  primary_key = True, index    = True)
    text        = Column(String)
    user_id     = Column(Integer,  ForeignKey('users.id'))
    number      = Column(Integer)
    created_at  = Column(DateTime, default     = func.now())    

    user = relationship("User", back_populates="notes")

class Task(Base):
    __tablename__ = 'tasks'
    id          = Column(Integer,  primary_key = True, index    = True)
    text        = Column(String)
    user_id     = Column(Integer,  ForeignKey('users.id'))
    number      = Column(Integer)
    created_at  = Column(DateTime, default     = func.now())    
    time        = Column(DateTime) 
    done        = Column(Boolean, default      = False)

    user = relationship("User", back_populates="tasks")

class Thought(Base):
    __tablename__ = 'thoughts'
    id          = Column(Integer,  primary_key = True, index    = True)
    text        = Column(String)
    user_id     = Column(Integer,  ForeignKey('users.id'))
    number      = Column(Integer)
    created_at  = Column(DateTime, default     = func.now())

    user = relationship("User", back_populates="thoughts")

class Goal(Base):
    __tablename__ = 'goals'
    id          = Column(Integer,  primary_key = True, index    = True)
    text        = Column(String)
    user_id     = Column(Integer,  ForeignKey('users.id'))
    number      = Column(Integer)
    deadline    = Column(DateTime)
    created_at  = Column(DateTime, default     = func.now())

    user = relationship("User", back_populates = "goals")

class Message(Base):
    __tablename__ = 'messages'
    id          = Column(Integer,  primary_key = True, index    = True)
    text        = Column(String)
    user_id     = Column(Integer,  ForeignKey('users.id'))
    role        = Column(String,   default='user')
    to_message  = Column(String)
    created_at  = Column(DateTime, default     = func.now())

    user = relationship("User", back_populates = "messages")


def create_numbering_listener(table_name):
    def set_number(mapper, connection, target):
        if target.user_id is not None:
            stmt = text(f'SELECT COALESCE(MAX(number), 0) FROM {table_name} WHERE user_id = :user_id')
            result = connection.execute(stmt, {'user_id': target.user_id})
            max_number = result.scalar()
            target.number = max_number + 1
    return set_number

def increment_user_context(mapper, connection, target):
    connection.execute(
        User.__table__.update()
        .where(User.id == target.user_id)
        .values(context=User.context + 2))


event.listen(Note,    'before_insert', create_numbering_listener('notes'))
event.listen(Task,    'before_insert', create_numbering_listener('tasks'))
event.listen(Thought, 'before_insert', create_numbering_listener('thoughts'))
event.listen(Goal,    'before_insert', create_numbering_listener('goals'))

event.listen(Message, 'after_insert',  increment_user_context)


engine        = create_engine(DATABASE_URL)
async_engine  = create_async_engine(DATABASE_URL_async)

SessionLocal  = sessionmaker(autocommit = False, autoflush = False, bind = engine)
async_session = sessionmaker(async_engine, class_ = AsyncSession) #pyright: ignore

Base.metadata.create_all(bind = engine)


async def fetch_tasks():
    async with async_session() as session: #pyright: ignore
        result = await session.execute(text("SELECT id, user_id, time, text, number FROM tasks"))
        return result.fetchall()

async_session_maker = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

@asynccontextmanager
async def get_db_async():
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()
