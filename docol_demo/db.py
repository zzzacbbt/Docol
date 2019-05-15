import aiopg.sa

from sqlalchemy import (
    MetaData, Table, Column, ForeignKey,
    Integer, String, DateTime
)

meta = MetaData()


users = Table(
    'users', meta,

    Column('id', Integer, primary_key=True),
    Column('username', String(200), nullable=False),
    Column('password', String(200), nullable=False)
)

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
    Column('datetime', DateTime, nullable=False),

    Column('project_id',
           Integer,
           ForeignKey('projects.id', ondelete='CASCADE'))
)


class RecordNotFound(Exception):
    """Requested record in database was not found"""


class AddNewProjectFailed(Exception):
    """Add new project in database failed"""


class DeleteProjectFailed(Exception):
    """delete project in database failed"""


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


async def get_projectandfiles(conn, project_id):
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


async def save(conn, id, filename, path, datetime, project_id):
    result = await conn.execute(files.insert(), [
        {'id': id,
         'file_name': filename,
         'path': path,
         'datetime': datetime,
         'project_id': project_id
         }
    ])


async def get_project(conn, project_id):
    result = await conn.execute(
        projects.select()
        .where(projects.c.id == project_id)
    )
    project_records = await result.first()
    if not project_records:
        msg = "Project with id: {} does not exists"
        raise RecordNotFound(msg.format(project_id))

    return project_records


async def get_Table_rowcount(conn, Table):
    result = await conn.execute(Table.select())

    Table_rowcount = result.rowcount
    return Table_rowcount


async def get_files_rowcount(conn, project_id):
    result = await conn.execute(
        files.select()
        .where(files.c.project_id == project_id)
    )

    files_rowcount = result.rowcount
    return files_rowcount


async def create_project(conn, id, project_name):
    await conn.execute(projects.insert(), [
        {'id': id,
         'project_name': project_name}
    ])


async def delete_project(conn, id):
    rowcount = await get_files_rowcount(conn, project_id=id)
    if rowcount == 0:
        await conn.execute(
            projects.delete()
            .where(projects.c.id == id)
        )
        await conn.execute(
        projects.update()
        .where(projects.c.id > id)
        .values(id=projects.c.id-1)
    )
    else:
        pass


async def delete_file(conn, file_id):
    await conn.execute(
        files.delete()
        .where(files.c.id == file_id)
    )
    await conn.execute(
        files.update()
        .where(files.c.id > file_id)
        .values(id=files.c.id-1)
    )


async def get_filepath(conn, file_id):
    result = await conn.execute(
        files.select()
        .where(files.c.id == file_id)
    )
    file_record = await result.first()
    return file_record


async def get_projectsandfiles(conn):
    result = await conn.execute(
        files.select()
        .order_by(files.c.id)
    )
    file_records = await result.fetchall()
    result = await conn.execute(
        projects.select()
        .order_by(projects.c.id)
    )
    project_records = await result.fetchall()
    return project_records, file_records


async def add_user(conn, id, username, password):
    result = await conn.execute(
        users.insert(), [
            {"id": id,
             "username": username,
             "password": password}
        ])


async def login_user(conn, username):
    result = await conn.execute(
        users.select().
        where(users.c.username == username)
    )
    user_record = await result.first()
    return user_record

