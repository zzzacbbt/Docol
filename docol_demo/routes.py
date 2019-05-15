#routes.py
import pathlib
import handles 

PROJECT_ROOT = pathlib.Path(__file__).parent

def setup_routes(app):
    app.router.add_get('/', handles.index, name='index')

    app.router.add_route('*', '/registration', handles.registration, name='registration')
    app.router.add_route('*', '/login', handles.login, name='login')
    app.router.add_route('*', '/upload/{project_id}', handles.upload, name='upload')
    app.router.add_route('*', '/download/{project_id}/files', handles.download_files, name='download_files')
    app.router.add_route('*', '/download/{project_id}/files/{datetime}/{file_name}', handles.download, name='download')
    app.router.add_route('*', '/create_project', handles.create_project, name='create_project')
    app.router.add_route('*', '/delete_project', handles.delete_project, name='delete_project')
    app.router.add_route('*', '/delete/{project_id}/files', handles.delete_files, name='delete_files')
    app.router.add_route('*', '/pipeline', handles.pipeline, name='pipeline')
    setup_static_routes(app)

def setup_static_routes(app):
    app.router.add_static('/static/', path=PROJECT_ROOT / 'static', name='static')