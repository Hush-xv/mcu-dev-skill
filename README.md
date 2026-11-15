# mcu-dev-skill — 通用 MCU 固件开发技能（ZCode 插件）

文档驱动的单片机固件开发工作流：**环境分析 → 手册精读 → 编码 → 硬件评审 → 构建门禁** 五阶段流水线，附 ARM Cortex-M / RISC-V / 8051 三套架构评审清单与板级档案沉淀。

English summary: a doc-driven five-phase firmware workflow skill for ZCode (environment analysis → datasheet research → coding → hardware review → build gates), with per-architecture review checklists for ARM Cortex-M, RISC-V and 8051, plus a board-profile skill for capturing per-board knowledge.

## 包含的技能

| 技能 | 职责 |
|---|---|
| `embedded-workflow` | 主工作流：五阶段流水线、`docs/` 手册目录约定、工具链矩阵、三道构建门禁 |
| `review-arm-cortex-m` | ARM 评审清单 + 症状→原因→修法表（STM32/GD32/nRF/RP2040） |
| `review-riscv` | RISC-V 评审清单 + 症状表（CH32V003/V203/V307、GD32V、ESP32-C 系） |
| `review-mcs51` | 8051 评审清单 + 症状表（STC8H/STC15/STC89/N76E003 等） |
| `board-profile` | 板级档案：为自己的板子沉淀事实表、防错规则、排障表、烧录恢复梯 |

命令：`/mcu-pipeline <目标描述>` 一键跑全流程。

## 安装（ZCode）

1. **插件市场 → 添加 → 添加插件市场**，粘贴本仓库目录（clone 后的本地路径）
2. **个人 → MCU Dev Skill（通用MCU开发技能）→ 安装**
3. 新任务中使用 `/mcu-pipeline`，或直接描述固件任务（技能按症状与关键词自动触发）

> 注：部分网络环境下 GitHub 市场源刷新会超时，推荐 clone 到本地后以**本地目录源**添加。

## 覆盖范围与兼容性

- **架构覆盖**：ARM Cortex-M（STM32/GD32/nRF/RP2040 等）、部分 RISC-V（WCH CH32V、ESP32-C 系）、8051（STC/N76/AT89）。AVR/MSP430/PIC/STM8 等平台可使用通用流程，但无专项评审清单。
- **客户端兼容**：ZCode 桌面端（本地目录市场源与 GitHub 市场源）。插件全部为 Markdown/JSON，无运行时依赖，不需要 Node/Python。
- **安装验证状态**：**尚未在任何环境完成实际安装验证**；本地目录源与 GitHub 源的完整安装流程均待实测（欢迎反馈）。

## 文档驱动用法

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

## 设计来源

架构与思想受 [embedded-claude-plugin](https://github.com/bahaabdelwahed/embedded-claude-plugin)（STM32 专属原作）启发并通用化；写作与档案方法论吸收 [mcu-skills](https://github.com/alexex1993/mcu-skills) 与 [zephyr-agent-skills](https://github.com/beriberikix/zephyr-agent-skills) 的实践经验。全部内容为原创编写，未复制第三方代码。

## License

[MIT](LICENSE)
