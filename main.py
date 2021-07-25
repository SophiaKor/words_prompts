import aiohttp
import json
import time
from aiohttp import web

from fuzzy_search import Trie
from change_keyboard_layout import reverse
from sort_result import sort_result


async def websocket_handler(request):
    """Получение введенным пользователем данных и возвращение подсказки. """
    # создание префиксного дерева
    trie = Trie()
    with open('./dictionary.txt') as f:
        words = f.readlines()
    # добавляем в дерево только слова длиной больше 3 символов
    for word in words:
        word = word.split('\n')[0]
        if len(word) > 2:
            trie.add_node(word, 1)

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        start_time = time.time()
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == 'close':
                await ws.close()
            else:
                if len(msg.data) > 0:
                    result = trie.fuzzy_search(reverse(msg.data))
                    if len(result) > 1:
                        result = sort_result(result, reverse(msg.data))
                    if result:
                        await ws.send_str(json.dumps(result[:10], indent=4, ensure_ascii=False))
                        print("--- %s seconds ---" % (time.time() - start_time))
        elif msg.type == aiohttp.WSMsgType.ERROR:
            print('ws connection closed with exception %s' %
                  ws.exception())

    print('websocket connection closed')

    return ws


if __name__ == "__main__":
    app = web.Application()
    app.add_routes([web.get('/ws', websocket_handler)])
    web.run_app(app)
