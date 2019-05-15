from sqlalchemy import  create_engine, MetaData
import asyncio
from docol_demo.settings import config
from docol_demo.db import projects, files, users

DSN = "postgresql://{user}:{password}@{host}:{port}/{database}"



def go():
    db_url = DSN.format(**config['postgres'])
    engine = create_engine(db_url) 
    meta = MetaData()
    meta.create_all(bind=engine, tables=[users,projects, files])
    conn = engine.connect()
            

if __name__ == '__main__':
    
    go()