---
name: review-arm-cortex-m
description: |
  ARM Cortex-M 架构固件评审清单。当评审或修复 STM32/GD32/NRF52/RP2040 等 Cortex-M 内核
  单片机代码，或遇到芯片失联、外设无输出、串口乱码、随机 HardFault、DMA 静默失败等症状
  需要归因时，或提到 NVIC、Flash 等待周期、CCM/TCM、SysTick、FreeRTOS 边界优先级、
  Cortex-M 硬错误时使用。按本清单逐类核查后分级报告并重新生成修复代码。
---

# ARM Cortex-M 评审清单

配合 `embedded-workflow` 阶段 4 使用。逐类核查，分级 Critical / High / Medium，报告后重新生成完整修复代码。

## 1. 时钟与等待周期

- [ ] PLL 配置产生的实际频率 = 预期频率（输入/VCO/输出范围全部核对）
- [ ] Flash 等待周期（FLASH_ACR.LATENCY）与 HCLK 匹配；**先提频后加等待周期，先降等待周期后降频**
- [ ] 各总线（AHB/APB1/APB2）分频后不超过各自上限
- [ ] HSE/PLL 就绪标志带超时检测后才切换系统时钟
- [ ] 时钟切换后 SWS 标志确认切换完成
- [ ] 高端型号（F4/F7/H7）稳压器档位与超频 Over-drive 模式

## 2. 初始化顺序

- [ ] 外设时钟使能先于任何寄存器访问（否则总线错误）
- [ ] GPIO 配置（含 AF 复用号）先于外设使能
- [ ] NVIC 配置在外设就绪之后
- [ ] DMA 配置先于外设的 DMA 请求使能位
- [ ] 外设使能位是初始化序列最后一步

## 3. 中断

- [ ] 优先级分组只在启动时设置一次
- [ ] 所有优先级在 `__NVIC_PRIO_BITS` 有效范围内
- [ ] **FreeRTOS 边界**：调用 FreeRTOS API 的 ISR 优先级 ≥ `configLIBRARY_MAX_SYSCALL_INTERRUPT_PRIORITY`（数值上更低优先）
- [ ] 每个使能的中断都有处理函数；共享向量处理所有可能的标志源
- [ ] 使能中断前先清 pending 标志（否则一使能就触发）
- [ ] ISR 内无阻塞操作（延时、printf、互斥量）

## 4. DMA

- [ ] 流/通道与外设的映射对照参考手册 DMA 请求表核对（不猜）
- [ ] 两个外设不共用同一 DMA 流
- [ ] 缓冲区在可 DMA 的 RAM：**不在 CCM（F3/F4）、不在 DTCM（F7）**——放错位置传输静默失败
- [ ] 缓冲区对齐（字传输 4 字节对齐）
- [ ] 方向、外设/内存数据宽度、增量模式三者都核对
- [ ] 新传输开始前清除传输完成标志
- [ ] FIFO 阈值与突发长度兼容；循环模式检查缓冲区覆盖
- [ ] 带 D-Cache 的型号（F7/H7）对 DMA 缓冲区做 Cache 维护

## 5. 内存与 volatile

- [ ] `volatile`：硬件寄存器指针、ISR 与主循环共享变量，全部加上
- [ ] SCB/NVIC 寄存器写入后加 `__DSB()` / `__ISB()` 屏障
- [ ] 链接脚本栈空间 ≥ 最坏调用深度 + ISR 嵌套；ISR 内不开大局部数组
- [ ] 读改写用 `|=` / `&= ~`，保留位不破坏；状态标志清除方式按外设规定（读清 / 写 1 清）

## 6. FreeRTOS（如使用）

- [ ] HAL 时基不用 SysTick（换 TIM6/7 等空闲定时器）
- [ ] ISR 内只用 `*FromISR()` 变体，唤醒更高优先级任务后调 `portYIELD_FROM_ISR()`
- [ ] `configPRIO_BITS` 与芯片 `__NVIC_PRIO_BITS` 一致
- [ ] 任务栈用 `uxTaskGetStackHighWaterMark` 验证过；开发期开 `configCHECK_FOR_STACK_OVERFLOW`

## 7. GPIO 特别项

- [ ] 复用号（AF0-AF15）对照数据手册复用表逐脚核对
- [ ] **SWD 引脚（通常 PA13/PA14）未被误配为其它复用**——配错即永久失联
- [ ] I2C 引脚开漏 + 上拉；未用引脚配模拟输入省电

## 8. 安全

- [ ] 读保护（RDP）级别与部署阶段匹配；量产关调试口
- [ ] 看门狗已启用且喂狗路径无死区
- [ ] Flash 中无硬编码密钥；敏感扇区考虑 PCROP

## 症状 → 原因 → 修法（Top 15，按出现频率排序）

| 症状 | 真正的原因 | 修法 |
|---|---|---|
| 首次访问外设寄存器即总线错误 | 漏开外设时钟 | RCC 使能位先于任何寄存器访问 |
| 外设完全无输出、引脚无波形 | AF 复用号错 | 对照数据手册复用表逐脚核对 |
| UART 收发乱码 | 波特率用错总线时钟（APB1/APB2 混淆）或 `HSE_VALUE` 定义不符 | 按实际外设时钟重算 BRR；核对 `-DHSE_VALUE` |
| 高频下随机 HardFault | Flash 等待周期不足 | 按频率表设 LATENCY；先提频后加等待 |
| DMA 传输静默失败/数据全 0 | 缓冲区在 CCM/DTCM（不可 DMA） | 移入主 SRAM 并 4 字节对齐 |
| 优化后 ISR 读到的总是旧值 | ISR 共享变量缺 volatile | 加 volatile，必要时加内存屏障 |
| SPI 完全不通 | CPOL/CPHA 与从机不符 | 按从机手册改模式 0~3 |
| 调用 FromISR 即硬错误 | ISR 优先级越过 FreeRTOS 边界 | 数值 ≥ `configLIBRARY_MAX_SYSCALL_INTERRUPT_PRIORITY` |
| 一个外设的 DMA 无故失效 | 两外设共用同一 DMA 流 | 重映射通道或改轮询 |
| SWD 突然连不上芯片 | PA13/PA14 被重配为其它复用 | BOOT0 进系统 bootloader 恢复；代码禁配 SWD 引脚 |
| 程序在 ISR 里卡死 | ISR 内调 HAL_Delay | 延时移出 ISR，用标志位+主循环 |
| 定时周期偏差大 | PSC/ARR off-by-one（都 +1 生效） | 公式重算，核对定时器时钟 ×2 规则 |
| 一使能中断就立刻进 ISR | 未清 pending 就使能 | 先清标志再 NVIC_EnableIRQ |
| 偶发数据错乱难复现 | ISR 与主循环读改写同一寄存器/变量 | 关中断临界区或原子操作 |
| 优先级行为与预期不符 | 优先级分组被多次设置 | 启动时设一次，之后不再动 |
