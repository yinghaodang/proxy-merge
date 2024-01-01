import os
from typing import Union

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse

from proxy_merge import download_and_load_yaml, merge_proxy, cutevpn_yaml_dump

# 加载.env文件中的环境变量
load_dotenv()

# 创建 FastAPI 应用实例
app = FastAPI()

def parse_url(url: str) -> Union[str, None]:
    """
    处理输入的url, 如果是""开头结尾的，进行处理
    """

    if url.startswith('"') and url.endswith('"'):
        url = url[1:-1]
    elif url.startswith("'") and url.endswith("'"):
        url = url[1:-1]

    # 检测字符串是否以 "http://" 开头
    if url.startswith('http://') or url.startswith('https://'):
        return url

@app.get("/")
def get_proxy_config():
    cutevpn = os.getenv('CUTEVPN')
    ikuuu = os.getenv("IKUUU")
    
    cutevpn  = parse_url(cutevpn)
    ikuuu  = parse_url(ikuuu)
    
    cutevpn_dict = download_and_load_yaml(cutevpn)
    ikuuu_dict = download_and_load_yaml(ikuuu)
    merged_proxy = merge_proxy(cutevpn_dict, ikuuu_dict)

    yaml_str = cutevpn_yaml_dump(merged_proxy, indent=2)

    # 将字符串保存为文件
    with open("proxy_config.yaml", "w") as file:
        file.write(yaml_str)

    # 返回文件
    return FileResponse("proxy_config.yaml")
