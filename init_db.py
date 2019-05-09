from sqlalchemy import  create_engine, MetaData
import asyncio
from docol_demo.settings import config
from docol_demo.db import projects, files

DSN = "postgresql://{user}:{password}@{host}:{port}/{database}"



def go():
    db_url = DSN.format(**config['postgres'])
    engine = create_engine(db_url) 
    meta = MetaData()
    meta.create_all(bind=engine, tables=[projects, files])
    conn = engine.connect()
            
    #conn.execute('DROP TABLE IF EXISTS projects CASCADE')
    #conn.execute('DROP TABLE IF EXISTS files CASCADE')
    conn.execute(projects.insert(), [
        {'id': 0,
        'project_name': 'Algar'}
    ])
    conn.execute(files.insert(),[
        {'id': 0, 
        'file_name': 'algar_111',
        'path': 'F:/Algar',
        'date': '2019-05-05 17:17:49.629+02',
        'project_id': 0}
    ])



if __name__ == '__main__':

    go()