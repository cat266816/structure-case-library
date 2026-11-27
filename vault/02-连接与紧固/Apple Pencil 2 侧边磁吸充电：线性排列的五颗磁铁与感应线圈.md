---
标题: "Apple Pencil 2 侧边磁吸充电：线性排列的五颗磁铁与感应线圈"
一级分类: "02-连接与紧固"
二级分类: ["磁吸"]
应用产品: ["Apple Pencil（第 2 代）与配套 iPad Pro 侧边充电"]
材料: ["笔内五颗磁铁：稀土磁铁（Apple 回收指南标为 Rare Earth Elements / Magnets ×5）", "iPad 侧充电板：带铜充电线圈（iFixit）", "外壳：白色塑料；内部有金属杆与钢层（iFixit）。磁铁牌号与壳体树脂牌号来源未给出"]
工艺: ["五颗磁铁沿笔身侧面布置，回收时需撬下（Apple 回收指南步骤 7）", "充电为感应耦合，不是外露触点；iPad 侧有独立的 Pencil charging board 与铜线圈", "笔身几乎无开口，iFixit 用超声波刀切开外壳"]
标签: ["Apple Pencil", "侧吸", "线性磁铁", "感应充电", "对中"]
难度: "进阶"
来源平台: "厂商技术文章"
来源链接: "https://www.apple.com/recycling/recycler-guides/pdf/products/accessories/Apple_Pencil_2nd_Gen_Recycler_Guide_English.pdf"
补充来源: ["https://www.ifixit.com/Teardown/iPad+Pro+11-Inch+Teardown/115457"]
收录日期: 2026-11-27
评分: 4
核实状态: "已核实（已重新下载并打开 Apple Pencil (2nd generation) Recycler Guide：步骤 7 撬下五颗稀土磁铁；已通过 API 打开 iFixit iPad Pro 11 英寸拆解指南 115457：iPad 侧 Pencil 充电板与铜线圈、笔内无线充电线圈与 alignment magnets、侧面长条充电区。Apple 与 iFixit 为两个独立机构。已打开来源未给出配对协议或霍尔芯片细节，故不写入配对电路。未把第一代带 Lightning 的 Pencil 写成同一结构。）"
封面图: "附件/pencil-recycler-p-13.png"
tags: ["结构案例", "磁吸", "Apple Pencil", "侧吸", "感应充电", "线性磁铁"]
---

# Apple Pencil 2 侧边磁吸充电：线性排列的五颗磁铁与感应线圈

> [!summary] 一句话概述
> Apple Pencil（第 2 代）把充电从第一代的 Lightning 插头，改成沿笔身侧面一字排开的磁铁，把笔吸在 iPad 侧边的长条充电区上，再用感应线圈传能：笔内是 alignment magnets 加无线充电线圈，iPad 里是一块带铜充电线圈的 Pencil charging board。它是线性侧吸，不是手机那种圆环磁铁阵列，也不是笔记本 MagSafe 那样的外露弹簧顶针。

## 配图

![[附件/pencil-recycler-p-13.png]]
*图源：[Apple Pencil (2nd generation) Recycler Guide](https://www.apple.com/recycling/recycler-guides/pdf/products/accessories/Apple_Pencil_2nd_Gen_Recycler_Guide_English.pdf) 第 13 页，步骤 7；官方回收步骤要求「Pry off the five magnets」，右侧材料框标注 Magnets (×5) 与 Rare Earth Elements。图示中五颗磁铁沿笔身一侧排列，不是绕成圆环。*

![[附件/pencil-ipad-charging-coils.jpg]]
*图源：[iFixit，iPad Pro 11" Teardown，步骤 15](https://www.ifixit.com/Teardown/iPad+Pro+11-Inch+Teardown/115457)；从 iPad 里取出的 Pencil charging board，板中间仍连着铜充电线圈。iFixit 写它「with its copper charging coils attached」。这是平板侧的发射端，与笔内线圈相对，不是触点。*

![[附件/pencil-ipad-charging-board.jpg]]
*图源：同上步骤 15 的另一张照片；这块细长充电板沿 iPad 侧边布置，与外观上「一条深色长椭圆形充电区」（iFixit 步骤 3：a long dark oval to charge the new Pencil）相对应。拆屏蔽时有小电容崩飞，说明这是一块独立的侧边充电模块，而不是主板的一部分。*

> 图片版权归原作者所有，仅作个人学习收藏；出处见文末「来源与核实记录」。

## 结构原理

> 本节所有数字只写来源里给出的；来源没有就写「来源未给出」。回收指南给出笔内磁铁数量与材质类别；iFixit 给出 iPad 侧充电板、铜线圈，以及笔内「wireless charging coil」和「alignment magnets」。已打开来源没有写配对总线或霍尔开关，本文不补充。

### 堆叠方案

方向：**从 iPad 侧边外壳，到笔身贴边的一侧**（侧吸，不是绕笔圆周的磁环）

| 层级 | 零件 | 材料 | 厚度/尺寸 | 固定方式 | 依据 |
| --- | --- | --- | --- | --- | --- |
| L1（iPad 外壳） | 侧边壳体与长条充电区 | iPad Pro 11" 为铝合金壳体（iFixit）；外观可见一条深色长椭圆充电区 | iFixit 写充电区附近壳体更厚，未给毫米数 | 充电区做在侧壁上 | iFixit 步骤 3、4 |
| L2 | Pencil charging board | 来源未给出板材牌号 | 细长条，长度与侧边充电区对应，具体毫米数来源未给出 | 从机内取出的独立小板 | iFixit 步骤 15 |
| L3 | iPad 侧铜充电线圈 | 铜 | 来源未给出匝数 | 附在充电板上 | iFixit 步骤 15 |
| L4（气隙） | 塑料外壳与壳体之间的间隙 | 笔为白色塑料壳 | 来源未给出气隙 | 感应耦合穿过外壳，无外露触点 | iFixit：无线充电；外观无充电插口 |
| L5 | 笔内 alignment magnets | 稀土磁铁（回收指南） | 五颗，沿笔身一侧线性排列；单颗尺寸来源未给出 | 回收步骤为从笔上撬下 | Apple 回收指南步骤 7；iFixit 步骤 18、19 称 alignment magnets |
| L6 | 笔内无线充电线圈 | 来源未给出线型 | 来源未给出 | 与侧边磁铁一起构成「wireless charging getup」 | iFixit 步骤 18、19 |
| L7 | 笔身内核 | 金属杆、多层焊接钢结构、电池等 | 来源未给出 | iFixit 用超声波刀切开白色外壳后露出 | iFixit 步骤 18、19 |

剖面示意：

```mermaid
flowchart LR
  IPAD["iPad 侧边长条充电区"] --> BOARD["Pencil charging board"]
  BOARD --> TX["铜充电线圈（发射）"]
  TX -->|"感应耦合，穿过外壳"| RX["笔内无线充电线圈"]
  MAGP["笔侧 5 颗稀土磁铁，线性排列"] -->|"侧向吸合、对中"| IPAD
  RX --> BAT["笔内电池"]
```

和本批其他磁吸充电的差别：

- 本案例：磁铁沿**笔的长轴排成一条线**，吸在平板侧壁上；传能靠感应线圈。
- [[iPhone MagSafe 环形磁铁阵列：18 颗磁铁把线圈对中并对附件保持]]：磁铁绕成圆环，贴的是手机背面。
- [[Apple Watch 磁吸充电盘：中心单颗磁铁对位与电感耦合（对照手机环形阵列）]]：圆盘中心单颗磁铁。
- [[MagSafe 1-2 笔记本磁吸充电头：磁力保持触点对中，拉力过大时整头脱落]]：外露弹簧顶针，不是感应充电。

### 零件清单

| 零件 | 数量 | 功能 | 材料 | 依据 |
| --- | --- | --- | --- | --- |
| 笔侧磁铁 | 5 | 把笔吸到 iPad 侧边并对中 | 稀土磁铁 | Apple 回收指南步骤 7，Magnets (×5)，Rare Earth Elements |
| 笔内无线充电线圈 | 1（iFixit 列在拆出的部件中） | 感应接收电能 | 来源未给出 | iFixit 步骤 19：Wireless charging coil |
| 笔内无线充电芯片 | 1 | 管理无线充电（iFixit 标注为 likely） | Broadcom BCM59358A0（iFixit：likely） | iFixit 步骤 19 |
| iPad 侧充电板 | 1 | 侧边充电模块，承载发射线圈与相关电路 | 来源未给出 | iFixit 步骤 15 |
| iPad 侧铜充电线圈 | 来源写 coils，复数；未给只数 | 向笔内线圈耦合电能 | 铜 | iFixit 步骤 15 |
| 白色塑料外壳 | 1 | 外观件，无充电插口 | 塑料 | iFixit 步骤 17–18；回收指南也按整支笔拆解 |
| 第一代兼容笔尖 | 1（可换） | 书写；iFixit 写笔尖与上一代兼容 | 来源未给出 | iFixit 步骤 18 |

iFixit 在步骤 19 还列出了电池、点按用的电容格栅、加速度计等，它们不是本篇侧吸充电结构的主角，不列入上表作为磁路零件。

### 装配顺序

> 笔内装配工艺来源未给出逐步文件。1–3 步按回收指南与 iFixit 拆解反推；4–5 步是使用时的侧吸。

1. 在笔身贴 iPad 的那一侧，沿轴向装入五颗稀土磁铁。
2. 在对应位置装入无线充电线圈及相关电路（iFixit 在拆开后看到 coil、alignment magnets 与 BCM59358A0）。
3. 套上无开口的白色外壳（iFixit 强调可见入口几乎为零，只能切开）。
4. iPad 侧预先把 Pencil charging board 和铜线圈装到侧边充电区内侧，该处壳体加厚（iFixit 从这边撬开会更吃力）。
5. 使用时把笔的平面/侧边贴到 iPad 侧边的长条充电区，五颗磁铁吸合对中，线圈进入耦合位置后开始充电。

### 受力与运动分析

- **受力路径**：五颗沿轴向排列的磁铁与 iPad 侧边（壳体或内侧对应导磁/磁铁件，已打开来源未拆出 iPad 侧磁铁本身）互相吸引，产生垂直于侧壁的吸力，把笔保持在充电位置。感应线圈不承担保持力。来源未给出吸力数值。
- **运动关系**：吸合后笔相对侧壁没有工作滑动；线性阵列同时提供沿笔长方向的大致定位，使笔内线圈对准充电板上的铜线圈。它不像圆环阵列那样在平面内做各向自对中，也不像中心单磁铁那样绕一点对中。
- **失效风险**：iFixit 写这支出笔几乎没有可拆入口，外壳和内部钢层焊在一起，维修性差。推断：侧吸只靠磁力，笔从包里或桌上滚落时，若侧向力超过吸力就会脱落，来源未给出跌落或侧向力测试。充电完全依赖外壳两侧对准，壳厚和笔壳材料都会影响耦合，来源未给出气隙设计值。

## 设计要点与参数

| 要点 | 内容 | 依据 |
| --- | --- | --- |
| 磁铁数量与类别 | 五颗，稀土磁铁，沿笔身一侧布置 | Apple 回收指南步骤 7 |
| 对中几何 | 线性侧吸，不是圆环，也不是盘心单磁铁 | 回收指南图示；iFixit 的侧边长条充电区 |
| 传能方式 | 感应耦合：笔内 wireless charging coil，iPad 侧 copper charging coils | iFixit 步骤 15、18、19 |
| 有无外露触点 | 无。第 2 代从外观即可由「没有 Lightning 插口」辨认（回收指南也写 absence of a Lightning connector） | Apple 回收指南识别段；iFixit 步骤 17 写可见入口为零 |
| iPad 侧模块 | 独立的 Pencil charging board，铜线圈附在板上 | iFixit 步骤 15 |
| 充电区外观 | 侧边一条深色长椭圆 | iFixit 步骤 3 |
| 壳体局部加厚 | 充电区附近壳体更厚，从这边撬开会更困难 | iFixit 步骤 4 |
| 笔内充电芯片 | Broadcom BCM59358A0，iFixit 标注为 likely | iFixit 步骤 19 |
| 笔尖 | 与上一代笔尖兼容 | iFixit 步骤 18 |
| 磁铁牌号、单颗尺寸、吸力、线圈匝数、气隙 | 来源未给出 | 已打开的两份来源均未列 |

## 优缺点

**优点**
- 取消笔尾 Lightning 插头，整支笔可以做成闭合外壳，侧边一贴就能充。
- 线性磁铁与长条线圈是匹配的：笔是细长件，用一排磁铁而不是圆环，才能和侧壁的长条充电区对上。
- 磁铁负责保持和对中，线圈负责传能，两者沿同一条侧边布置，功能分开。
- iPad 侧做成独立充电板，损坏时至少在结构上与主板分离（iFixit 作为可拆下的一块板取出；整机维修性仍受胶和薄边框限制）。

**缺点 / 代价**
- 已打开来源没有吸力、气隙和线圈参数，无法按窗口做等效设计。
- 笔身几乎不可拆，回收指南也是破坏性撬磁铁，日常维修不友好。
- 只靠磁力侧挂，没有机械锁，存在意外碰落的风险，来源未给出保持力。
- iPad 必须在侧壁让出加厚的充电区和一块长条板，对薄边框是额外约束。

## 可借鉴点

- **细长附件要侧充时，用线性磁铁阵列，不要套用手机的圆环或手表的中心单磁铁。** 阵列的长度应与发射线圈的布置一致。
- **磁铁对中、线圈传能，外壳上不要再开充电口。** 气隙和壳厚会进入耦合，需要在加厚壳体（iFixit 观察到充电区更厚）和充电效率之间做取舍。
- **把发射端做成独立的侧边充电板**，便于在整机里单独布置铜线圈，而不把线圈堆到主板上。
- 若需要可脱落的大电流触点连接，应去看笔记本 MagSafe 1-2，而不是把这五颗磁铁改成弹针。

## 与库中相似案例对比

| 对比项 | 本案例（Apple Pencil 2 侧吸） | [[iPhone MagSafe 环形磁铁阵列：18 颗磁铁把线圈对中并对附件保持]] | [[Apple Watch 磁吸充电盘：中心单颗磁铁对位与电感耦合（对照手机环形阵列）]] | [[MagSafe 1-2 笔记本磁吸充电头：磁力保持触点对中，拉力过大时整头脱落]] |
| --- | --- | --- | --- | --- |
| 磁力几何 | 沿笔身的五颗线性磁铁 | 线圈周围的圆环（iPhone 12 为 18 颗） | 盘心单颗磁铁 | 插头端面与插座吸合 |
| 传能 | 侧边感应线圈 | 背面感应线圈 | 盘内利兹线线圈 | 五枚弹簧顶针 |
| 贴合面 | iPad 侧壁的长条区 | 手机背面 | 圆形表背 | 插座平面 |
| 何时用这篇 | 细长手写笔、电容笔、侧挂充电 | 大平面无线充或附件对中 | 圆形表类充电盘 | 可脱落的有线磁吸电源头 |

## 相关案例

- [[iPhone MagSafe 环形磁铁阵列：18 颗磁铁把线圈对中并对附件保持]]
- [[Apple Watch 磁吸充电盘：中心单颗磁铁对位与电感耦合（对照手机环形阵列）]]
- [[MagSafe 1-2 笔记本磁吸充电头：磁力保持触点对中，拉力过大时整头脱落]]
- [[Pogo Pin 弹簧顶针：针头、弹簧与针管的工作行程和弹力]]
- 分类索引：[[02-连接与紧固 索引]]

## 来源与核实记录

- 主来源：[Apple Pencil (2nd generation) Recycler Guide](https://www.apple.com/recycling/recycler-guides/pdf/products/accessories/Apple_Pencil_2nd_Gen_Recycler_Guide_English.pdf)（Apple Inc.，© 2023；已重新下载官方 PDF。识别段写明第 2 代没有 Lightning 插口；步骤 7 与第 13 页图示要求撬下五颗磁铁，并标注 Magnets (×5)、Rare Earth Elements。）
- 补充来源：[iFixit, iPad Pro 11" Teardown](https://www.ifixit.com/Teardown/iPad+Pro+11-Inch+Teardown/115457)（指南 115457，作者 Arthur Shi。独立第二机构。步骤 3 的侧边长条充电区、步骤 4 充电区壳体加厚、步骤 15 的 Pencil charging board 与铜线圈、步骤 18–19 笔内 wireless charging coil 与 alignment magnets、BCM59358A0，均来自已打开的 API 全文。）
- 核实：2026-11-27 下载并打开上述 PDF，并打开 iFixit 指南。未引用未打开的 Apple 支持页或第一代 Pencil 拆解（指南 52955）中的结构。已打开来源未描述配对协议，故不写入。
