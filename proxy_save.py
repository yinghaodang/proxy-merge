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