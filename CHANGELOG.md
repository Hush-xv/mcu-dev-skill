# Changelog

版本策略：本地迭代不升版；仅在发布节点统一升——功能级变化升次版本（0.x → 0.y），修复合并入下一次发布。

## 0.3.0 — 2026-11-15

- 五阶段工作流引入**任务三模式**（纯分析 / 代码修复 / 实际烧录），门禁与排障捷径不再互相冲突；门 1 未过仅禁止构建烧录，分析/评审/补丁可继续
- **模糊症状协议**：查板级档案 → 静默扫工作区推断型号 → 都失败则小步分诊（2~4 条高概率假设各附验证动作 + 一个区分度最高的问题）
- 三份架构评审清单（ARM Cortex-M / RISC-V / 8051）+ 症状 → 常见原因 → 验证与修法表
- 板级档案 skill：事实表（引脚带极性）/防错规则/排障表/烧录恢复梯，三级验证状态（硬件实测/手册推导/未验证）并记录测试日期与料号
- 表述与证据等级纪律：手册证实 / 多源互证 / 经验候选待验证；修复默认最小可应用 diff
- 第二轮审查修正：`/mcu-pipeline` 步骤与最小 diff 口径统一；PFIC 限定 WCH/GD32，ESP32-C 按 IDF 中断机制检查；评审与修复拆分为独立任务模式；volatile 语义澄清（可见性≠原子性）
- 第三、四轮审查修正：GD32V 中断控制器更正为 ECLIC（与 WCH PFIC、ESP32-C IDF 三分支）；门 2 分开判定编译工具与烧录工具；新增烧录执行边界（确认芯片/设备/擦除后才执行）；板级档案过期以关键事实为准（换 PCB/MCU/烧录器/时钟后重确认）；新增行为验收样例 docs/acceptance-examples.md
- 第五、六轮审查修正：Makefile 生成只由门 1+编译工具控制（门 3 仅阻止烧录）；优先使用工程已有构建系统，不再对 Keil/IAR/ESP-IDF 等强生 Makefile；门 1/2 按构建系统判定（设备包/SDK 管理的资源不要求在项目目录）；**Flash 等待周期顺序更正**（升频先增等待再切高频）；ARM 清单按平台标注（STM32/GD32 专属项与 RP2040 XIP 差异）；结果分级 构建成功≠烧录成功≠功能实测通过，档案只在功能实测后建档；验收样例增至 A1~A8
- 第七轮审查修正：GD32 Flash 等待周期寄存器按系列查（如 FMC_WS.WSCNT，非 FLASH_ACR.LATENCY）；门 1 应用入口按框架判定（`main()`/`app_main()`）；ARM 清单残余 STM32 风格项标注平台或泛化（AF0-AF15/APB/HSE_VALUE/定时器倍频/DMA 流）；ILP32E 栈对齐明确 4 字节；A8 增加型号前置条件，新增 A9 ESP-IDF 工程样例
- 第八轮审查修正：ARM 清单剩余 STM32 假设全部平台标注或泛化（DMA 流/CCM-DTCM/调试引脚/引脚复用）；阶段 1 补充 ESP-IDF 与 Zephyr 识别特征并要求组合判断（防单文件误判）；门 2 补 Zephyr（west）/PlatformIO（pio）构建入口；`/mcu-pipeline` 先判任务模式再执行阶段，编码仅限修复/烧录模式；新增 A10 ESP-IDF 自动识别样例
- 第九轮审查修正：Zephyr 识别改为候选特征组合（`prj.conf`/`find_package(Zephyr)`/应用目录结构；`west.yml` 在 workspace manifest 仓库，需向上查 `.west/config`）；工具链矩阵补 Zephyr（west build/flash，runner 按板级配置）与 PlatformIO（pio run/upload）完整门禁条目；FIFO 与未用引脚检查项泛化
- 第十轮全仓审查修正：STC8 EXTRAM 方向澄清（清零启用，按型号手册设定）；sbit 位地址通用规则限定可位寻址 SFR；SDCC 中断编号 n 与向量地址 0x0003+8n 区分；`/mcu-pipeline` 阶段 4 与最终呈现按模式限定（只评审不出 diff）；铁律 3 改为"未过的门只停止其保护的动作"；阶段 3 完整文件规则限定新建/示例（改已有项目用最小 diff）；阶段 1 查询顺序明确（档案→扫描→补问）；模糊症状提问口径统一（一条消息 ≤3 字段）；D-Cache 项泛化
- 第十一轮审查修正：`/mcu-pipeline` 烧录任务改为使用工程已有构建系统（不再强制生成 Makefile）；ESP-IDF 识别改为组合候选（`idf_component.yml` 可选）；矩阵拆分构建/烧录/检测三列（west build vs west flash、pio run vs upload），探针不可预检时要求设备枚举；MCS-51 端口模式按厂商分支（STC PxM0/PxM1 vs N76 PxM1/PxM2）；位寻址范围补 0xF8；新增 A11（Zephyr 无应用内 west.yml）、A12（PIO 探针上传无串口）样例；症状表 Top 数与实际行数对齐（16/11/11）
- 第十二轮审查修正：STC 端口复位默认按子系列拆分（STC8G/8H 除 P3.0/P3.1 外默认高阻，非准双向）；MounRiver 识别补 `.wvproj` 并写明构建入口；CMSIS-DAP 不再绑定固定 VID；代码修复模式明确执行门 1/2、不执行门 3；pdata 术语更正（分页 xdata）与 data/idata 上限说明；定时器初值公式限定模式/位宽；xPack/MounRiver 混用改为条件核验；"心测编译"改静态自检+实际构建；板级症状档案逐条标注证据状态（已实测/候选）
- 第十三轮审查修正：STC15 复位默认细分子系列（W1 准双向 / 15H 高阻），无法确认按型号手册；A10/A11 请求改为"定位原因并修复"以对齐代码修复模式；定时器计算改为两步公式（Ftimer = Fosc/分频 → N = round(T×Ftimer) → 16 位重装 65536−N）
- 第十四轮审查修正：A11 预期改为纯代码修复模式（west build 验证、不执行 west flash、不要求板子在线）；新增 A13 实际烧录样例（west flash 前确认芯片/探针/擦除）
- 第十五轮审查修正：CMSIS-DAP 的 ARM VID 更正为 0x0d28（DAPLink 常见 0x0d28:0x0204），删除错误的 0x2e3a 归属；A13 移至 A12 之后，样例编号恢复连续
- 技术断言校准：SWD 失联改 Connect-Under-Reset 路径；WCH-LinkE 依据改为 1-wire SDI 接口兼容性；时钟未使能的后果标注依型号而异
- 已知未验证项：GitHub 市场源在部分网络环境刷新超时（推荐 clone 本地添加）；插件 agents/ 形态未启用
