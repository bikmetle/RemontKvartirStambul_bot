from sqlalchemy import create_engine, Column, Integer, String, DateTime, SmallInteger, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

DATABASE_URL = 'sqlite:///mydatabase.db'
engine = create_engine(DATABASE_URL)
Base = declarative_base()

class UserModel(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    full_name = Column(String(100))
    username = Column(String(50))
    displayed_name = Column(String(100))
    comments = relationship("CommentModel", back_populates="user")
    responses = relationship("ResponseModel", back_populates="applicant")
    offers = relationship("OfferModel", back_populates="customer")

class CommentModel(Base):
    __tablename__ = "comment"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime)
    mark = Column(SmallInteger)
    offer_id = Column(Integer, ForeignKey('offer.id'))
    offer = relationship("OfferModel", back_populates="comments")
    text = Column(String)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("UserModel", back_populates="comments")

class OfferModel(Base):
    __tablename__ = "offer"
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('user.id'))
    customer = relationship("UserModel", back_populates="offers")
    description = Column(String)
    date = Column(DateTime)
    responses = relationship("ResponseModel", back_populates="offer")
    comments = relationship("CommentModel", back_populates="offer")

class ResponseModel(Base):
    __tablename__ = "response"
    id = Column(Integer, primary_key=True, index=True)
    applicant_id = Column(Integer, ForeignKey('user.id'))
    applicant = relationship("UserModel", back_populates="responses")
    offer_id = Column(Integer, ForeignKey('offer.id'))
    offer = relationship("OfferModel", back_populates="responses")
    is_canceled = Column(Integer, default=0)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = Session()

Base.metadata.create_all(bind=engine)