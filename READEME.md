# 概述

使用无头浏览器来截图 Grafana 页面实现渲染仪表盘图像的目的。

# 安装

环境需要 playwright

```bash
pip instll playwright py-grafana-render
playwright install
playwright install-dev
```

# 使用

在你的代码中引用：

```python
from py_grafana_render import GrafanaRender

# 此处传入 Grafana 服务账户的 Token
gf = GrafanaRender(token="<your-grafana-service-token>", browser="firefox")
title, image_bytes = gf.snapshot(
    url="https://<your-domain>/d/<dashboard>?xxx=xxx&kiosk",
    file_path="./test.png"
)
```

### 参数说明

##### GrafanaRender

| 参数名     | 必填 | 类型  | 默认值     | 说明                                       |
|---------|----|-----|---------|------------------------------------------|
| token   | 是  | str |         | Grafana 服务账户的 Token                      |
| browser |    | str | firefox | 使用的无头浏览器，可选值：<br/>- chrome<br/>- firefox | 

##### snapshot

参数：

| 参数名                | 必填 | 类型   | 默认值  | 说明                                                          |
|--------------------|----|------|------|-------------------------------------------------------------|
| url                | 是  | str  |      | Grafana 的页面，可以包含查询字符串，不限仪表盘或面板。                             |
| width              |    | int  | 762  | 截图宽度。                                                       | 
| height             |    | int  | 300  | 截图高度。若开启自动高度，则仪表盘将使用自动高度，面板内容高度小于默认高度时使用默认高度，大于默认高度时使用自动高度。 | 
| auto_height        |    | bool | True | 自动获取实际高度，如果无法自动获取，仅会使用默认高度。                                 | 
| auto_height_offset |    | int  | 150  | 自动获取的高度，会因为存在顶部筛选器导致误差，使用该值对自动高度进行一定偏移。                     | 
| hide_class         |    | list | None | 隐藏的样式选择器列表，比如 .css-k3l5qq 是 v11.3.1 的顶部筛选器栏。                | 
| filetype           |    | str  | png  | 可选 png 或 jpeg                                               | 
| file_path          |    | str  | None | 截图文件保存路径，需要包括文件名的完整路径。可以不传入，获取返回的字节流后自行保存。                  | 

返回:

- 标题：str 浏览器页面标题，需自行处理
- 图片字节流：bytes 当不传入 file_path 时，可以自行存储字节流，比如发送到 s3 存储等。


> 提示：
> 若希望全屏，需要自行在 url 中加入 kiosk 查询字符串。
