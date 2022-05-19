from sqlalchemy import orm

PGSession = orm.scoped_session(orm.sessionmaker(autocommit=False, autoflush=True))
