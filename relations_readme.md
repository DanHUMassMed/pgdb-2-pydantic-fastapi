# Relation ships mapping

## One-to-Many (most common) and Many-to-One (inverse of One-to-Many)

```
class Conference(Base):
    __tablename__ = 'conferences'
    id = Column(Integer, primary_key=True)
    attendees = relationship("Attendee", back_populates="conference")

class Attendee(Base):
    __tablename__ = 'attendees'
    id = Column(Integer, primary_key=True)
    conference_id = Column(Integer, ForeignKey('conferences.id'))
    conference = relationship("Conference", back_populates="attendees")
```

### Pydantic
```
# For creation
class AttendeeCreate(BaseModel):
    conference_id: int

class ConferenceCreate(BaseModel):
    pass  # Add fields as needed

# For full reading (nested)
class AttendeeRead(BaseModel):
    id: int
    conference_id: int

    class Config:
        orm_mode = True

class ConferenceRead(BaseModel):
    id: int
    attendees: List[AttendeeRead]

    class Config:
        orm_mode = True
```
## One-to-One

```
class Attendee(Base):
    __tablename__ = 'attendees'
    id = Column(Integer, primary_key=True)
    judge = relationship("Judge", back_populates="attendee", uselist=False)

class Judge(Base):
    __tablename__ = 'judges'
    id = Column(Integer, primary_key=True)
    attendee_id = Column(Integer, ForeignKey('attendees.id'))
    attendee = relationship("Attendee", back_populates="judge")
```

## Many-to-Many

```
association_table = Table(
    'association', Base.metadata,
    Column('attendee_id', Integer, ForeignKey('attendees.id')),
    Column('poster_id', Integer, ForeignKey('posters.id'))
)

class Attendee(Base):
    __tablename__ = 'attendees'
    id = Column(Integer, primary_key=True)
    posters = relationship("Poster", secondary=association_table, back_populates="attendees")

class Poster(Base):
    __tablename__ = 'posters'
    id = Column(Integer, primary_key=True)
    attendees = relationship("Attendee", secondary=association_table, back_populates="posters")
```

## Additional Options
	•	back_populates="...": creates a bidirectional relationship.
	•	cascade="...": controls what happens on delete/update.
	•	lazy="select"/"joined"/"subquery": controls when related data is loaded.
	•	uselist=False: enforces a one-to-one instead of one-to-many.


# Example Code!!!!!!!!!!!!!
    ```
    from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import Relationship

from models.base import TimeStampedModel, Model


class User(TimeStampedModel):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(80), nullable=False)
    last_name = Column(String(80), nullable=False)
    email = Column(String(320), nullable=False, unique=True)

    preference = Relationship("Preference", back_populates="user", uselist=False, passive_deletes=True)
    addresses = Relationship("Address", back_populates="user", passive_deletes=True)
    roles = Relationship("Role", secondary="user_roles", back_populates="users", passive_deletes=True)

    def __repr__(self):
        return f"{self.__class__.__name__}, name: {self.first_name} {self.last_name}"


class Preference(TimeStampedModel):
    __tablename__ = "preferences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    language = Column(String(80), nullable=False)
    currency = Column(String(3), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, unique=True)

    user = Relationship("User", back_populates="preference")


class Address(TimeStampedModel):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    road_name = Column(String(80), nullable=False)
    postcode = Column(String(80), nullable=False)
    city = Column(String(80), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    user = Relationship("User", back_populates="addresses")

    def __repr__(self):
        return f"{self.__class__.__name__}, name: {self.city}"


class Role(Model):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(80), nullable=False)
    slug = Column(String(80), nullable=False, unique=True)

    users = Relationship("User", secondary="user_roles", back_populates="roles", passive_deletes=True)

    def __repr__(self):
        return f"{self.__class__.__name__}, name: {self.name}"


class UserRole(TimeStampedModel):
    __tablename__ = "user_roles"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    ```