#views.py
from aiohttp import web
import db
import aiohttp_jinja2
import os

async def index(request):
    return web.Response(text='Test')


@aiohttp_jinja2.template('detail.html')
async def poll(request):
    async with request.app['db'].acquire() as conn:
        question_id = request.match_info['question_id']
        try:
            question, choices = await db.get_question(conn,question_id)
        except db.RecordNotFound as e:
            raise web.HTTPNotFound(text=str(e))
        return {
            'question': question,
            'choices': choices
        }


@aiohttp_jinja2.template('results.html')
async def results(request):
    async with request.app['db'].acquire() as conn:
        question_id = request.match_info['question_id']

        try:
            question, choices = await db.get_question(conn,
                                                      question_id)
        except db.RecordNotFound as e:
            raise web.HTTPNotFound(text=str(e))

        return {
            'question': question,
            'choices': choices
        }


async def vote(request):
    async with request.app['db'].acquire() as conn:
        question_id = int(request.match_info['question_id'])
        data = await request.post()
        try:
            choice_id = int(data['choice'])
        except (KeyError, TypeError, ValueError) as e:
            raise web.HTTPBadRequest(
                text='You have not specified choice value') from e
        try:
            await db.vote(conn, question_id, choice_id)
        except db.RecordNotFound as e:
            raise web.HTTPNotFound(text=str(e))
        router = request.app.router
        url = router['results'].url_for(question_id=str(question_id))
        return web.HTTPFound(location=url)


@aiohttp_jinja2.template('upload.html')
async def upload(request):
    if request.method == "POST":
        data = await request.multipart() 
        field = await data.next()
        assert field.name == 'name'
        name = await field.read(decode=True)
        
        field = await data.next()
        assert field.name == 'mp3'
        filename = field.filename

        filename = data['file'].filename
        input_file = data['file'].file
        basepath = os.path.dirname(os.path.abspath(__file__)+"/../../")
        upload_path = os.path.join(basepath, 'data', filename)
        

        
    async with request.app['db'].acquire() as conn:
        project_id = int(request.match_info['project_id'])
        try:
            projects, files = await db.get_project(conn,project_id)
        except db.RecordNotFound as e:
            raise web.HTTPNotFound(text=str(e))

        return {
            'projects': projects,
            'files': files
        }        
