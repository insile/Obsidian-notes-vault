from pathlib import Path
import requests
import execjs
import time


def get_sign(imp):
    inputData = imp
    with open("code.js") as f:
        jsData = f.read()
    sign = execjs.compile(jsData).call("e", inputData)  # 调用js代码中的 e函数，传入参数为 inputData
    # print(sign)
    return sign

def main(obsidian_path, txt_path, cookie, AcsToken, token,sleeptime):
    obsidian_path.mkdir(exist_ok=True)
    (obsidian_path / 'words').mkdir(exist_ok=True)
    with open(txt_path, encoding='utf-8') as f:
        lst = f.readlines()
    num = 0

    # 遍历单词
    for i in lst:
        time.sleep(sleeptime)
        keyword = i.strip()
        # url
        post_url = 'https://fanyi.baidu.com/v2transapi?from=en&to=zh'

        # 请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.29',
            'Acs-Token': AcsToken,  # 参数 Acs-Token
            'cookie': cookie  # 参数 cookie
        }

        # post表单
        datas = {
            'from': 'en',
            'to': 'zh',
            'query': keyword,
            'transtype': 'translang',
            'simple_means_flag': 3,
            'sign': get_sign(keyword),
            'token': token,  # 参数 token
            'domain': 'common',
            'ts': int(time.time())
        }

        # 请求发送
        try:
            respones = requests.post(url=post_url, data=datas, headers=headers)
            # 获取响应数据 json
            dic_obj = respones.json()
            a = dic_obj['dict_result']['simple_means']['symbols'][0]
            with open(obsidian_path / 'words' / f'{keyword}.md', 'w', encoding='utf-8') as md:
                # 音标
                if a.get("ph_en") and a.get("ph_am"):
                    md.write(f'- 英：/{a.get("ph_en")}/； 美：/{a.get("ph_am")}/\n')

                # 词义
                for mean in a['parts']:
                    if mean.get("part") and mean.get("means"):
                        md.write(f'- {mean["part"]}\n')
                        md.write(f'\t- {";".join(mean["means"])}\n')
                    elif mean.get("part_name") and mean.get("means"):
                        md.write(f'- 词性缺失\n')
                        md.write(f'\t- {";".join(mean["means"])}\n')

                # 例句
                f = 0
                while not dic_obj.get('liju_result').get('double') and f <= 3:
                    respones = requests.post(url=post_url, data=datas, headers=headers)
                    dic_obj = respones.json()
                    f += 1
                if dic_obj.get('liju_result').get('double'):
                    md.write(f'---\n')
                    b = eval(dic_obj['liju_result']['double'])
                    count1 = 0
                    for liju in b:
                        count1 += 1
                        count2 = 0
                        for lijulang in liju:
                            if count2:
                                tab = '\t'
                                sep = ''
                            else:
                                tab = ''
                                sep = ' '
                            txt = f'{sep}'.join(list(map(list, zip(*lijulang)))[0])
                            md.write(f'{tab}- {txt}\n')
                            count2 += 1
                            if count2 >= 2:
                                break
                        if count1 >= 3:
                            break

                # 特殊词形
                md.write(f'---\n')
                if dic_obj.get("dict_result").get("simple_means").get("exchange"):
                    for i in dic_obj.get("dict_result").get("simple_means").get("exchange").items():
                        if i[0] and i[1]:
                            md.write(f'- {i[0]}: {i[1][0]}\n')

            num += 1
            print(f'{num}: {keyword} 完成')

        except:
            with open(obsidian_path / 'error.txt', 'a', encoding='utf-8') as error:
                error.write(f'{keyword}\n')
            print(f'{keyword} 错误')
            num += 1

if __name__ == '__main__':
    obsidian_path = Path(r"C:\Users\Desktop\英语")  # obsidian 仓库路径
    txt_path = obsidian_path / '考研四六级.txt'  # 单词表路径
    cookie = 'cookie'
    AcsToken = 'AcsToken'
    token = 'token'
    sleeptime = 0.5
    main(obsidian_path, txt_path, cookie, AcsToken, token, sleeptime)


