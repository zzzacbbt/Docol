import aiohttp_jinja2
from aiohttp import web



async def handle_404(request):
    return aiohttp_jinja2.render_template('404.html', request, {})


async def handle_500(request):
    return aiohttp_jinja2.render_template('500.html', request, {})


def create_error_middleware(overrides):
    @web.middleware
    async def error_middleware(request, handler):
        try:
            response = await handler(request)
            override = overrides.get(response.status)
            if override:
                return await override(request)
            return response
        except web.HTTPException as ex:
            override = overrides.get(ex.status)
            if override:
                return await override(request)
            raise
    return error_middleware


def setup_middlewares(app):
    error_middleware = create_error_middleware({
        404: handle_404,
        500: handle_500
    })
    app.middlewares.append(error_middleware)


async def login_middlewares(app, handler):
    async def login(request):
        cookie = request.cookies.get('docol_cookie')
        rel_url = str(request.rel_url)
        if cookie == '1234' or rel_url == '/login' :
            response = await handler(request)
            return response
         
        else:
            url = request.app.router['login'].url_for()
            response = web.HTTPFound(location=url)
            return response
    return login