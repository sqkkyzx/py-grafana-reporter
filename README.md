# 腾讯云对象存储与 Dagster 集成

该 Dagster 集成是为了更便捷的调用腾讯云对象存储，集成提供了一个 Dagster Resource，和一个 Op 。

## 安装
要安装库，请使用 pip 。

```bash
pip install dagster-qcloud-cos==0.1.0-alpha -U
```

## Resource

#### QcloudCosResource

该资源返回一个 CosS3Client 类，该类是腾讯云官方 Python SDK 的类，可以查看 https://cloud.tencent.com/document/product/436/12269 了解使用方法。


## OP

#### 上传 5G 大小以内的文件并获取预签名的临时链接

```python

from dagster_qcloud_cos import cos_op, QcloudCosResource
from dagster import job, Definitions


@job
def upload_file():    
    etag, presigned_url = cos_op.op_upload_file()
    
defs = Definitions(
    jobs=[upload_file],
    resources={"dingtalk_webhook": QcloudCosResource()}
)
```

###### 输入说明：
- `key`: str, 上传文件KEY
- `file`: bytes, 文件字节数据
- `expired`: int, 预签名下载链接的过期时间，0 为不获取，默认为 0
- `bucket`: str, bucket_id，默认为资源设置的bucket_id

###### 输出说明：
- `etag`
- `presigned_url`: 预签名下载链接，或空字符串

