---
name: review-riscv
description: |
  RISC-V 架构固件评审清单。当评审或修复 CH32V003/V203/V307、GD32V、ESP32-C3/C6 等 RISC-V
  单片机代码，或遇到连不上芯片、烧录失败、中断异常、随机内存踩踏等症状需要归因时，
  或提到 riscv-none-elf-gcc、-march/-mabi、CLIC/CLINT/PLIC、WCH-Link、minichlink、
  esptool、ch32v003fun、ESP-IDF、RV32EC 时使用。按本清单逐类核查后分级报告并重新生成修复代码。
---

# RISC-V 评审清单

配合 `embedded-workflow` 阶段 4 使用。覆盖 WCH CH32V / GD32V / ESP32-C 系三类主流生态。逐类核查，分级 Critical / High / Medium，报告后重新生成完整修复代码。

## 1. 工具链与 ABI（RISC-V 特有，最高频翻车点）

- [ ] `-march` 与内核实际 ISA 匹配：CH32V003 是 **RV32EC**（压缩指令、仅 16 个寄存器），CH32V203 及以上多为 RV32IMAC——用错 -march 生成的代码不能跑或不能中断
- [ ] `-mabi` 匹配（ilp32 / ilp32e：RV32E 必须用 **ilp32e**）
- [ ] 不混用 xPack GCC 与 MounRiver 自带 GCC 的运行时库/启动文件（两套 libc 与 newlib 配置不兼容）
- [ ] ESP32-C 系用 ESP-IDF 工具链（riscv32-esp-elf-gcc），与通用 riscv-none-elf-gcc 不互换
- [ ] 链接脚本 ROM/RAM 起始与长度对应该型号；栈顶符号在 RAM 顶端且对齐（RV32E 要求 2/4 字节对齐）

## 2. 中断系统（RISC-V 无统一标准，按核确认）

- [ ] 中断控制器形态确认：WCH 自研 PFIC、CLIC、CLINT、PLIC——不同核的寄存器与编程模型完全不同，不可混写
- [ ] WCH 平台：中断函数用厂商属性（`__attribute__((interrupt("WCH-interrupt")))` 或 ch32v003fun 的宏），硬件压栈（HPE）是否启用要明确；标准 `interrupt` 属性在 WCH 核上行为不同
- [ ] 向量模式（vectored）vs 直接模式（direct）与启动文件的跳转表一致
- [ ] 全局中断使能（mstatus.MIE）+ 外设中断使能 + PFIC 使能三层都要开
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

- [ ] WCH-Link(E) 与目标匹配：**CH32V003 必须 WCH-LinkE**（普通 WCH-Link 不支持 RV32E）——配错连不上
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

## 症状 → 原因 → 修法（Top 10）

| 症状 | 真正的原因 | 修法 |
|---|---|---|
| 烧进去不跑/直接跑飞 | `-march/-mabi` 与内核不匹配（V003 应 RV32EC/ilp32e） | 按内核 ISA 重设并重编 |
| 链接错或运行时异常 | xPack 与 MounRiver 两套 GCC 的启动/库混用 | 全链路统一一套工具链 |
| 一进中断就异常 | WCH 核用了标准 interrupt 属性 | 改 `WCH-interrupt` 属性或厂商宏 |
| WCH-Link 连不上芯片 | 普通版 Link 烧 RV32E 芯片（V003） | 换 WCH-LinkE |
| OpenOCD 找不到 target cfg | 用了通用 OpenOCD | 装 openocd-wch 或 minichlink |
| 运行中随机内存踩踏 | 2KB RAM：.bss 与栈重叠 | 链接脚本核对栈顶与 .bss 边界 |
| 中断永不触发 | 三层使能（MIE/PFIC/外设）漏一层 | 逐层检查使能位 |
| DMA 拿不到数据 | 通道映射凭记忆配错 | 对照 RM DMA 请求表 |
| RTOS 节拍忽快忽慢 | SysTick 源与 port 不匹配 | 按 port 要求配置节拍源 |
| 高频下随机崩溃 | Flash 等待周期不符 | 按手册等待周期表设置 |
