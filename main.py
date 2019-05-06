''' Create a aiohttp server '''
from aiohttp import web

def main():
    app = web.Application()
    web.run_app(app)


if __name__ == "__main__":
    main()



