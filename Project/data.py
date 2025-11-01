from sqlmodel import SQLModel, create_engine


engine = create_engine("sqlite:///database_project.db", echo=False)


def init_db():
    SQLModel.metadata.create_all(engine)



