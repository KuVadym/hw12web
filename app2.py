import aiohttp
import asyncio
from bs4 import BeautifulSoup
import aiohttp_jinja2
import jinja2
from aiohttp import web
import pathlib
from settings import urls
from aiohttp.web import Application

BASE_DIR = pathlib.Path(__file__).parent
app = web.Application()
aiohttp_jinja2.setup(app,
                     loader=jinja2.FileSystemLoader(str(BASE_DIR / 'templates')))

async def get_page(session, url):
    async with session.get(url, ssl=False) as response:
        return await response.text()

def handler(data, num):
    list_of_news_dict=[]
    for row in data:
        print(row)
        news_dict = {}
        if len(str(row).split('"')) > 3:
            news_dict[row.string] = str(row).split('"')[num]
            list_of_news_dict.append(news_dict)
    return list_of_news_dict

async def get_all(session, urls):
    tasks = []
    for url in urls:
        task = asyncio.create_task(get_page(session, url))
        tasks.append(task)
    results = await asyncio.gather(*tasks)
    return results


async def main(urls):
    async with aiohttp.ClientSession() as session:
        data = await get_all(session, urls)
        return data

def parse(results):
    list_of_news_dict=[]
    for html in results:
        soup = BeautifulSoup(html)
        data = soup.find_all("h3", limit=5)
        if data:
            list_of_news_dict.extend(handler(data, 3))
        else:
            data = soup.find_all("h2", limit=5)
            if data:
                list_of_news_dict.extend(handler(data, 5))
    return list_of_news_dict  

@aiohttp_jinja2.template('index.html')
def index(request):
    n = app["news"]
    return {"news": n}

def setup_routes(app: Application):
    app.router.add_get('/', index, name='index')

if __name__ == "__main__":
    urls = urls
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    results = asyncio.run(main(urls))
    news = parse(results)
    app["news"] = news
    setup_routes(app)
    web.run_app(app)
