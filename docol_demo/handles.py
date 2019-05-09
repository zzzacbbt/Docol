#views.py
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
            projects, files = await db.get_project(conn,project_id)
        except db.RecordNotFound as e:
            raise web.HTTPNotFound(text=str(e))

        return {
            'projects': projects,
            'files': files
        }   
    return web.Response(text='Test')



@aiohttp_jinja2.template('choose_project.html')
async def choose_project(request):
    if request.method == "POST":
        data = await request.post()
        try:
            project_id = int(data['project'])
        except (KeyError, TypeError, ValueError) as e:
            raise web.HTTPBadRequest(
                text='You have not specified project value') from e
        
        url = request.app.router['upload'].url_for(project_id=str(project_id))
        return web.HTTPFound(location=url)


    async with request.app['db'].acquire() as conn:
        try:
            projects = await db.get_projects(conn)
        except db.RecordNotFound as e:
            raise web.HTTPNotFound(text=str(e))

        return {
            'projects': projects
        }

@aiohttp_jinja2.template('upload.html')
async def upload(request):
    
    if request.method == "POST":
        date = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        data = await request.multipart() 
        
        field = await data.next()
        assert field.name == 'file'
        filename = field.filename

        basepath = dirname(dirname(os.path.abspath(__file__)))
        upload_path = os.path.join(basepath, 'data', filename)
        
        
        with open(upload_path, 'wb') as f:
            while True:
                chunk = await field.read_chunk()
                if not chunk:
                    break
                size = + len(chunk)
                f.write(chunk)

        
        async with request.app['db'].acquire() as conn:        
            result = await conn.execute("SELECT * FROM files")
            project_id = int(request.match_info['project_id'])
            id = result.rowcount
            await db.save(conn, id=id, filename=filename, path=upload_path, date=date, project_id=project_id)

        return web.Response(text='{} size of {} successfully stored '''.format(filename,size))


    async with request.app['db'].acquire() as conn:
        try:
            projects = await db.get_projects(conn)
        except db.RecordNotFound as e:
            raise web.HTTPNotFound(text=str(e))

        return {
            'projects': projects
        }
        

def query_parse(req):
    obj = req.query_string
    queryitem = []
    if obj:
        query = req.query.items()
        for item in query:
            queryitem.append(item)
        return dict(queryitem)
    else:
        return None


@aiohttp_jinja2.template('download.html')
async def download(request):
    async with request.app['db'].acquire() as conn:
        project_id = int(request.match_info['project_id'])
        try:
            projects, files = await db.get_project(conn,project_id)
        except db.RecordNotFound as e:
            raise web.HTTPNotFound(text=str(e))

    query = query_parse(request)
    filename = query.get('file')
    async with aiofiles.open(files[1].path, 'rb') as f:
        content = await f.read()
        if content:
            response = web.Response(
                content_type='application/octet-stream',
                headers={'Content-Disposition': 'attachment;filename={}'.format(filename)},
                body=content)
        else:
            return
            
    return {
        'projects': projects,
        'files': files
    }        