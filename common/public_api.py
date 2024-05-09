import json
import logging

import pytest
import requests

from conf.公共信息 import ip, user, password, file_path_xlsx, file_path_jpg
from conf.exceldata import Read

data_list = Read().get_data()
variable_dict = {}
session = requests.session()


# 封装登录
def login_data_json():
    url = f"{ip}/login"
    data = {"username": f"{user}", "password": f"{password}"}
    headers = {
        'Content-Type': 'application/json'
    }
    response = session.post(url=url, data=json.dumps(data), headers=headers, verify=False)
    lonin_data = json.loads(response.text)
    print('登录响应：', lonin_data)
    return lonin_data


# 因为网站有token，封装每次登录的token
def token_save():
    data = login_data_json()
    return data['data']['tokenMap']['access_token']


# 获取Router-Path
def get_routerpath(json_data, result):
    if isinstance(json_data, dict):
        for key, value in json_data.items():
            if key == 'menuName' and 'routeUrl' in json_data and json_data['routeUrl']:
                result[value] = json_data['routeUrl']
            elif isinstance(value, (dict, list)):
                get_routerpath(value, result)
    elif isinstance(json_data, list):
        for item in json_data:
            get_routerpath(item, result)

    return result  # 返回整理后的结果


# 封装函数，方法、url、json数据
def send_request(method, url, json_data, head):
    if method == "get":
        res = session.get(headers=head, url=url, params=json_data)
    elif method == "post":
        res = session.post(headers=head, url=url, json=json.loads(json_data))
    elif method == "delete":
        res = session.delete(headers=head, url=url, json=json_data)
    return res.json()


def send_request_form_data(url, json_data, head):
    print('针对form_data的请求')
    res = session.post(headers=head, url=url, data=json.loads(json_data))
    return res.json()


# 文件上传接口
def send_request_upload(url, head, json2):
    print('针对文件上传的请求')
    if json2 == 'test_uploadfile.xlsx':
        files = {
            'file': ('test_uploadfile.xlsx', open(file_path_xlsx, 'rb'),
                     'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        }
    elif json2 == 'test_picture.jpg':
        files = {
            'file': ('test_picture.jpg', open(file_path_jpg, 'rb'),
                     'image/jpeg')
        }
    res = session.post(headers=head, url=url, files=files)
    return res.json()


def get_data():
    print('获取数据')
    for data in data_list:
        if data[0] is not None:
            id_ = data[0].split('_')[1]
            sheet = data[0].split('_')[0]
            id = int(id_)
            module = data[1]
            name_ = data[2]
            name = str(name_)
            desc = data[3]
            method = data[4]
            url = data[5]
            json = data[6]
            variable = data[7]
            is_variable = data[8]
            expected = str(data[9])
            is_execute = data[10]
            yield id, sheet, module, name, desc, method, url, json, variable, is_variable, expected, is_execute


# 获取标题
def get_title():
    data_list1 = list(get_data())
    title_list = []
    for data in data_list1:
        module = data[2]
        # print(module)
        name_ = data[3]
        desc = data[4]
        title = f'{module}_{name_}_{desc}'
        title_list.append(title)
    print('标题列表：', title_list)
    return title_list


# 获取变量
def get_variable(method, url, json, headers):
    res = send_request(method, url, json, headers)
    return res


def find_value_by_key_index(nested_dict, target_key):
    target_key_split = target_key.split('.')
    print('用.分割的target_key：', target_key_split)
    if len(target_key_split) != 2:
        raise ValueError(f"Invalid target key format: {target_key}")

    target_key = target_key_split[0]
    print('变量名：', target_key)
    index = int(target_key_split[1])  # 获取索引信息
    print('索引：', index)
    result = []  # 存储查找结果的列表

    def find_value_in_dict(d, key):
        if isinstance(d, dict):
            for k, v in d.items():
                if k == key:
                    result.append(v)
                find_value_in_dict(v, key)
        elif isinstance(d, list):
            for item in d:
                find_value_in_dict(item, key)

    find_value_in_dict(nested_dict, target_key)

    if index < len(result):
        return result[index]
    else:
        return None  # 处理索引超出范围的情况


def find_value_by_key(nested_dict, target_key):
    """
        递归搜索嵌套字典，根据键名查找对应的值。

        :param nested_dict: 要搜索的嵌套字典
        :param target_key: 要查找的键名，支持多个键名用逗号分隔
        :return: 找到的值组成的列表，如果没有找到返回空列表
        """
    result = []  # 存储查找结果的列表
    if '.' in target_key and ',' not in target_key:
        every_key = find_value_by_key_index(nested_dict, target_key)
        result.append(every_key)
        return result
    if ',' in target_key:
        keys = target_key.split(',')
        for key_ in keys:
            if '.' in key_:
                every_key = find_value_by_key_index(nested_dict, key_)
                result.append(every_key)
            else:
                sub_result = find_value_by_key(nested_dict, key_)
                result.extend(sub_result)

    else:
        if isinstance(nested_dict, dict):
            for key, value in nested_dict.items():
                if key == target_key:
                    result.append(value)
                # 如果值是字典类型，则递归搜索
                elif isinstance(value, dict):
                    sub_result = find_value_by_key(value, target_key)
                    result.extend(sub_result)
                # 如果值是列表类型，可能列表里有字典，也进行递归搜索
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            sub_result = find_value_by_key(item, target_key)
                            result.extend(sub_result)

    return result


# 对value_str去重
def remove_duplicates(input_list):
    unique_list = []

    for item in input_list:
        if isinstance(item, list):
            # 如果元素是列表，则递归调用remove_duplicates函数
            item = remove_duplicates(item)

        if item not in unique_list:
            unique_list.append(item)
    return unique_list


def get_variable_dict(key_str, value_str1):
    global variable_dict
    if key_str is None or value_str1 is None:
        print('Key or value is None！！！！')

    if isinstance(value_str1, list):  # 只对列表进行去重处理
        value_str = remove_duplicates(value_str1)
    else:
        value_str = value_str1

    if ',' in key_str:
        keys = key_str.split(',')
        values = [str(val).strip("[]'") for val in value_str]  # 处理元素为字符串并去除方括号和单引号
        for key, value in zip(keys, values):
            variable_dict[key.strip()] = value.strip()
    else:
        variable_dict[key_str] = str(value_str).strip("[]'")  # 处理元素为字符串并去除方括号和单引号
    print('全局字典：', variable_dict)
    logging.info(f'当前全局字典为：{variable_dict}')


def get_variable_dict_list(key_str, value_str1):
    global variable_dict
    print(type(value_str1))
    print(value_str1, '11111111')

    if key_str is None or value_str1 is None:
        print('Key or value is None！！！！')

    if not isinstance(value_str1, list):  # 如果不是列表，则转换为列表
        value_str = [value_str1]
    else:
        value_str = value_str1

    if ',' in key_str:
        keys = key_str.split(',')
        values = [str(val).strip("[]'") for val in value_str]  # 处理元素为字符串并去除方括号和单引号
        for key, value in zip(keys, values):
            variable_dict[key.strip()] = [value.strip()]  # 存入字典的值为列表
    else:
        variable_dict[key_str] = [str(val).strip("[]'") for val in value_str]  # 存入字典的值为列表

    print('全局字典：', variable_dict)
    logging.info(f'当前全局字典为：{variable_dict}')


# 获取变量的值,替换传参中的变量值
def replace_value_by_key(target_keys, data_str, method):
    global variable_dict
    if isinstance(data_str, dict):
        data_dict = data_str
    else:
        data_dict = json.loads(data_str)
    if '.' in target_keys:
        target_key_new = target_keys.split('.')[0]
        get_variable_dict(target_key_new, variable_dict.get(target_keys))
        data_dict = replace_value_by_key_helper(target_key_new, data_dict)
    target_keys = target_keys.split(',') if ',' in target_keys else [target_keys]

    for target_key in target_keys:
        data_dict = replace_value_by_key_helper(target_key, data_dict)
    if method == 'post':
        result_json = json.dumps(data_dict)
        return result_json
    return data_dict


def replace_value_by_key_helper(target_key, data):
    global variable_dict
    if isinstance(data, dict):
        for key, value in data.items():
            if key == target_key:
                data[key] = variable_dict.get(target_key, value)
            elif isinstance(value, (dict, list)):
                data[key] = replace_value_by_key_helper(target_key, value)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, (dict, list)):
                data[i] = replace_value_by_key_helper(target_key, item)
    return data


def parse_params(input_str):
    params = {}
    pairs = input_str.split('&')  # 按照 '&' 符号拆分字符串
    for pair in pairs:
        key_value = pair.split('=')
        key = key_value[0]
        value = key_value[1]
        if key in params:
            # 如果键已经存在于字典中，则将新值添加到值的列表中
            if isinstance(params[key], list):
                params[key].append(value)
            else:
                params[key] = [params[key], value]
        else:
            # 如果键不存在于字典中，则直接赋值
            params[key] = value
    return params


# 给定一个key，从全局字典中获取它对应的值
def get_variable_dict_by_key(key):
    if key in variable_dict:
        return variable_dict[key]
    return None


# 变量再次赋值
def replace_variable_too(variable):
    processed_variables = []  # 存储处理后的变量
    if ',' in variable:
        variables = variable.split(',')
        for var in variables:
            processed_var = replace_variable_too(var)  # 递归处理每个变量
            processed_variables.extend(processed_var)  # 将处理后的变量列表扩展到结果列表中
    else:
        if '+' in variable and '=' in variable:
            variable_ = variable.split('=')
            left_variable = variable_[0]
            right_variables = variable_[1].split('+')
            right_variables_list = []
            for right_variable in right_variables:
                if right_variable in variable_dict:
                    value = variable_dict.get(right_variable)
                    right_variables_list.append(value)
            get_variable_dict_list(left_variable, right_variables_list)
            processed_variables.append(left_variable)  # 将左变量加入列表
        else:
            if '=' not in variable:
                value = variable_dict.get(variable)
                if value is not None:
                    get_variable_dict(variable, value)
                processed_variables.append(variable)  # 将变量加入列表
            else:
                variable_ = variable.split('=')
                left_variable = variable_[0]
                right_variable = variable_[1]
                value = variable_dict.get(right_variable)
                if value is not None:
                    get_variable_dict(left_variable, value)
                processed_variables.append(left_variable)  # 将左变量加入列表
    return processed_variables  # 返回处理后的所有变量


# 判断使用变量
def judge_variable(method, json1, data9):
    if method == 'get' and json1:
        json1 = parse_params(json1)
        logging.info(f'替换后的json1: {json1}')
    if '=' in data9:
        left_keys = replace_variable_too(data9)  # 返回左侧变量组成的列表
        logging.info(f'返回的左侧变量组成的列表: {left_keys}')
        if isinstance(left_keys, list):
            for left_key in left_keys:
                if isinstance(left_key, list):
                    json1 = replace_value_by_key(left_key[0], json1, method)
                json1 = replace_value_by_key(left_key, json1, method)
        else:
            json1 = replace_value_by_key(left_keys, json1, method)
    else:
        if isinstance(json1, list):
            json1 = list_json_replace(json1, data9)
            return json1
        json1 = replace_value_by_key(data9, json1, method)
    return json1


# 针对报表选择设备
def list_json_replace(json1, data9):
    global variable_dict
    json1 = []
    if '.' in data9:
        if '+' in data9:
            keys = data9.split('+')
            for key in keys:
                json1.append(variable_dict.get(key))
        else:
            json1.append(variable_dict.get(data9))
    return json1


if __name__ == '__main__':
    aa = '{"userId":"532387166576709"}'
