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