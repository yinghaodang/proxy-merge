from utils.os_utils import get_env
from typing import TypedDict, List, Union


class Proxy(TypedDict):
    name: str

class ProxyGroup(TypedDict):
    name: str
    proxies: List[str]

class ConfigDict(TypedDict):
    proxies: List[Proxy]
    # proxy-groups: List[ProxyGroup]
    rules: List[str]


# =================== 合并两份yaml文件 并添加自定义规则 ====================
def merge_proxy(cutevpn_dict:ConfigDict, ikuuu_dict:ConfigDict) -> dict:
    """
    将 cutevpn_dict 和 ikuuu_dict 合并成一个字典
    1. cutevpn_dict, proxies字段中"name"字段含有"美国"或者"香港"的字典,添加到ikuuu_dict.
    2. cutevpn_dict, proxy-groups字段中"name"字段为"🔰国外流量"的，含有"美国"或者"香港"的字典,添加到ikuuu_dict.
       删除ikuuu_dict中proxy-groups字段中"name"字段为"🔰国外流量"的，不含有"美国"或者"香港"的字典.
    3. 新增OpenAI和Claude这两proxy-groups
    4. 新增rules.
    """
    def is_us_or_hk(proxy: Union[Proxy, str]) -> bool:
        """
        如果proxy是Proxy字典, "name"字段含有"美国"或者"香港", 返回True
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
    rules = [
        "DOMAIN-SUFFIX,r.stripe.com,OpenAI",
        "DOMAIN-SUFFIX,arxiv.org,OpenAI",
        "DOMAIN-SUFFIX,txyz.ai,OpenAI",
        "DOMAIN-SUFFIX,bing.com,OpenAI",
        "DOMAIN-SUFFIX,openai.com,OpenAI",
        "DOMAIN-SUFFIX,bing.net,OpenAI",
        "DOMAIN-SUFFIX,anthropic.com,Claude",
        "DOMAIN,claude.ai,Claude",
        "DOMAIN-SUFFIX,anthropic.com,Claude",
        "DOMAIN,ai.meta.com,Claude",
        "DOMAIN,bard.google.com,Claude",
        "DOMAIN-SUFFIX,easydoc.net,🇨🇳 国内网站",
        "DOMAIN-SUFFIX,vuejs.org,🇨🇳 国内网站",
        "DOMAIN-SUFFIX,gradio.app,🇨🇳 国内网站",
        "DOMAIN-SUFFIX,cn.bing.com, 🔰 选择节点",
        "DOMAIN-SUFFIX,y.qq.com,🔰 选择节点",
        "DOMAIN,dl.stream.qqmusic.qq.com,🔰 选择节点",
        "DOMAIN-SUFFIX,oracle.com,🔰 选择节点",
        "DOMAIN-SUFFIX,huggingface.co,🔰 选择节点",
        "DOMAIN-SUFFIX,civitai.com,🔰 选择节点",
        "DOMAIN-SUFFIX,docker.com,🔰 选择节点",
        "DOMAIN-SUFFIX,microsoft.com,🔰 选择节点",
        "DOMAIN-SUFFIX,office.com,🔰 选择节点",
        "DOMAIN-SUFFIX,bilivideo.com,🌏 爱奇艺&哔哩哔哩",
        "DOMAIN-SUFFIX,akamaized.net,🌏 爱奇艺&哔哩哔哩",
        "DOMAIN-SUFFIX,hdslb.com,🌏 爱奇艺&哔哩哔哩",
        "DOMAIN-SUFFIX,bilibili.com,🌏 爱奇艺&哔哩哔哩",
        ]

    # 将ruls插入到rules字段的第一个位置
    ikuuu_dict['rules'] = rules + ikuuu_dict['rules']

    return ikuuu_dict


if __name__ == '__main__':
    
    from proxy_download import download_and_load_yaml
    from proxy_save import cutevpn_yaml_dump, ikuuu_yaml_dump

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
