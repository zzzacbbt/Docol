#routes.py
import pathlib
from handles import index, upload, download, choose_project

PROJECT_ROOT = pathlib.Path(__file__).parent

def setup_routes(app):
    app.router.add_get('/', index, name='index')

    app.router.add_route('*', '/upload', choose_project, name='choose_project')
    app.router.add_route('*', '/upload/{project_id}', upload, name='upload')
    app.router.add_route('*', '/download/{project_id}', download, name='download')
    
    setup_static_routes(app)
    


def setup_static_routes(app):
    app.router.add_static('/static/', path=PROJECT_ROOT / 'static', name='static')