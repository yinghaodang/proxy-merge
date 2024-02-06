import yaml
import requests

from typing import Union
from utils.log_utils import log


# =================== 调试时候使用 下载 加载成dict ====================
def download_yaml(file_url: str, output_file: str, proxy: dict = None) -> None:
    """
    根据file_url下载yaml文件, 并保存到本地。支持通过代理下载。

    参数:
    - file_url: 要下载的yaml文件的URL。
    - output_file: 本地保存文件的路径。
    - proxy: 可选，代理服务器的字典，格式为{'http': 'http://代理IP:端口', 'https': 'https://代理IP:端口'}。
    """
    try:
        response = requests.get(file_url, proxies=proxy, timeout=10)
        if response.status_code == 200:
            with open(output_file, 'wb') as file:
                file.write(response.content)
            print(f"文件 '{output_file}' 下载完成。")
        else:
            print(f"下载失败, HTTP状态码: {response.status_code}")
    except requests.RequestException as e:
        print(f"下载文件时出错: {e}")


def read_yaml(file_path:str) -> Union[str, None]:
    """
    读取yaml文件, 返回字典
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.load(f, Loader=yaml.FullLoader)
    

# =================== 实际运行时使用 下载 加载成dict ====================
def download_and_load_yaml(file_url:str, proxy: dict = None) -> Union[str, None]:
    """
    下载yaml文件并保存在内存中,转化为字典
    这样可以减少磁盘IO, 但是会占用内存
    """
    response = requests.get(file_url,proxies=proxy , timeout=10)
    if response.status_code == 200:
        return yaml.load(response.content, Loader=yaml.FullLoader)
    else:
        log.error("下载失败, HTTP状态码: {response.status_code}")