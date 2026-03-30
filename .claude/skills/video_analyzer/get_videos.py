from bilibili_api import user, sync

# UP 主 UID: 208861 (灵剑2011)
u = user.User(208861)

# 获取视频列表
videos = sync(u.get_videos())

print(f"获取到 {len(videos['list']['vlist'])} 个视频")
print("\n最新 18 个视频：")
print("-" * 80)

for i, v in enumerate(videos['list']['vlist'][:18], 1):
    bvid = v['bvid']
    title = v['title']
    url = f"https://www.bilibili.com/video/{bvid}"
    print(f"{i}. {title}")
    print(f"   {url}")

# 保存到文件
with open('video_urls.txt', 'w', encoding='utf-8') as f:
    for v in videos['list']['vlist'][:18]:
        f.write(f"https://www.bilibili.com/video/{v['bvid']}\n")

print("\n链接已保存到 video_urls.txt")
