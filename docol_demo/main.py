#main.py
''' Create a aiohttp server '''
import os
from aiohttp import web
from routes import setup_routes
from settings import config
import aiohttp_jinja2
import jinja2
from middlewares import setup_middlewares, login_middlewares
from db import close_pg, init_pg, init_table





async def init_app():
    app = web.Application()
    app['config'] = config
    

    aiohttp_jinja2.setup(
        app, loader=jinja2.FileSystemLoader('%s/templates/' % os.path.dirname(os.path.abspath(__file__)))
    )

    app.middlewares.append(login_middlewares)
    
    app.on_startup.append(init_pg)
    app.on_startup.append(init_table)
    app.on_cleanup.append(close_pg)

    setup_routes(app)
    setup_middlewares(app)

    return app



def main():
    app =  init_app()
        
    configs = config
    web.run_app(app, host=configs['host'], port=configs['port'])
    



if __name__ == "__main__":
    main()
    



