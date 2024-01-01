import datetime
import os
import sys


def join_dir_path_with_mk(path: str, *subs) -> str:
    """
    拼接目录路径和子目录
    如果拼接后的目录不存在 则创建
    :param path: 目录路径
    :param subs: 子目录路径 可以传入多个表示多级
    :return: 拼接后的子目录路径
    """
    target_path = path
    for sub in subs:
        if sub is None:
            continue
        target_path = os.path.join(target_path, sub)
        if not os.path.exists(target_path):
            os.mkdir(target_path)
    return target_path


def get_path_under_work_dir(*sub_paths: str) -> str:
    """
    获取当前工作目录下的子目录路径
    :param sub_paths: 子目录路径 可以传入多个表示多级
    :return: 拼接后的子目录路径
    """
    return join_dir_path_with_mk(get_work_dir(), *sub_paths)


def get_work_dir() -> str:
    """
    返回项目根目录的路径 main.py所在
    :return: 项目根目录
    """
    dir_path: str = os.path.abspath(__file__)
    up_times = 2  # 向上返回两层目录
    for _ in range(up_times):
        dir_path = os.path.dirname(dir_path)
    return dir_path


def get_env(key: str) -> str:
    """
    获取环境变量
    :param key: key
    :return: value
    """
    return os.environ.get(key)


def get_env_def(key: str, dft: str) -> str:
    """
    获取环境变量 获取不到时使用默认值
    :param key: key
    :param dft: 默认值
    :return: value
    """
    val = get_env(key)
    return val if val is not None else dft


def is_debug() -> bool:
    """
    判断当前是否在debug模式
    环境变量 DEBUG = 1
    :return: 是否在debug模式
    """
    return '1' == get_env_def('DEBUG', '0')
