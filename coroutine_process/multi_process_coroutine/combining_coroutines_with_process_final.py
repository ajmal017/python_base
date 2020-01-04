import asyncio
import concurrent.futures
import logging
import sys
import time
import asyncio
import aiohttp
import time
from aiomultiprocess import Pool
import requests
import numpy as np
import sys
import time
from concurrent import futures
from random import randrange
from coroutine_process.multi_process_coroutine.arcfour import arcfour
JOBS = 12
SIZE = 2**18

KEY = b"'Twas brillig, and the slithy toves\nDid gyre"
STATUS = '{} workers, elapsed time: {:.2f}s'
async def arcfour_test(size, key):
    in_text = bytearray(randrange(256) for i in range(size))
    cypher_text = arcfour(key, in_text)
    out_text = arcfour(key, cypher_text)
    assert in_text == out_text, 'Failed arcfour_test'
    return size

async def compute_dot():
    print('go compute')
    res=np.dot(np.random.random((7000, 1000)), np.random.random((1000, 7000)))
    print('res',res)
    return res


async def get(url):
    session = aiohttp.ClientSession()
    response = await session.get(url)
    result = await response.text()
    # result_temp=await compute_dot()
    # result=str(result)+str(result_temp)
    #在close前加上await否则显示close is not awaited
    await session.close()
    return result
def sub_loop(urls):
    log = logging.getLogger('run_subloop')
    log.info('go sub_loop')

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    tasks_cpu=[]
    # tasks = [get(url) for url in urls]
    for i in range(JOBS, 0, -1):
        size = SIZE + int(SIZE / JOBS * (i - JOBS / 2))
        tasks_cpu.append(arcfour_test( size, KEY))
    # tasks.extend(tasks_cpu)
    tasks=tasks_cpu
    results = loop.run_until_complete(asyncio.gather(*tasks))

    ##这是所有的任务已经完成了
    print('res000',results)
    # for num, result in results:
    #     print('fetch({}) = {}'.format(num, result))
    return results


async def run(executor, urls=None):
    log = logging.getLogger('run_blocking_tasks')
    log.info('starting')
    log.info('creating executor tasks')
    loop = asyncio.get_event_loop()
    url = 'http://127.0.0.1:5000'
    urls = [url for _ in range(100)]
    print('excutor',executor)
    results=await loop.run_in_executor(executor, sub_loop,urls)

    # await asyncio.get_event_loop().run_in_executor(executor, sub_loop,urls)
    # results = [t.result() for t in completed]
    log.info('results: {!r}'.format(results))
    print('gogo')

if __name__ == '__main__':
    start=time.time()
    # Configure logging to show the id of the process
    # where the log message originates.
    logging.basicConfig(
        level=logging.INFO,
        format='PID %(process)5s %(name)18s: %(message)s',
        stream=sys.stderr,
    )

    # Create a limited process pool.
    executor = concurrent.futures.ProcessPoolExecutor(
        max_workers=2,
        #max_workers=1,36.5468909740448
        #4,34.53132891654968
    )

    event_loop = asyncio.get_event_loop()
    try:
        ss=time.time()
        event_loop.run_until_complete(
            # run_blocking_tasks(executor)
            # run_blocking_tasks_request(executor)
            run(executor)
        )
        print('{} workers cost time final'.format(executor._max_workers),time.time()-ss)
    finally:
        event_loop.close()
    print(time.time()-start)#100个url,10进程耗时32s

'''
这个程序虽然能运行但是逻辑上不是我想要的，因为这里开一个进程时，就是按照顺序进行的，并没有异步的进行
（可能是time.sleep造成的，也就是我的调用方法错误造成的么）；
但是多个进程确实进行了并行处理
###这里的逻辑估计是多个进程，每个进程独立并行的运行并控制多个协程

##要求对于多并发IO高效，同样要求对于cpu密集型，能体现出多进程的优势


'''
