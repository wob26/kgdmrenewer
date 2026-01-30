# DigitalPlat 域名自动续期脚本 - 配置说明

## 📋 修复说明 (2025年1月)

### 主要修复内容:
1. ✅ 修复了Chrome驱动崩溃问题 (改用stable版本代替114)
2. ✅ 适配了新版DigitalPlat界面流程
3. ✅ 增加了更多的元素定位方式,提高稳定性
4. ✅ 优化了错误处理和日志输出
5. ✅ 添加了续期窗口期检测 (180天)

### 新版续期流程:
```
登录 → 访问域名管理页面 → 点击"Renew"标签 → 点击"Request free renewal" → 确认 → 完成
```

## 🚀 快速配置指南

### 第1步: 在GitHub仓库设置Secrets

进入你的GitHub仓库 → Settings → Secrets and variables → Actions → New repository secret

为每个账户添加以下3个Secrets:

#### 账户1 (必需):
- `ACCOUNT_1_USERNAME`: 你的DigitalPlat用户名或邮箱
- `ACCOUNT_1_PASSWORD`: 你的DigitalPlat密码
- `ACCOUNT_1_DOMAINS`: 你要续期的域名列表 (用逗号分隔)

**示例:**
- ACCOUNT_1_USERNAME: `your.email@example.com`
- ACCOUNT_1_PASSWORD: `your_password_here`
- ACCOUNT_1_DOMAINS: `wiobr.dpdns.org,zhiqiao.dpdns.org`

#### 账户2 (可选):
- `ACCOUNT_2_USERNAME`: 第二个账户的用户名
- `ACCOUNT_2_PASSWORD`: 第二个账户的密码
- `ACCOUNT_2_DOMAINS`: 第二个账户的域名列表

#### 更多账户:
如需添加更多账户,继续添加 ACCOUNT_3_*, ACCOUNT_4_* 等,脚本会自动检测

### 第2步: 替换项目文件

1. 用新的 `renew.py` 替换你项目根目录的旧文件
2. 用新的 `renew-domain.yml` 替换 `.github/workflows/` 目录下的旧文件

### 第3步: 提交并推送

```bash
git add renew.py .github/workflows/renew-domain.yml
git commit -m "修复域名续期脚本,适配新版DigitalPlat界面"
git push
```

### 第4步: 测试运行

1. 进入GitHub仓库 → Actions
2. 选择 "DPDNS Domain Auto-Renew" workflow
3. 点击 "Run workflow" → "Run workflow" 按钮
4. 等待运行完成,查看日志

## ⏰ 自动运行时间

脚本会在以下时间自动运行:
- 每月1号 UTC时间 3:00 (北京时间 11:00)
- 每月15号 UTC时间 3:00 (北京时间 11:00)

**注意:** 免费续期需要域名到期时间少于180天,所以建议:
- 在域名到期前6个月(约180天)开始尝试续期
- 每半个月检查一次,确保在续期窗口内能成功续期

## 🔧 常见问题排查

### Q1: 脚本运行失败,显示 "未找到任何账户配置"
**解决:** 检查Secrets名称是否正确,必须是 `ACCOUNT_1_USERNAME` 而不是其他名称

### Q2: 脚本显示 "域名不在免费续期窗口期内"
**解决:** 这是正常情况,域名需要到期时间少于180天才能免费续期,请等待

### Q3: Chrome驱动崩溃
**解决:** 新版脚本已修复此问题,使用stable版Chrome

### Q4: 登录失败
**解决:** 
- 检查用户名和密码是否正确
- 确保账户没有被锁定
- 查看Actions日志中的详细错误信息

### Q5: 找不到Renew按钮
**解决:** 
- 新版脚本已增加多种定位方式
- 如果仍然失败,可能是页面结构再次变化,需要更新脚本

## 📝 域名列表格式

多个域名用逗号分隔,例如:
```
domain1.dpdns.org,domain2.dpdns.org,domain3.dpdns.org
```

**注意:**
- 不要有空格 (脚本会自动处理,但最好不要)
- 域名必须包含完整的后缀 (.dpdns.org等)
- 域名必须在对应账户下

## 🔍 查看运行日志

1. 进入GitHub仓库 → Actions
2. 点击最近的运行记录
3. 点击 "renew" job
4. 展开 "Run renewal script" 查看详细日志

日志会显示:
- 每个账户的登录状态
- 每个域名的续期状态
- 任何错误或警告信息

## ⚠️ 重要提示

1. **Secrets安全性**: 
   - 永远不要在代码中硬编码密码
   - 不要将Secrets提交到Git
   - 定期更新密码

2. **续期时机**:
   - 域名到期前180天内才能使用免费续期
   - 建议在到期前3-6个月开始尝试
   - 脚本会每月自动运行2次

3. **多账户管理**:
   - 每个账户独立配置
   - 可以为不同账户配置不同的域名
   - 支持无限多个账户

4. **故障恢复**:
   - 如果某个域名续期失败,脚本会继续处理其他域名
   - 可以查看上传的错误截图 (如果有)
   - 可以手动重新运行workflow

## 📊 执行流程图

```
开始
 ↓
读取账户1配置
 ↓
启动浏览器 → 登录账户1
 ↓
获取域名列表
 ↓
循环处理每个域名:
  - 访问域名管理页面
  - 点击Renew标签
  - 点击Request free renewal
  - 确认并检查结果
 ↓
关闭浏览器
 ↓
读取账户2配置 (如果存在)
 ↓
重复上述流程...
 ↓
所有账户处理完毕
 ↓
结束
```

## 🆘 获取帮助

如果遇到问题:
1. 先查看本说明文档的常见问题部分
2. 查看GitHub Actions的运行日志
3. 检查Secrets配置是否正确
4. 确保域名在续期窗口期内
5. 在GitHub仓库提交Issue描述问题

## 📅 更新日志

### v2.0 (2025-01-30)
- 🔧 修复Chrome驱动崩溃问题
- 🎯 适配新版DigitalPlat界面
- ✨ 增加更稳定的元素定位
- 📝 改进日志输出
- ⏰ 优化自动运行时间

### v1.0
- 🎉 初始版本
- ⚡ 基本续期功能
