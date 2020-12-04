import requests

def download_file(url_list):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0'
    }
    proxies = {
        'http': 'socks5h://127.0.0.1:1080',
        'https': 'socks5h://127.0.0.1:1080'
    }
    available_websites = []
    error_websites = []
    for url in url_list:
        try:
            response = requests.get(url, headers=headers, proxies=proxies, verify=False)
            if response.status_code == 200:
                available_websites.append(url)
                print("available_website:", url)
            else:
                error_websites.append(url)
                print("error_website:", url)
        except:
            error_websites.append(url)
            print("error_website:", url)

    print(available_websites)
    print(error_websites)

def read10000():
    filepath = "/media/zyan/文档/毕业设计/top10000.csv"
    url_list = []
    with open(filepath, "r") as f:
        for line in f.readlines():
            line = line.strip('\n')  # 去掉列表中每一个元素的换行符
            url_list.append("https://www." + line.split(',')[-1])
    f.close()
    print(url_list)
    for item in url_list:
        print(item)
    # download_file(url_list)

read10000()