---
name: review-riscv
description: |
  RISC-V 架构固件评审清单。当评审或修复 CH32V003/V203/V307、GD32V、ESP32-C3/C6 等 RISC-V
  单片机代码，或遇到连不上芯片、烧录失败、中断异常、随机内存踩踏等症状需要归因时，
  或提到 riscv-none-elf-gcc、-march/-mabi、CLIC/CLINT/PLIC、WCH-Link、minichlink、
  esptool、ch32v003fun、ESP-IDF、RV32EC 时使用。按本清单逐类核查后分级报告，修复默认输出最小可应用 diff。
---

# RISC-V 评审清单

配合 `embedded-workflow` 阶段 4 使用。覆盖 WCH CH32V / GD32V / ESP32-C 系三类主流生态。逐类核查，分级 Critical / High / Medium，报告后默认输出**最小可应用 diff**；仅单文件示例或用户明确要求完整替换时才输出完整文件。

## 1. 工具链与 ABI（RISC-V 特有，最高频翻车点）

- [ ] `-march`/`-mabi` 从该芯片的**官方工程或构建配置**取值，逐型号核验 ISA 扩展，不凭系列名套用：CH32V003 是 RV32EC（压缩指令、仅 16 个寄存器，ABI 用 ilp32e）；其余型号逐个确认——用错 -march 生成的代码不能跑或不能中断
- [ ] ilp32e 在 RISC-V ABI 规范中仍为草案，实际可用性取决于工具链——以厂商 SDK/官方示例的编译配置为准，并检查编译、链接与运行库一致
- [ ] 不混用 xPack GCC 与 MounRiver 自带 GCC 的运行时库/启动文件（两套 libc 与 newlib 配置不兼容）
- [ ] ESP32-C 系用 ESP-IDF 工具链（riscv32-esp-elf-gcc），与通用 riscv-none-elf-gcc 不互换
- [ ] 链接脚本 ROM/RAM 起始与长度对应该型号；栈顶符号在 RAM 顶端且对齐（RV32E 要求 2/4 字节对齐）

## 2. 中断系统（RISC-V 无统一标准，按核确认）

- [ ] 中断控制器形态确认：WCH 自研 PFIC、CLIC、CLINT、PLIC——不同核的寄存器与编程模型完全不同，不可混写
- [ ] WCH 平台：中断函数的属性名与写法**从项目启动文件和厂商示例确认**（如 `interrupt("WCH-interrupt")` 或 ch32v003fun 的宏，随工具链与芯片系列而异）；硬件压栈（HPE）是否启用要明确；中断 ABI、启动文件向量表与芯片中断控制器三者必须匹配
- [ ] 向量模式（vectored）vs 直接模式（direct）与启动文件的跳转表一致
- [ ] 使能链逐层确认，**按平台机制而非统一层名**：WCH/GD32 系为 mstatus.MIE + PFIC + 外设使能；ESP32-C 系为 IDF 中断分配器 + interrupt matrix + 外设使能
- [ ] 中断里清标志 + 最小化处理，与 ARM 相同的纪律适用
- [ ] SysTick/系统节拍源与 RTOS port 匹配（ch32v003fun、FreeRTOS WCH port 各有约定）

## 3. 时钟与 Flash

- [ ] PLL 倍频源与目标频率核对；CH32V003 上限 48MHz、V203 上限 144MHz 等逐型号确认
- [ ] Flash 等待周期/预取使能与主频匹配（该型号参考手册核对）
- [ ] 外设时钟使能先于寄存器访问（WCH 同样有 RCC 使能位体系）

## 4. 内存（小 RAM 型号重点）

- [ ] CH32V003 仅 **2KB RAM**：.data+.bss+栈总和必须逐项核对，链接脚本里栈顶定义与 .bss 末尾不重叠
- [ ] DMA 缓冲区对齐与所在 RAM 区域可 DMA 性确认（逐型号）
- [ ] `volatile` 纪律与 ARM 相同：寄存器、ISR 共享变量
- [ ] 大缓冲区考虑放 XRAM（有该特性的型号如 V307）

## 5. DMA（WCH/GD32）

- [ ] DMA 通道映射对照参考手册请求表核对（CH32V 的 DMA1/DMA2 通道表）
- [ ] 外设/内存数据宽度与增量模式核对；新传输前清完成标志
- [ ] 无流冲突（两外设共用通道）

## 6. 烧录与调试

- [ ] WCH-Link(E) 与目标匹配：**CH32V003 使用 1-wire SDI 调试接口，普通 WCH-Link 不支持该接口，需 WCH-LinkE**（接口兼容性问题，非 ISA 问题）——配错连不上；以 WCH 官方支持表核对适配器型号与固件版本
- [ ] OpenOCD 用 WCH fork（openocd-wch）或 minichlink，通用 OpenOCD 不含 WCH 目标配置
- [ ] OpenOCD 配置文件对应该型号（wch-riscv.cfg 参数）；ESP32-C3 用 esptool/idf.py
- [ ] SDIO/JTAGMEM 等新调试接口（V307+）与传统 SWIO 差异确认
- [ ] Boot 引脚/BOOT 模式与下载方式匹配

## 7. ESP-IDF 生态（如使用 ESP32-C 系）

- [ ] FreeRTOS 为 IDF 原生集成，任务/队列 API 前缀 `xTask`/`xQueue` 与 IDF 特有 API 不混用
- [ ] flash 分区表与 app 偏移核对；`idf.py flash` 的端口与波特率
- [ ] 外设驱动用 IDF 组件（driver/uart.h 等）还是寄存器直访，风格统一

## 8. 安全

- [ ] 看门狗启用且喂狗路径完整
- [ ] 读保护/调试口策略（WCH 有对应配置寄存器）
- [ ] 无硬编码密钥

## 症状 → 常见原因 → 验证与修法（Top 10）

| 症状 | 常见原因 | 验证与修法 |
|---|---|---|
| 烧进去不跑/直接跑飞 | `-march/-mabi` 与内核不匹配（V003 应 RV32EC/ilp32e） | 验证：核对编译命令与官方工程配置；修法：按内核 ISA 重设并重编 |
| 链接错或运行时异常 | xPack 与 MounRiver 两套 GCC 的启动/库混用 | 验证：检查启动文件与运行库来源；修法：全链路统一一套工具链 |
| 一进中断就异常 | 中断函数属性与启动文件向量表/工具链不匹配 | 验证：比对启动文件与厂商示例；修法：按示例改写中断属性 |
| WCH-Link 连不上芯片 | CH32V003 的 1-wire SDI 接口需 LinkE | 验证：核对适配器型号与 WCH 官方支持表；修法：换 WCH-LinkE |
| OpenOCD 找不到 target cfg | 用了通用 OpenOCD | 验证：查 openocd 来源与脚本目录；修法：装 openocd-wch 或 minichlink |
| 运行中随机内存踩踏 | 2KB RAM：.bss 与栈重叠 | 验证：map 文件核对段边界；修法：链接脚本修正栈顶与 .bss |
| 中断永不触发 | 使能链漏一层（WCH/GD32：MIE+PFIC+外设；ESP32-C：IDF 中断分配+外设） | 验证：按平台机制逐层读使能；修法：补全使能链 |
| DMA 拿不到数据 | 通道映射凭记忆配错 | 验证：对照 RM DMA 请求表；修法：改正通道配置 |
| 串口乱码/无输出 | 波特率源配错、printf 未重定向（`_write`）、TX 引脚复用错 | 验证：核对实际外设时钟；修法：重算波特率、补重定向与复用 |
| RTOS 节拍忽快忽慢 | SysTick 源与 port 不匹配 | 验证：核对 port 文档要求；修法：按 port 配置节拍源 |
| 高频下随机崩溃 | Flash 等待周期不符 | 验证：主频对照手册等待周期表；修法：按表设置 |
