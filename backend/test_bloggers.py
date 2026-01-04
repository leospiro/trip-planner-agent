"""测试博主 RSSHub 订阅"""
import urllib.request
import sys

bloggers = [
    ('593032945e87e77791e03696', '小宇菇菇'),
    ('5aec57f04eacab43557f7b77', '嬉游小助理'),
    ('52f59215b4c4d66b2eafa21d', '小墨与阿猴'),
    ('5acf498411be105586e79b4c', '这里是新疆'),
    ('5bf9ff7e999837000189d106', '房琪kiki'),
    ('616cdf5a000000001f03a074', '小羊爱溜达'),
    ('5af05c664eacab116931c0d0', '小鹿Lawrence'),
    ('5f0a7dfb0000000001007eaa', 'Linksphotograph'),
    ('6613e7610000000003033ddc', '贝贝贝贝贝'),
    ('64239daf00000000120120dd', '旅行搭子小爱酱'),
    ('5ffd4e370000000001008dbc', 'Eden的环球旅行'),
]

results = []
print('博主ID测试结果:')
print('='*70)

for bid, name in bloggers:
    url = f'http://localhost:1200/xiaohongshu/user/{bid}/notes'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read().decode('utf-8')
            if '<item>' in data:
                count = data.count('<item>')
                status = 'OK'
                print(f'[OK]   {name:20} | {bid} | 笔记: {count}')
            else:
                status = 'EMPTY'
                count = 0
                print(f'[EMPTY] {name:20} | {bid} | 无笔记')
    except urllib.error.HTTPError as e:
        status = f'HTTP{e.code}'
        count = 0
        print(f'[FAIL] {name:20} | {bid} | HTTP {e.code}')
    except Exception as e:
        status = 'ERROR'
        count = 0
        print(f'[FAIL] {name:20} | {bid} | {type(e).__name__}')
    results.append((name, bid, status, count))
    sys.stdout.flush()

print('='*70)
ok_count = sum(1 for r in results if r[2] == 'OK')
print(f'总计: {ok_count}/{len(bloggers)} 个博主有效')
