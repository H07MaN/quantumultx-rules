# Quantumult X 国内 App 与网页去广告

本仓库是 fmz200/wool_scripts 的去广告子集，原作者为奶思及其上游贡献者，采用 GPL-3.0。不是从零原创规则，也不是全 App 去广告保证。

## 订阅地址

1. HTTPS 重写（添加到“重写 → 引用/资源”）：

https://raw.githubusercontent.com/H07MaN/quantumultx-rules/main/china-adblock.snippet

2. 广告域名（添加到“分流 → 引用/资源”）：

https://raw.githubusercontent.com/H07MaN/quantumultx-rules/main/china-adblock.list

两个资源一起使用。不要把它们添加到服务器订阅。分流资源不设置策略偏好，不强制改成 direct；保留每条规则自身的 reject 策略。使用规则分流模式。

如果手动编辑现有配置，将下方两行分别加入已经存在的对应段。不要用这个片段替换整个配置，也不要重复创建同名段。

```ini
[filter_remote]
https://raw.githubusercontent.com/H07MaN/quantumultx-rules/main/china-adblock.list, tag=国内广告域名, update-interval=86400, opt-parser=false, enabled=true

[rewrite_remote]
https://raw.githubusercontent.com/H07MaN/quantumultx-rules/main/china-adblock.snippet, tag=国内广告HTTPS重写, update-interval=86400, opt-parser=false, enabled=true
```

将广告分流资源排在可能提前命中的国内直连等宽泛分流之前，并检查既有本地直连规则是否提前命中。

## 证书与开关

1. 在 Quantumult X 的 MitM/HTTPS 解密设置中生成自己的 CA 证书，并使用安装证书入口。
2. 到 iPhone“设置 → 通用 → VPN 与设备管理”安装刚下载的描述文件。
3. 到“设置 → 通用 → 关于本机 → 证书信任设置”，为刚安装的 Quantumult X 证书开启完全信任。
4. 返回 Quantumult X，开启 MitM 和重写，启用两个资源并更新。重写资源已附 hostname，不需要设为 `*`。
5. 完全退出目标 App 后重新打开。开屏广告可能来自本地缓存，必要时清除该 App 缓存再试；无需为此直接删除整个 App。

证书在手机本地生成，仓库没有 p12、私钥或密码。不要把含这些字段的完整配置上传到公开仓库。不同 Quantumult X / iOS 版本入口名称可能略有变化。

## 本次构建范围

- 1,306 条原生重写规则，包括 reject 系列和两条选定的广告响应字段替换。
- 8,505 条域名拦截规则；删除了命中本重写服务主机的部分域名拦截冲突。
- 817 个去重的 MitM 主机名/模式，取自保留规则所属分组与上游已启用主机名的交集。分组中可能仍包含只供其他规则使用的主机名，并非逐个实测清单。
- 选取了 511 个上游分组中的规则。分组数不等于支持或实测通过的 App 数。
- 包括百度系、知乎、小红书、京东、部分微信公众号推广接口，以及许多开屏、弹窗与广告联盟接口；每个 App 只覆盖保留下来的路径。
- 这版没有远程 JavaScript；依赖脚本才能清理的混合信息流广告，不在本版完整覆盖范围。微博与抖音等不能宣称全部去广告。
- 域名规则适用于网页加载的广告请求；HTTPS 重写针对列出的路径，不是通用网页元素隐藏器，因此可能留下广告空位。

本次仅通过静态格式、正则编译和去重检查，未在真实 iPhone/App 中测试。上游规则也可能因 App 版本、接口更新或证书锁定失效。若某 App 开启后出现联网异常，先停用本重写资源复测，确认是证书解密还是某条规则导致，再按主机名或请求路径定位；不要盲目把整个域名强制直连。

## 更新与来源

本仓库由已设置的 ChatGPT 定时任务每 7 天检查上游并在校验通过后发布；没有部署 GitHub Actions 工作流。`update-interval=86400` 让 Quantumult X 每天检查本仓库的已发布版本。

- 原始重写：https://github.com/fmz200/wool_scripts/blob/main/QuantumultX/rewrite/rewrite.snippet
- 原始分流：https://github.com/fmz200/wool_scripts/blob/main/QuantumultX/filter/filter.list
- 官方格式：https://github.com/crossutility/Quantumult-X/blob/master/sample.conf
- 官方重写示例：https://github.com/crossutility/Quantumult-X/blob/master/sample-import-rewrite.snippet

`build.py` 记录转换过程；`build-report.json` 记录数量、分组与过滤冲突。规则头部记录下载内容 SHA256。保留原作者归属与 GPL-3.0 许可，修正一处 KFC 路径中的非法正则转义，去重时对重复 URL 正则保留第一条。

## 2026-09-08 用户实测补充

新增两个精确域名：`83876gc.ezze0ct.com`、`0812gc.18tmnxt.com`。用户确认同时拦截后底部横幅消失，尚未分别验证每条必要性及翻页功能。没有扩大为 gc 关键词或整个主域名拦截。build.py 会在后续重建时保留这两条规则。

## GeQ1an 补充来源（2026-09-08）

在原有 2,428 条分流基础上新增 6,077 条，总计 8,505 条。原有重写和两个实测横幅域名保留。补充仅接受 HOST/HOST-SUFFIX 域名规则，统一映射为 reject，排除 IP、IPv6 和 User-Agent 条目；去重并检查 MitM 冲突与列出的业务保护域名。静态筛选不能保证所有新增域名当前仍只承载广告，未逐条实机测试。

原数据作者：GeQ1an/Rules 及其贡献者；并非本项目原创。来源：https://raw.githubusercontent.com/GeQ1an/Rules/master/QuantumultX/Filter/AdBlock.list ，用户指定的 CDN：https://fastly.jsdelivr.net/gh/GeQ1an/Rules@master/QuantumultX/Filter/AdBlock.list 。截至接入时该文件 master 分支最后修改日期为 2024-11-16；不要把本项目生成时间理解为该源维护时间。

构建时将该源保存为 SOURCE_DIRECTORY/geq.list，与原来的三个上游文件一起提供，再运行 `python3 build.py SOURCE_DIRECTORY`。`supplement.py` 执行筛选，`build-report.json` 记录来源哈希及排除原因。源缺失或异常时停止发布，不清空补充规则。后续更新必须携带 supplement.py 并检查两份来源；保持实测自定义补丁。
