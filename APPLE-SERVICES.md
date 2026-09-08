# Apple 服务独立分流
适用于 Quantumult X，独立于去广告订阅。仅调整指定服务器的网络出口，不修改地区判定、账户、DNS 或 HTTPS 响应，也不需要安装或重新生成证书。

## 订阅
- Apple Intelligence / Siri / 扩展：https://raw.githubusercontent.com/H07MaN/quantumultx-rules/main/apple-intelligence.list
- iCloud 私密转送：https://raw.githubusercontent.com/H07MaN/quantumultx-rules/main/apple-private-relay.list

## 手机设置
1. 在「资源 → 分流」分别添加上述链接，不要添加到重写。
2. 分别打开「策略偏好」，选择你已有且能正常访问目标服务的代理节点或策略组。文件使用内置 direct 作为兼容默认值；不设置策略偏好就会直连。
3. 打开「插入资源」，让它们在普通 Apple/iCloud 分流及 IP/ASN 直连规则之前匹配。资源解析器关闭。若本地有同域名规则，也需检查其优先级。
4. 使用规则分流模式。节点须能处理相关 TCP/UDP 流量；Apple 列出部分服务使用 UDP 443。
5. 重连 Quantumult X，再分别测试 Siri 中的 ChatGPT 和私密转送。网络活动中查看实际命中的域名、规则和出口。

不需要新增自定义策略组，可直接选择已有节点。也可自行建立手动选择组再用策略偏好绑定。

## 范围与限制
Intelligence 文件覆盖 Apple 官方列出的扩展中继、Siri/Search、Private Cloud Compute，不能视为完整 ChatGPT 网页/App 登录域名清单。私密转送文件只覆盖官方列出的三个入口；不接管全部 iCloud 同步流量。
两份文件不含 reject、重写或 MITM hostname，彼此域名不重复。发布时检查与本仓库去广告分流和 MITM 主机范围的冲突。
Apple 服务应避免 HTTPS 解密；如果用户另行添加了通配 MITM 主机，需要自行排除这些服务。
你目前在中国大陆、美区账户、日版 iPhone。账户区域与购买地区并不能保证所有服务在当前位置可用。关闭 Quantumult X 仍提示国家或地区不支持，说明不能把原因仅归于本仓库规则。此订阅用于连通性排查，不承诺地区解锁。
如果命中指定代理后仍提示地区不支持，请保留提示原文和对应网络活动记录继续定位，不要反复重装证书。真实 iPhone 上的功能恢复尚未验证。

## 官方资料
- https://support.apple.com/en-us/101555
- https://developer.apple.com/icloud/prepare-your-network-for-icloud-private-relay/
- https://support.apple.com/en-hk/guide/iphone/iph00fd3c8c2/ios
- https://support.apple.com/en-hk/102602
