# DPDNS Domain Auto-Renew with GitHub Actions 🚀

![Workflow Status](https://github.com/wob26/kgdmrenewer/actions/workflows/renew-domain.yml/badge.svg)

一份 **“一劳永逸”** 的解决方案，用于自动续期您在 [digitalplat.org](https://dash.domain.digitalplat.org/) 注册的免费 `.dpdns.org` 域名。告别手动续期的烦恼，让 GitHub Actions 成为您 7x24 小时的域名续期管家！

## ✨ 特性

-   ✅ **完全自动化**：设定好计划后，无需任何人工干预。
-   ✅ **多账户 & 多域名支持**：轻松管理多个账户下的任意数量域名。
-   ✅ **安全可靠**：利用 GitHub 的加密 Secrets 安全存储您的账户凭据，代码中不留痕迹。
-   ✅ **无需服务器**：所有任务均在 GitHub 的云端服务器上运行，零硬件成本。
-   ✅ **高度可定制**：通过简单的 `cron` 表达式自由设定续期检查的频率和时间。
-   ✅ **详尽的日志与错误报告**：每次运行都有完整的日志记录，并在出错时自动截屏，方便快速定位问题。

## ⚙️ 工作原理

本项目利用 [Python](https://www.python.org/) 和强大的浏览器自动化工具 [Selenium](https://www.selenium.dev/)，编写了一个能够模拟人工操作的脚本。该脚本被配置在 [GitHub Actions](https://github.com/features/actions) 工作流中，通过 `schedule` 事件定时触发。

当预定时间到达时，GitHub Actions 会自动：
1.  创建一个虚拟的 Ubuntu Linux 环境。
2.  安装 Python、Chrome 浏览器和所有必要的依赖。
3.  从您配置的 GitHub Secrets 中安全地读取账户信息。
4.  执行 `renew.py` 脚本，该脚本会依次登录您的每个账户，并为您账户下的所有域名执行一整套续期操作。

## 🚀 部署指南

只需简单的四步，即可拥有属于您自己的域名续期机器人。

### 第 1 步：创建您的代码仓库

点击本页面右上角的 **Fork** 按钮，将此项目复制一份到您自己的 GitHub 账户下。

### 第 2 步：配置您的账户机密 (最关键的一步！)

进入您 Fork 后的仓库，点击 `Settings` > `Secrets and variables` > `Actions`。

然后，点击 `New repository secret` 按钮，添加以下**所有**机密信息。请注意命名规则，这是脚本识别账户的关键。

**为您的第一个账户添加：**
*   `ACCOUNT_1_USERNAME`:
    *   值: `1756467390@qq.com`
*   `ACCOUNT_1_PASSWORD`:
    *   值: 该账户在 `digitalplat.org` 的登录密码。
*   `ACCOUNT_1_DOMAINS`:
    *   值: 此账户下的所有域名，**用英文逗号隔开，不要有空格**。
    *   例如: `domain-a.dpdns.org,domain-b.dpdns.org`

**为您的第二个账户添加：**
*   `ACCOUNT_2_USERNAME`:
    *   值: `1510572948@qq.com`
*   `ACCOUNT_2_PASSWORD`:
    *   值: 该账户的密码。
*   `ACCOUNT_2_DOMAINS`:
    *   值: 此账户下的所有域名，同样用逗号隔开。
    *   例如: `domain-c.dpdns.org,another.dpdns.org,wioscat.dpdns.org`

> **提示**：如果您有更多账户，只需按照 `ACCOUNT_3_USERNAME`、`ACCOUNT_3_PASSWORD` 的格式继续添加即可，脚本会自动识别并处理。

### 第 3 步：自定义执行计划 (可选)

本项目默认在每年的**3月28日**和**4月28日**凌晨3点 (UTC时间) 自动运行。

如果您想修改这个时间，请编辑 `.github/workflows/renew-domain.yml` 文件，找到 `cron` 表达式：

```yaml
  schedule:
    # 格式: 分钟 小时 日 月份 星期
    - cron: '0 3 28 3,4 *'
```

您可以根据自己的需求修改它。例如，修改为每月1号运行：`- cron: '0 3 1 * *'`。

### 第 4 步：手动运行以验证配置

1.  进入仓库的 `Actions` 标签页。
2.  在左侧选择 `DPDNS Domain Auto-Renew` 工作流。
3.  在右侧，您会看到一个提示，点击 **`Run workflow`** 按钮。
4.  在弹出的窗口中再次点击绿色的 **`Run workflow`** 按钮。

等待几分钟，观察工作流的运行状态。如果最终显示一个**绿色的勾 ✅**，那么恭喜您，一切配置正确，您的自动化系统已成功部署！

## 📂 项目文件结构

```
.
├── .github/workflows/
│   └── renew-domain.yml    # GitHub Actions 工作流配置文件，定义了何时以及如何运行任务
└── renew.py                # 核心 Python 脚本，负责执行所有浏览器自动化操作
```

## 🛠️ 问题排查

如果 Actions 运行失败（显示红色的叉 ❌），请不要担心：
1.  点击进入失败的工作流。
2.  查看 **Run python renew.py** 步骤的日志，通常错误信息会在这里显示。
3.  在工作流的 **Summary** 页面，会有一个名为 `error-screenshots` 的构建产物 (Artifact)。下载并解压它，您可以看到脚本失败时卡在了哪个页面的截图，这对于定位问题非常有帮助。

---

***That's it! Enjoy your freedom from manual renewals. ✨***
