# from sqlalchemy import Boolean, Column, ForeignKey, Index
# from sqlalchemy.dialects.postgresql import UUID
# from sqlalchemy.orm import backref, relationship

# from core.database import Base

# '''
# Foreignkey naming convention = fk_sourceTable_columnName_targetTable
# index naming covention = idx_sourceTable_columnName
# '''

# class Friend(Base):
#     __tablename__ = "friends"
    
#     friend_creater_id = Column(
#         UUID(as_uuid=True),
#         ForeignKey(
#             "users.id",
#             name = "fk_friends_friend_creater_id_users",
#         ),
#         nullable=True,
#     )
    
#     __table_args__ = (
#         Index('idx_friends_friend_creater_id','friend_creater_id'),
#     )
    
#     shadow_group_id = Column(
#         UUID(as_uuid=True),
#         ForeignKey(
#             "groups.id",
#             name= "fk_friends_shadow_group_id_groups",
#         ),
#         nullable=True,
#     )
    
#     is_friend = Column(Boolean, nullable=False, default=False)
    
#     # relationShips
    
#     friend = relationship(
#         "User",
#         foreign_keys=[friend_creater_id],
#         backref=backref("friend_creater", remote_side=[id]),
#         lazy="selectin"
#     )
    
#     shadow_group = relationship("Group", foreign_keys=[shadow_group_id])
    
    