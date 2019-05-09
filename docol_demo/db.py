import aiopg.sa

from sqlalchemy import (
    MetaData, Table, Column, ForeignKey,
    Integer, String, Date
)

meta = MetaData()

projects = Table(
    'projects', meta,

    Column('id', Integer, primary_key=True),
    Column('project_name', String(200), nullable=False),
)

files = Table(
    'files', meta,

    Column('id', Integer, primary_key=True),
    Column('file_name', String(200), nullable=False),
    Column('path', String(200), nullable=False),
    Column('date', Date, nullable=False),

    Column('project_id',
            Integer,
            ForeignKey('projects.id', ondelete='CASCADE'))
)


class RecordNotFound(Exception):
    """Requested record in database was not found"""


async def init_pg(app):
    conf = app['config']['postgres']
    engine = await aiopg.sa.create_engine(
        database=conf['database'],
        user=conf['user'],
        password=conf['password'],
        host=conf['host'],
        port=conf['port'],
        minsize=conf['minsize'],
        maxsize=conf['maxsize']
    )
    app['db'] = engine

async def close_pg(app):
    app['db'].close()
    await app['db'].wait_closed()


async def get_project(conn,project_id):
    result = await conn.execute(
        projects.select()
        .where(projects.c.id == project_id)
    )
    project_records = await result.first()
    if not project_records:
        msg = "Project with id: {} does not exists"
        raise RecordNotFound(msg.format(project_id))
    result = await conn.execute(
        files.select()
        .where(files.c.project_id == project_id)
        .order_by(files.c.id)
    )
    file_records = await result.fetchall()
    return project_records, file_records


async def get_projects(conn):
    result = await conn.execute(
        projects.select()
        .order_by(projects.c.id)
    )
    projects_records = await result.fetchall()
    return projects_records 

async def vote(conn, question_id, choice_id):
    result = await conn.execute(
        choice.update()
        .returning(*choice.c)
        .where(choice.c.question_id == question_id)
        .where(choice.c.id == choice_id)
        .values(votes=choice.c.votes+1))
    record = await result.fetchone()
    if not record:
        msg = "Question with id: {} or choice id: {} does not exists"
        raise RecordNotFound(msg.format(question_id, choice_id))


async def save(conn, id, filename, path, date, project_id):
    result = await conn.execute(files.insert(), [
        {'id': id,
        'file_name': filename,
        'path': path,
        'date': date,
        'project_id': project_id
        }
    ])


async def get_project_name(conn,project_id):
    result = await conn.execute(
        projects.select()
        .where(projects.c.id == project_id)
        )
    project_records = await result.first()
    if not project_records:
        msg = "Project with id: {} does not exists"
        raise RecordNotFound(msg.format(project_id))

    return project_records



