import yaml
import requests

from typing import Union
from utils.log_utils import log
from utils.os_utils import get_env


# =================== 调试时候使用 下载 加载成dict ====================
def download_yaml(file_url:str, output_file:str) -> None:
    """
    根据file_url下载yaml文件, 并保存到本地
    """
    # 发起GET请求并下载文件
    try:
        response = requests.get(file_url, timeout=10)
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
def download_and_load_yaml(file_url:str) -> Union[str, None]:
    """
    下载yaml文件并保存在内存中,转化为字典
    这样可以减少磁盘IO, 但是会占用内存
    """
    try:
        response = requests.get(file_url, timeout=10)
        if response.status_code == 200:
            return yaml.load(response.content, Loader=yaml.FullLoader)
        else:
            log.error("下载失败, HTTP状态码: {response.status_code}")
    except requests.RequestException as e:
        log.error(f"下载文件时出错: {e}")


# =================== 合并两份yaml文件 并添加自定义规则 ====================
def merge_proxy(cutevpn_dict:dict, ikuuu_dict:dict) -> dict:
    """
    将 cutevpn_dict 和 ikuuu_dict 合并成一个字典
    1. cutevpn_dict, proxies字段中"name"字段含有"美国"或者"香港"的字典,添加到ikuuu_dict.
    2. cutevpn_dict, proxy-groups字段中"name"字段为"🔰国外流量"的，含有"美国"或者"香港"的字典,添加到ikuuu_dict.
       删除ikuuu_dict中proxy-groups字段中"name"字段为"🔰国外流量"的，不含有"美国"或者"香港"的字典.
    3. 新增OpenAI和Claude这两proxy-groups
    4. 新增rules.
    """
    def is_us_or_hk(proxy:dict) -> bool:
        """
        如果proxy是dict, "name"字段含有"美国"或者"香港", 返回True
        如果proxy是str, 含有"美国"或者"香港", 返回True
        """
        if isinstance(proxy, dict):
            return "美国" in proxy['name'] or "香港" in proxy['name']
        elif isinstance(proxy, str):
            return "美国" in proxy or "香港" in proxy
        else:
            raise TypeError("proxy必须是dict或者str类型")

    proxy_list = [proxy for proxy in cutevpn_dict['proxies'] if is_us_or_hk(proxy)]
    proxy_groups = [proxy for proxy in cutevpn_dict['proxy-groups'][0]["proxies"] if is_us_or_hk(proxy)]

    # 添加到ikuuu_dict
    ikuuu_dict['proxies'].extend(proxy_list)
    ikuuu_dict['proxy-groups'][0]["proxies"].extend(proxy_groups)

    # 删除ikuuu_dict中proxy-groups字段中"name"字段为"🔰国外流量"的，不含有"美国"或者"香港"的字典.
    ikuuu_dict['proxy-groups'][0]["proxies"] = [proxy for proxy in ikuuu_dict['proxy-groups'][0]["proxies"] if is_us_or_hk(proxy)]
    
    # 新增OpenAI和Claude这两proxy-groups
    openai = { 
        "name": "OpenAI",
        "type": "select",
        "proxies": []
        }
    claude = { 
        "name": "Claude",
        "type": "select",
        "proxies": []
        }
    # 选出所有的美国节点
    us_proxies = [proxy for proxy in ikuuu_dict['proxy-groups'][0]["proxies"] if "美国" in proxy]
    openai['proxies'].extend(us_proxies)
    claude['proxies'].extend(us_proxies)
    openai['proxies'] = ["🔰 选择节点"] + openai['proxies']
    claude['proxies'] = ["🔰 选择节点"] + claude['proxies']
    ikuuu_dict['proxy-groups'].append(openai)
    ikuuu_dict['proxy-groups'].append(claude)

    # 新增rules
    rules = ["DOMAIN-SUFFIX,arxiv.org,OpenAI",
            "DOMAIN-SUFFIX,txyz.ai,OpenAI",
            "DOMAIN-SUFFIX,bing.com,OpenAI",
            "DOMAIN-SUFFIX,openai.com,OpenAI",
            "DOMAIN-SUFFIX,bing.net,OpenAI",
            "DOMAIN-SUFFIX,anthropic.com,OpenAI",
            "DOMAIN,claude.ai,Claude",
            "DOMAIN-SUFFIX,anthropic.com,Claude",
            "DOMAIN,ai.meta.com,Claude",
            "DOMAIN,bard.google.com,Claude",
            "DOMAIN,dl.stream.qqmusic.qq.com,🔰 选择节点",
            "DOMAIN-SUFFIX,oracle.com,🔰 选择节点",
            "DOMAIN-SUFFIX,huggingface.co,🔰 选择节点",
            "DOMAIN-SUFFIX,civitai.com,🔰 选择节点",
            "DOMAIN-SUFFIX,docker.com,🔰 选择节点",
            "DOMAIN-SUFFIX,microsoft.com,🔰 选择节点",
            "DOMAIN-SUFFIX,office.com,🔰 选择节点",
            "DOMAIN-SUFFIX,akamaized.net,🌏 爱奇艺&哔哩哔哩",
            "DOMAIN-SUFFIX,hdslb.com,🌏 爱奇艺&哔哩哔哩",
            "DOMAIN-SUFFIX,bilibili.com,🌏 爱奇艺&哔哩哔哩",]

    # 将ruls插入到rules字段的第一个位置
    ikuuu_dict['rules'] = rules + ikuuu_dict['rules']

    return ikuuu_dict


# =================== 将合并好的文件进行保存 ====================
def ikuuu_yaml_dump(data, indent=2):
    """
    ikuuu的yaml保存格式
    """
    indent_str = ' ' * indent
    result = ''
    for key, value in data.items():
        if isinstance(value, dict):
            result += f"{indent_str}{key}:\n"
            result += ikuuu_yaml_dump(value, indent + 2)
        elif isinstance(value, list):
            result += f"{indent_str}{key}:\n"
            for item in value:
                result += f"{indent_str}  - {item}\n"
        else:
            result += f"{indent_str}{key}: {value}\n"
    return result


def cutevpn_yaml_dump(data, indent=2):
    """
    cutevpn的yaml保存格式
    """
    indent_str = ' ' * indent
    result = ''
    for key, value in data.items():
        if isinstance(value, dict):
            result += f"{indent_str}{key}:\n"
            result += cutevpn_yaml_dump(value, indent + 2)
        elif isinstance(value, list):
            result += f"{indent_str}{key}:\n"
            for item in value:
                if isinstance(item, dict):
                    result += f"{indent_str}  -\n"
                    result += cutevpn_yaml_dump(item, indent + 4)
                else:
                    result += f"{indent_str}  - {item}\n"
        else:
            result += f"{indent_str}{key}: {value}\n"
    return result

if __name__ == '__main__':
        
    cutevpn = get_env("CUTEVPN")
    ikuuu = get_env("IKUUU")

    # download_yaml(ikuuu, 'ikuuu.yml')
    # download_yaml(cutevpn, 'cutevpn.yml')
    # cutevpn_dict = read_yaml('cutevpn.yml')
    # ikuuu_dict = read_yaml('ikuuu.yml')
    cutevpn_dict = download_and_load_yaml(cutevpn)
    ikuuu_dict = download_and_load_yaml(ikuuu)
    merged_proxy = merge_proxy(cutevpn_dict, ikuuu_dict)

    # # 保存merge后的字典
    # with open('yhd_config.yaml', 'w', encoding='utf-8') as f:
    #     yaml.dump(merged_proxy, f, allow_unicode=True, indent=2)

    # 自定义保存格式
    # cutevpn格式会多500行左右
    yaml_str = cutevpn_yaml_dump(merged_proxy, indent=2)
    with open('yhd_config_cutevpn.yaml', 'w', encoding='utf-8') as f:
        f.write(yaml_str)
    
    yaml_str = ikuuu_yaml_dump(merged_proxy, indent=2)
    with open('yhd_config_ikuuu.yaml', 'w', encoding='utf-8') as f:
        f.write(yaml_str)
