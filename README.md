<div align="center">

# ⚙️ mcu-dev-skill

**通用 MCU 固件开发技能包 —— 让 AI 像资深固件工程师一样工作**

*文档驱动 · 五阶段流水线 · 硬件级评审 · 构建门禁*

</div>

<p align="center">
  <a href="https://github.com/Hush-xv/mcu-dev-skill/releases"><img alt="Release" src="https://img.shields.io/github/v/tag/Hush-xv/mcu-dev-skill?style=flat-square&label=release" /></a>
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/github/license/Hush-xv/mcu-dev-skill?style=flat-square" /></a>
  <a href="#包含的技能"><img alt="Skills" src="https://img.shields.io/badge/skills-6-blue?style=flat-square" /></a>
  <a href="#安装"><img alt="Platform" src="https://img.shields.io/badge/ZCode-%E6%A1%8C%E9%9D%A2%E7%AB%AF-blueviolet?style=flat-square" /></a>
</p>
<p align="center">
  <a href="#覆盖范围与兼容性"><img alt="ARM Cortex-M" src="https://img.shields.io/badge/ARM_Cortex_M-supported-blue.svg" /></a>
  <a href="#覆盖范围与兼容性"><img alt="RISC-V" src="https://img.shields.io/badge/RISC__V-supported-blue.svg" /></a>
  <a href="#覆盖范围与兼容性"><img alt="8051" src="https://img.shields.io/badge/8051-supported-blue.svg" /></a>
  <a href="#覆盖范围与兼容性"><img alt="ESP-IDF" src="https://img.shields.io/badge/ESP__IDF-%E8%AF%86%E5%88%AB-blueviolet.svg" /></a>
  <a href="#覆盖范围与兼容性"><img alt="Zephyr" src="https://img.shields.io/badge/Zephyr-%E8%AF%86%E5%88%AB-blueviolet.svg" /></a>
  <a href="#覆盖范围与兼容性"><img alt="PlatformIO" src="https://img.shields.io/badge/PlatformIO-%E8%AF%86%E5%88%AB-blueviolet.svg" /></a>
</p>

---

## 📖 这是什么？

**mcu-dev-skill** 是一套 ZCode 插件，把资深固件工程师的工作纪律沉淀为 AI 可执行的工作流：**环境分析 → 手册精读 → 编码 → 硬件评审 → 构建门禁**，五种任务模式（纯分析 / 只评审 / 代码修复 / 实际烧录）按需启用阶段，门禁只拦该拦的事。

它的核心思想是**文档驱动**：寄存器值、引脚复用、电气参数一律以你提供的芯片手册为准，每条摘录带页码可追溯；手册里找不到的明说找不到——绝不猜。成功 bring-up 的板子用 `board-profile` 沉淀为板级档案，越用越准。

## 🤔 为什么需要它？

通用编码代理做固件开发，常见三个坑：

- **寄存器幻觉** —— 冷门型号的寄存器细节不可靠，AI 会把"大概率正确"的值写得斩钉截铁。
  → 解法：手册为源 + 页码可追溯 + 证据等级（手册证实 / 多源互证 / 经验候选），"经验候选"不作为确定结论。
- **手册盲区** —— 训练语料覆盖不到的型号（STC 冷门款、WCH 新款）才是真盲区。
  → 解法：`docs/` 手册目录约定，代理现场精读 PDF，手册越全代码越准。
- **流程散漫** —— 拿到"帮我修个串口"就直接开写，跳过环境分析、没有构建验证。
  → 解法：任务模式路由 + 三道构建门禁；烧录前强制确认芯片、设备与擦除。

## ✨ 包含的技能

| 技能 | 职责 |
|---|---|
| `embedded-workflow` | 主工作流：任务模式路由、五阶段流水线、`docs/` 手册目录约定、工具链矩阵、三道构建门禁 |
| `review-embedded-c` | 架构无关的嵌入式 C 质量检查：边界、整数、生命周期、错误处理、并发与工具证据 |
| `review-arm-cortex-m` | ARM 评审清单 + 症状→常见原因→验证与修法表（STM32/GD32/nRF/RP2040） |
| `review-riscv` | RISC-V 评审清单 + 症状表（CH32V003/V203/V307、GD32V、ESP32-C 系） |
| `review-mcs51` | 8051 评审清单 + 症状表（STC8H/STC15/STC89/N76E003 等，复位默认按子系列区分） |
| `board-profile` | 板级档案：为自己的板子沉淀事实表、防错规则、排障表、烧录恢复梯 |

命令：`/mcu-pipeline <目标描述>` 一键跑全流程（自动按任务模式裁剪阶段）。

## 🚀 安装（ZCode）

1. **插件市场 → 添加 → 添加插件市场**，粘贴本仓库目录（clone 后的本地路径），或直接填 `Hush-xv/mcu-dev-skill`（GitHub 源）
2. **个人 → MCU Dev Skill（通用MCU开发技能）→ 安装**
3. 新任务中使用 `/mcu-pipeline`，或直接描述固件任务（技能按症状与关键词自动触发）

> 注：部分网络环境下 GitHub 市场源刷新会超时，推荐 clone 到本地后以**本地目录源**添加。

## 覆盖范围与兼容性

- **架构覆盖**：ARM Cortex-M（STM32/GD32/nRF/RP2040 等）、部分 RISC-V（WCH CH32V、ESP32-C 系）、8051（STC/N76/AT89）。AVR/MSP430/PIC/STM8 等平台可使用通用流程 + `review-embedded-c`，但无专项评审清单。
- **客户端兼容**：ZCode 桌面端（本地目录市场源与 GitHub 市场源）。插件全部为 Markdown/JSON，无运行时依赖，插件运行本身不需要 Node/Python。
- **安装验证状态**：**尚未在任何环境完成实际安装验证**；本地目录源与 GitHub 源的完整安装流程均待实测（欢迎反馈）。行为验收样例见 [docs/acceptance-examples.md](docs/acceptance-examples.md)。

## 🧭 文档驱动用法

技能假定你把芯片手册 PDF 放在项目 `docs/` 下：

```text
docs/
├── reference-manual/     # 参考手册（寄存器位域，最常用）
├── datasheet/            # 数据手册（引脚复用、电气参数）
├── user-manual/          # 用户手册（板级布局、晶振）
├── programming-manual/   # 编程手册（内核指令、调试口）
├── application-notes/    # 应用笔记
├── technical-notes/
└── security-docs/
```

手册越全，生成的代码越准；所有寄存器值以手册为准并带页码引用。成功 bring-up 后用 `board-profile` 沉淀板级档案，越用越准。

## ✅ 行为验收

19 个固定验收样例（A1~A19）覆盖全部任务模式与识别边界——模糊症状、只评审、缺手册、缺烧录器、Keil/ESP-IDF/Zephyr/PIO 识别、烧录确认边界、C 质量评审路由。详见 [docs/acceptance-examples.md](docs/acceptance-examples.md)。

## 🛠️ 仓库维护校验

修改 skill、插件清单或验收样例后，可用 Python 3.10+ 标准库检查 frontmatter、内部引用、插件路径、README 技能目录和验收编号：

```sh
python scripts/validate_repo.py
```

该脚本只校验仓库结构与文档一致性，不替代插件安装和 A1–A19 行为验收。

## 🤝 致谢

架构与思想受 [embedded-claude-plugin](https://github.com/bahaabdelwahed/embedded-claude-plugin)（STM32 专属原作）启发并通用化；写作与档案方法论吸收 [mcu-skills](https://github.com/alexex1993/mcu-skills) 与 [zephyr-agent-skills](https://github.com/beriberikix/zephyr-agent-skills) 的实践经验。全部内容为原创编写，未复制第三方代码。

## 📄 许可证

[MIT](LICENSE)
