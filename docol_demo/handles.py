# views.py
import logging
from aiohttp import web
import db
import aiohttp_jinja2
import os
from os.path import dirname
import time
import aiofiles


@aiohttp_jinja2.template('main.html')
async def index(request):
    async with request.app['db'].acquire() as conn:
        project_id = 0
        try:
            projects, files = await db.get_projectsandfiles(conn)
        except db.RecordNotFound as e:
            raise web.HTTPNotFound(text=str(e))

        return {
            'projects': projects,
            'files': files
        }


@aiohttp_jinja2.template('pipeline_method.html')
async def pipeline_method(request):
    if request.method == "POST":

        data = await request.post()
        try:
            method = data['method']
        except (KeyError, TypeError, ValueError) as e:
            raise web.HTTPBadRequest(
                text='You have not specified project value') from e

        url = request.app.router['pipeline_project'].url_for(method=method)
        return web.HTTPFound(location=url)


@aiohttp_jinja2.template('pipeline_project.html')
async def pipeline_project(request):
    method = request.match_info['method']
    if request.method == "POST":

        data = await request.post()
        try:
            project_id = int(data['project'])
        except (KeyError, TypeError, ValueError) as e:
            raise web.HTTPBadRequest(
                text='You have not specified project value') from e
        if method == 'upload':
            url = request.app.router['upload'].url_for(
                project_id=str(project_id))
            return web.HTTPFound(location=url)
        if method == 'download':
            url = request.app.router['download_files'].url_for(
                project_id=str(project_id))
            return web.HTTPFound(location=url)
        if method == 'delete':
            url = request.app.router['delete_files'].url_for(
                project_id=str(project_id))
            return web.HTTPFound(location=url)

    async with request.app['db'].acquire() as conn:
        try:
            projects = await db.get_projects(conn)
        except db.RecordNotFound as e:
            raise web.HTTPNotFound(text=str(e))

        return {
            'projects': projects,
            'method': method
        }


@aiohttp_jinja2.template('upload.html')
async def upload(request):
    project_id = request.match_info['project_id']
    if request.method == "POST":
        datetime = time.strftime(
            '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        dir_datetime = datetime.replace(":", "_")
        data = await request.multipart()

        field = await data.next()
        assert field.name == 'file'
        filename = field.filename

        basepath = dirname(dirname(os.path.abspath(__file__)))
        upload_path = os.path.join(
            basepath, 'data', str(project_id), dir_datetime)
        file_path = os.path.join(upload_path, filename)
        folder = os.path.exists(upload_path)
        if not folder:
            os.makedirs(upload_path)

        with open(file_path, 'wb') as f:
            while True:
                chunk = await field.read_chunk()
                if not chunk:
                    break
                size = + len(chunk)
                f.write(chunk)

        async with request.app['db'].acquire() as conn:
            id = await db.get_Table_rowcount(conn, Table=db.files)

            await db.save(conn, id=id, filename=filename, path=file_path, datetime=datetime, project_id=project_id)

        logging.info('{} size of {} successfully stored '''.format(filename, size))
        url = request.app.router['index'].url_for()
        return web.HTTPFound(location=url)


    async with request.app['db'].acquire() as conn:
        try:
            project = await db.get_project(conn, project_id=project_id)
        except db.RecordNotFound as e:
            raise web.HTTPNotFound(text=str(e))

        return {
            'project': project
        }


@aiohttp_jinja2.template('download_files.html')
async def download_files(request):
    async with request.app['db'].acquire() as conn:
        project_id = int(request.match_info['project_id'])
        try:
            projects, files = await db.get_projectandfiles(conn, project_id)
        except db.RecordNotFound as e:
            raise web.HTTPNotFound(text=str(e))

        return {
            'projects': projects,
            'files': files
        }


async def download(request):
    project_id = request.match_info['project_id']
    datetime = request.match_info['datetime']
    dir_datetime = datetime.replace(":", "_")
    filename = request.match_info['file_name']
    basepath = dirname(dirname(os.path.abspath(__file__)))
    file_path = os.path.join(basepath, 'data', str(
        project_id), dir_datetime, filename)
    async with aiofiles.open(file_path, 'rb') as f:
        content = await f.read()
        if content:
            response = web.Response(
                content_type='application/octet-stream',
                headers={
                    'Content-Disposition': 'attachment;filename={}'.format(filename)},
                body=content)
            return response
        else:
            return


@aiohttp_jinja2.template('create_project.html')
async def create_project(request):
    if request.method == 'POST':
        data = await request.post()
        project_name = data['create_project']
        async with request.app['db'].acquire() as conn:
            projects = await db.get_projects(conn)
            for project in projects:
                if project.project_name == project_name:
                    break

            try:
                id = await db.get_Table_rowcount(conn, Table=db.projects)
                await db.create_project(conn, id=id, project_name=project_name)
            except db.AddNewProjectFailed as e:
                raise web.HTTPNotFound(text=str(e))

        url = request.app.router['index'].url_for()
        return web.HTTPFound(location=url)


@aiohttp_jinja2.template('delete_project.html')
async def delete_project(request):
    if request.method == 'POST':
        data = await request.post()
        project_id = data['delete_project']
        async with request.app['db'].acquire() as conn:
            try:
                await db.delete_project(conn, id=project_id)
            except db.DeleteProjectFailed as e:
                pass

        url = request.app.router['index'].url_for()
        return web.HTTPFound(location=url)
    
    async with request.app['db'].acquire() as conn:
        projects = await db.get_projects(conn)

    return {
        'projects': projects
    }


@aiohttp_jinja2.template('delete_files.html')
async def delete_files(request):
    if request.method == 'POST':
        data = await request.post()
        file_id = data['file']
        async with request.app['db'].acquire() as conn:
            file_record = await db.get_filepath(conn, file_id=file_id)
            filepath = file_record['path']
            os.remove(filepath)
            os.removedirs(os.path.dirname(filepath))
            await db.delete_file(conn, file_id=file_id)

    async with request.app['db'].acquire() as conn:
        project_id = int(request.match_info['project_id'])
        try:
            project, files = await db.get_projectandfiles(conn, project_id)
        except db.RecordNotFound as e:
            raise web.HTTPNotFound(text=str(e))
        return {
            'project': project,
            'files': files
        }


@aiohttp_jinja2.template('registration.html')
async def registration(request):
    if request.method == 'POST':
        data = await request.post()
        username = data['Username']
        password = data['Password']

        async with request.app['db'].acquire() as conn:
            user_record = await db.login_user(conn, username=username)
            if user_record == None:
                id = await db.get_Table_rowcount(conn, Table=db.users)
                await db.add_user(conn, id=id, username=username, password=password)
                url = request.app.router['login'].url_for()
                return web.HTTPFound(location=url)
            else:
                url = request.app.router['registration'].url_for()
                return web.HTTPFound(location=url)


@aiohttp_jinja2.template('login.html')
async def login(request):
    if request.method == 'POST':
        data = await request.post()
        username = data['Username']
        password = data['Password']

        async with request.app['db'].acquire() as conn:
            user_record = await db.login_user(conn, username=username)
            if user_record == None:
                url = request.app.router['login'].url_for()
            else:
                if user_record['password'] == password:
                    url = request.app.router['index'].url_for()
                else:
                    url = request.app.router['login'].url_for()
            return web.HTTPFound(location=url)


@aiohttp_jinja2.template('pipeline.html')
async def pipeline(request):
    if request.method == 'POST':
        data = await request.post()
        method = data['method']
        project_id = data['project']
        if method == 'upload':
            url = request.app.router['upload'].url_for(
                project_id=str(project_id))
        if method == 'download':
            url = request.app.router['download_files'].url_for()
        if method == 'delete':
            url = request.app.router['delete_files'].url_for(project_id=str(project_id))
        return web.HTTPFound(location=url)

    async with request.app['db'].acquire() as conn:
        projects = await db.get_projects(conn)

    return {
        'projects': projects
    }
