import uuid
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import declarative_base
from datetime import datetime, timedelta
from datetime import datetime
from app.core.config import get_settings
from app.core.database import Base

class CommonColumns(object):
  """
  共通カラム
  """
  @declared_attr
  def delete_flag(cls): 
    return Column(Boolean, default=False, nullable=False, comment="削除フラグ")
  
  @declared_attr
  def create_datetime(cls):
    return Column(DateTime, default=datetime.now(), nullable=False, comment="作成日時")
  
  @declared_attr
  def update_datetime(cls): 
    return Column(DateTime, default=datetime.now(), onupdate=datetime.now(), nullable=False, comment="更新日時")

class Authcode(Base, CommonColumns):
  """
  認証コード
  """
  __tablename__ = "authcodes"
  authcode_id = Column(
    String(36), 
    primary_key=True, 
    default=lambda: str(uuid.uuid4()), 
    comment="認証コードID"
  )
  code = Column(String(6), nullable=False, comment="コード")
  email = Column(String(255), nullable=False, comment="メールアドレス")
  expire_datetime = Column(
    DateTime, 
    default=(datetime.now() + timedelta(minutes=get_settings().AUTHCODE_EXPIRE_MINUTES)), 
    nullable=False, 
    comment="有効期限"
  )