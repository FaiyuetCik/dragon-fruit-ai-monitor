const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, LevelFormat,
  TableOfContents, HeadingLevel, BorderStyle, WidthType, ShadingType,
  PageNumber, PageBreak
} = require('docx');

const border = { style: BorderStyle.SINGLE, size: 1, color: "AAAAAA" };
const borders = { top: border, bottom: border, left: border, right: border };
const cellMargins = { top: 80, bottom: 80, left: 120, right: 120 };

const h1 = t => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: t, font: "Microsoft YaHei", size: 32, bold: true })] });
const h2 = t => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text: t, font: "Microsoft YaHei", size: 28, bold: true })] });
const h3 = t => new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun({ text: t, font: "Microsoft YaHei", size: 26, bold: true })] });
const p = (t, o = {}) => new Paragraph({ spacing: { after: 100, line: 360 }, indent: o.i ? { firstLine: 480 } : undefined, children: [new TextRun({ text: t, font: o.m ? "Consolas" : "SimSun", size: o.m ? 18 : 22 })] });
const pc = t => new Paragraph({ spacing: { after: 60, line: 320 }, children: [new TextRun({ text: t, font: "Consolas", size: 18 })] });
const c = (t, w, o = {}) => new TableCell({ borders, width: { size: w, type: WidthType.DXA }, margins: cellMargins, shading: o.s ? { fill: o.s, type: ShadingType.CLEAR } : undefined, children: [new Paragraph({ children: [new TextRun({ text: t, font: o.b ? "Microsoft YaHei" : "SimSun", size: 20, bold: !!o.b })] })] });
const tr = cells => new TableRow({ children: cells });
const tbl = (cols, rows) => new Table({ width: { size: 9026, type: WidthType.DXA }, columnWidths: cols, rows });
const pb = () => new Paragraph({ children: [new PageBreak()] });

function monoBlock(lines) {
  return lines.map(l => pc(l));
}

async function main() {
  const doc = new Document({
    styles: {
      default: { document: { run: { font: "SimSun", size: 22 } } },
      paragraphStyles: [
        { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 32, bold: true, font: "Microsoft YaHei" }, paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0 } },
        { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 28, bold: true, font: "Microsoft YaHei" }, paragraph: { spacing: { before: 280, after: 160 }, outlineLevel: 1 } },
        { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 26, bold: true, font: "Microsoft YaHei" }, paragraph: { spacing: { before: 200, after: 120 }, outlineLevel: 2 } },
      ]
    },
    numbering: {
      config: [
        { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "●", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
        { reference: "numbers", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      ]
    },
    sections: [
      // ====== COVER PAGE ======
      { properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
        children: [
          new Paragraph({ spacing: { before: 3200 } }),
          new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 360 }, children: [new TextRun({ text: "火龙果 AI 视觉监控系统", font: "Microsoft YaHei", size: 52, bold: true, color: "2D5016" })] }),
          new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [new TextRun({ text: "Dragon Fruit AI Vision Monitoring System", font: "Arial", size: 28, color: "888888", italics: true })] }),
          new Paragraph({ spacing: { before: 500 } }),
          new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 }, children: [new TextRun({ text: "项目技术文档", font: "Microsoft YaHei", size: 36, bold: true })] }),
          new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 }, children: [new TextRun({ text: "基于深度学习与计算机视觉的火龙果智能监控方案", font: "SimSun", size: 22, color: "555555" })] }),
          new Paragraph({ spacing: { before: 2000 } }),
          new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 }, children: [new TextRun({ text: "技术栈：Python 3.12 · PyTorch 2.12 · YOLOv5 · OpenCV · Gradio · PIL", font: "Consolas", size: 18, color: "666666" })] }),
          new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 }, children: [new TextRun({ text: "项目路径：E:\\yolov5-master\\dragon_fruit\\", font: "Consolas", size: 18, color: "666666" })] }),
          new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 }, children: [new TextRun({ text: "日期：2026 年 5 月", font: "SimSun", size: 22, color: "666666" })] }),
          new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 }, children: [new TextRun({ text: "标签语言：英文", font: "SimSun", size: 18, color: "999999" })] }),
        ] },

      // ====== TOC + CONTENT ======
      { properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
        headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "火龙果 AI 视觉监控系统 · 技术文档", font: "Microsoft YaHei", size: 16, color: "999999" })] })] }) },
        footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "- ", size: 16 }), new TextRun({ children: [PageNumber.CURRENT], size: 16 }), new TextRun({ text: " -", size: 16 })] })] }) },
        children: [
          new Paragraph({ spacing: { before: 400, after: 300 }, children: [new TextRun({ text: "目  录", font: "Microsoft YaHei", size: 36, bold: true })] }),
          new TableOfContents("目录", { hyperlink: true, headingStyleRange: "1-3" }),
          pb(),

          // ====== CHAPTER 1: 项目概述 ======
          h1("第一章  项目概述"),
          h2("1.1 项目背景"),
          p("火龙果（学名：Hylocereus undatus）是我国南方重要的热带经济作物。传统果园巡检依靠人工目视检查，存在效率低、主观性强、难以覆盖大面积果园等问题。计算机视觉和深度学习技术的发展为农业智能化管理提供了新的技术手段。", { i: true }),
          p("本系统利用 AI 视觉技术，实现对火龙果果园的智能化监控，能够自动判断果实成熟度、识别病虫害症状、监测植株生长异常状态，并将识别结果输出为分级预警信息和结构化日志记录。", { i: true }),

          h2("1.2 功能清单"),
          p("（1）果实成熟度检测 — YOLOv5s 目标检测，2 类别（Unripe / Ripe），mAP@0.5 = 0.995", { i: true }),
          p("（2）病虫害识别 — CNN 图像分类，3 类别（Healthy / Aphids / Anthracnose），含降级策略", { i: true }),
          p("（3）生长异常检测 — 纯 OpenCV 经典 CV，绿化指数 / 黄化率 / 倾斜角度", { i: true }),
          p("（4）图像预处理 — CLAHE 低光增强 + 高斯降噪 + letterbox 尺寸调整 + 归一化", { i: true }),
          p("（5）预警与日志 — 三级预警（INFO / WARNING / CRITICAL）+ CSV/JSON 双格式日志", { i: true }),
          p("（6）Web 交互界面 — Gradio 拖拽上传，实时分析，结果可视化", { i: true }),

          h2("1.3 技术栈"),
          tbl([2500, 2000, 4526], [
            tr([c("技术组件", 2500, { b: true, s: "E8F5E9" }), c("版本", 2000, { b: true, s: "E8F5E9" }), c("用途", 4526, { b: true, s: "E8F5E9" })]),
            tr([c("Python", 2500), c("3.12.7", 2000), c("主要编程语言", 4526)]),
            tr([c("PyTorch", 2500), c("2.12.0", 2000), c("深度学习推理框架", 4526)]),
            tr([c("YOLOv5", 2500), c("v6.0", 2000), c("目标检测 / 分类模型框架", 4526)]),
            tr([c("Ultralytics", 2500), c("8.3.x", 2000), c("YOLO 生态工具包", 4526)]),
            tr([c("OpenCV", 2500), c("4.13.0", 2000), c("图像处理与经典计算机视觉", 4526)]),
            tr([c("Pillow (PIL)", 2500), c("10.4.0", 2000), c("中文 / 英文文字渲染（替代 cv2.putText）", 4526)]),
            tr([c("Gradio", 2500), c("latest", 2000), c("Web 交互界面", 4526)]),
            tr([c("NumPy", 2500), c("1.26.4", 2000), c("数组计算（必须 <2.0）", 4526)]),
            tr([c("Node.js + docx", 2500), c("v18 + v9", 2000), c("Word 报告生成", 4526)]),
          ]),

          h2("1.4 设计原则"),
          p("（1）零侵入：dragon_fruit/ 独立包，不修改任何 YOLOv5 原始文件，仅通过 import 复用现有功能。", { i: true }),
          p("（2）类封装：每个模块是一个独立类，构造函数注入 MonitoringConfig，单一入口方法。", { i: true }),
          p("（3）中心化配置：所有路径、阈值、开关集中在 config.py 的 MonitoringConfig 数据类。", { i: true }),
          p("（4）统一输出契约：MonitoringResult 数据类定义 JSON 可序列化输出格式。", { i: true }),
          p("（5）优雅降级：病虫害模型未训练时自动跳过，不影响成熟度检测和生长异常分析。", { i: true }),
          pb(),

          // ====== CHAPTER 2: 系统架构与数据流 ======
          h1("第二章  系统架构与数据流"),

          h2("2.1 整体架构"),
          p("系统采用模块化流水线架构（Pipeline Architecture）。输入图像依次流经四个核心处理阶段，最终由预警引擎汇总评估并输出报告。", { i: true }),
          p("系统架构图（数据流）：", { i: true }),
          ...monoBlock([
            "  输入图像 (BGR uint8)",
            "       |",
            "       v",
            "  [1] PreprocessingPipeline    CLAHE -> Denoise -> Letterbox -> ToTensor",
            "       |                         RGB float32 (1,3,640,H)",
            "       +----------+----------+----------+",
            "       |          |          |          |",
            "       v          v          v          v",
            "  [2] Maturity  [3] Pest    [4] Growth   (并行概念，实际串行)",
            "   Detector     Classifier  Detector",
            "   YOLOv5推理   CNN分类      HSV + Edge",
            "       |          |          |",
            "       v          v          v",
            "  MonitoringResult (统一数据类)",
            "       |",
            "       v",
            "  [5] AlertEngine  6条规则评估 -> List<Alert>",
            "       |",
            "       v",
            "  输出: JSON报告 + 标注图 + CSV预警日志",
          ]),

          h2("2.2 模块依赖关系"),
          p("各模块之间的 import 依赖关系（箭头方向 = 被依赖方）：", { i: true }),
          ...monoBlock([
            "  cli.py",
            "    -> config.py (MonitoringConfig)",
            "    -> pipeline/orchestrator.py (DragonFruitMonitor)",
            "    -> web/app.py (run_server, lazy --serve only)",
            "",
            "  pipeline/orchestrator.py",
            "    -> preprocessing/pipeline.py",
            "    -> detection/maturity.py",
            "    -> classification/pest_disease.py",
            "    -> growth/anomaly.py",
            "    -> pipeline/alert.py",
            "    -> pipeline/report.py",
            "",
            "  detection/maturity.py",
            "    -> detection/result_formatter.py",
            "    -> pipeline/draw_utils.py (put_chinese_text_with_bg)",
            "    -> YOLOv5: models.common.DetectMultiBackend",
            "    -> YOLOv5: utils.general (non_max_suppression, scale_boxes)",
            "    -> YOLOv5: utils.torch_utils.select_device",
            "",
            "  classification/pest_disease.py",
            "    -> YOLOv5: models.common.DetectMultiBackend",
            "    -> YOLOv5: utils.augmentations.classify_transforms",
            "",
            "  growth/anomaly.py",
            "    -> growth/color_analysis.py",
            "    -> growth/geometry.py",
            "",
            "  preprocessing/transforms.py",
            "    -> YOLOv5: utils.augmentations.letterbox",
          ]),

          h2("2.3 YOLOv5 复用组件清单"),
          p("dragon_fruit/ 通过 import 复用以下 YOLOv5 原生功能，不重复造轮子：", { i: true }),
          tbl([2200, 3500, 3326], [
            tr([c("YOLOv5 路径", 2200, { b: true, s: "E8F5E9" }), c("功能", 3500, { b: true, s: "E8F5E9" }), c("使用位置", 3326, { b: true, s: "E8F5E9" })]),
            tr([c("utils.augmentations.letterbox", 2200), c("保持宽高比的尺寸调整 + 填充", 3500), c("preprocessing/transforms.py", 3326)]),
            tr([c("utils.augmentations.classify_transforms", 2200), c("分类预处理（224x224 + 归一化）", 3500), c("classification/pest_disease.py", 3326)]),
            tr([c("models.common.DetectMultiBackend", 2200), c("统一模型加载器（检测+分类）", 3500), c("maturity.py, pest_disease.py", 3326)]),
            tr([c("utils.general.non_max_suppression", 2200), c("NMS 后处理", 3500), c("detection/maturity.py", 3326)]),
            tr([c("utils.general.scale_boxes", 2200), c("边界框从模型尺寸缩放到原图", 3500), c("detection/maturity.py", 3326)]),
            tr([c("utils.torch_utils.select_device", 2200), c("设备选择（CPU/CUDA）", 3500), c("maturity.py, pest_disease.py", 3326)]),
          ]),
          pb(),

          // ====== CHAPTER 3: 详细模块设计 ======
          h1("第三章  详细模块设计"),

          h2("3.1 预处理模块（preprocessing/）"),
          p("PreprocessingPipeline 类 — 可配置的 5 步预处理流水线。输入 BGR uint8 (H,W,3)，输出 RGB float32 tensor (1,3,640,H)，范围 [0,1]。", { i: true }),

          h3("3.1.1 enhancers.py"),
          p("apply_clahe(image, clip_limit=2.0, tile_grid_size=(8,8)) → np.ndarray：将 BGR 图转换到 LAB 空间，对 L 通道做 CLAHE 自适应直方图均衡化，增强低光对比度。", { i: true }),
          p("adjust_brightness_contrast(image, alpha=1.2, beta=10) → np.ndarray：cv2.convertScaleAbs 调整对比度（alpha）和亮度（beta）。", { i: true }),

          h3("3.1.2 denoisers.py"),
          p("denoise_gaussian(image, kernel_size=(5,5)) → np.ndarray：高斯模糊降噪，速度快。", { i: true }),
          p("denoise_nlm(image, h=10, h_color=10, template_size=7, search_size=21) → np.ndarray：非局部均值降噪，效果好但慢。", { i: true }),
          p("denoise_fast(image) → np.ndarray：便捷函数，内部调用 denoise_gaussian(kernel_size=(3,3))。", { i: true }),

          h3("3.1.3 transforms.py"),
          p("resize_letterbox(image, target_size=(640,640), stride=32, auto=True) → np.ndarray：调用 YOLOv5 原生 letterbox()，保持宽高比填充至目标尺寸，确保尺寸是 stride 的整数倍。", { i: true }),
          p("to_tensor(image) → torch.Tensor：HWC→CHW 转置，BGR→RGB，÷255 归一化，添加 batch 维度。返回 (1,3,H,W) float32。", { i: true }),

          h3("3.1.4 pipeline.py"),
          p("PreprocessingPipeline.__call__(image) → torch.Tensor：按 config 开关依次执行：adjust_brightness_contrast → apply_clahe → denoise_fast → resize_letterbox → to_tensor。每个步骤可由 MonitoringConfig 中的 boolean 开关独立控制。", { i: true }),

          h2("3.2 成熟度检测模块（detection/）"),
          p("MaturityDetector 类 — 封装 YOLOv5 DetectMultiBackend 的目标检测推理。", { i: true }),
          p("__init__(config)：调用 select_device() 选择计算设备，DetectMultiBackend() 加载模型权重，model.warmup() 预热。", { i: true }),
          p("detect(preprocessed_tensor) → List[dict]：将预处理 tensor 送入模型 → NMS 后处理 → scale_boxes 缩放回原图坐标 → format_detections() 格式化。返回每个检测框的 class_name / label_en / maturity / confidence / bbox。", { i: true }),
          p("annotate(image, results) → np.ndarray：使用 PIL draw_utils 在图上画绿色（成熟）/ 橙色（未熟）边界框和英文标签。", { i: true }),
          p("detect_on_image(image, preprocessed_tensor) → (results, annotated)：一站式方法，返回检测结果和标注图。", { i: true }),
          p("类别映射（来自 K.yaml）：shenghlg → Unripe，huolongguo → Ripe。", { i: true }),

          h2("3.3 病虫害分类模块（classification/）"),
          p("PestDiseaseClassifier 类 — CNN 图像分类器，识别 3 类病虫害。", { i: true }),
          p("__init__(config)：若 config.pest_weights 存在则加载模型，否则日志提示跳过。available 属性标识模型是否可用。", { i: true }),
          p("classify(image, top_k=3) → List[dict]：将图像 resize 到 224x224 → 送入模型 → softmax → 返回 Top-K 预测（class_id / label_en / confidence）。模型未加载时返回降级标记。", { i: true }),
          p("classify_crops(image, detection_boxes) → List[List[dict]]：对成熟度检测出的每个果实区域裁剪后逐一分类。", { i: true }),
          p("预定义类别：0 = Healthy，1 = Aphids，2 = Anthracnose。", { i: true }),

          h2("3.4 生长异常检测模块（growth/）"),
          p("GrowthAnomalyDetector 类 — 纯 OpenCV 经典 CV，无需深度学习模型。analyze(image) 返回生长异常分析结果。", { i: true }),

          h3("3.4.1 color_analysis.py — HSV 颜色分析"),
          p("compute_greenness_index(image) → float：HSV 色相 35-85 范围（绿色）像素占比。低于 0.30 触发绿化不足告警。", { i: true }),
          p("compute_yellowness_ratio(image) → float：HSV 色相 20-35 范围（黄色）在非果实区域（排除色相 0-10 和 160-180 的红色/紫色）中的占比。高于 0.15 触发黄化告警。", { i: true }),
          p("segment_foliage(image) → np.ndarray：绿色掩码 + 形态学闭/开运算去噪，输出二值前景掩码。", { i: true }),

          h3("3.4.2 geometry.py — 几何分析"),
          p("detect_tilt_angle(image) → float：灰度 → 高斯模糊 → Canny 边缘检测（阈值 50/150）→ 概率 Hough 线检测（threshold=100, minLineLength=80, maxLineGap=20）→ 计算所有线段角度 → 取中位数。高于 15° 触发倾斜告警。", { i: true }),
          p("estimate_plant_coverage(image, green_mask) → float：植株绿色区域占画面比例。", { i: true }),

          h3("3.4.3 HSV 阈值参考表"),
          tbl([2500, 2000, 2000, 2526], [
            tr([c("检测目标", 2500, { b: true, s: "E8F5E9" }), c("H 范围", 2000, { b: true, s: "E8F5E9" }), c("S/V 范围", 2000, { b: true, s: "E8F5E9" }), c("用途", 2526, { b: true, s: "E8F5E9" })]),
            tr([c("绿色叶片", 2500), c("35 - 85", 2000), c("40-255", 2000), c("绿化指数", 2526)]),
            tr([c("黄色/枯黄", 2500), c("20 - 35", 2000), c("40-255", 2000), c("黄化率", 2526)]),
            tr([c("红色/紫色果实", 2500), c("0-10, 160-180", 2000), c("40-255", 2000), c("果实排除掩码", 2526)]),
          ]),

          h2("3.5 流水线调度模块（pipeline/）"),

          h3("3.5.1 orchestrator.py — 顶层调度器"),
          p("DragonFruitMonitor 类 — 系统总调度器，聚合所有子模块。", { i: true }),
          p("__init__(config)：构造 PreprocessingPipeline / MaturityDetector / PestDiseaseClassifier / GrowthAnomalyDetector / AlertEngine / LogWriter。各子模块根据 config 开关决定是否启用。", { i: true }),
          p("process_image(image_path) → MonitoringResult：完整处理流水线 — 读取图像 → 预处理 → 成熟度检测 → 病虫害分类 → 生长异常分析 → 预警评估 → CSV 日志记录 → 生成摘要。", { i: true }),
          p("process_and_save(image_path, output_dir) → MonitoringResult：在 process_image 基础上额外保存标注图和 JSON 日志。", { i: true }),
          p("process_directory(dir_path, output_dir) → List[MonitoringResult]：批量处理 + 生成 batch_report.json。", { i: true }),

          h3("3.5.2 MonitoringResult 数据类"),
          p("统一的 JSON 可序列化输出契约，字段：image_path / timestamp / maturity_detections / pest_disease_results / growth_anomalies / alerts / annotated_image_path / summary。", { i: true }),

          h3("3.5.3 alert.py — 预警与日志"),
          p("AlertLevel 枚举：INFO / WARNING / CRITICAL。", { i: true }),
          p("AlertEngine：内置 6 条 AlertRule，evaluate(result) 方法遍历所有规则并返回触发的 Alert 列表。", { i: true }),
          p("LogWriter：write_csv(alerts, image_path) 写入每日 CSV 日志（UTF-8 BOM 编码）；write_json_log(result, output_path) 写入完整 JSON 日志。", { i: true }),
          tbl([2500, 1500, 5026], [
            tr([c("规则名", 2500, { b: true, s: "FFF3E0" }), c("等级", 1500, { b: true, s: "FFF3E0" }), c("触发条件", 5026, { b: true, s: "FFF3E0" })]),
            tr([c("anthracnose_detected", 2500), c("CRITICAL", 1500), c("病虫害分类结果包含 Anthracnose", 5026)]),
            tr([c("aphids_detected", 2500), c("WARNING", 1500), c("病虫害分类结果包含 Aphids", 5026)]),
            tr([c("no_ripe_fruit", 2500), c("INFO", 1500), c("未检测到任何果实", 5026)]),
            tr([c("leaf_yellowing", 2500), c("WARNING", 1500), c("黄化率 > 15%", 5026)]),
            tr([c("plant_tilting", 2500), c("WARNING", 1500), c("倾斜角度 > 15°", 5026)]),
            tr([c("low_greenness", 2500), c("WARNING", 1500), c("绿化指数 < 30%", 5026)]),
          ]),

          h3("3.5.4 report.py — 报告生成"),
          p("generate_summary_text(result) → str：生成一行英文摘要，包含成熟度统计、病虫害结果、生长异常数量和预警统计。", { i: true }),
          p("save_annotated_image(image, result, output_path) → Path：使用 PIL（非 cv2.putText）渲染英文标签，绘制边界框、左上角信息面板和分级预警覆盖。", { i: true }),
          p("generate_json_report(results, output_path) → Path：将 MonitoringResult 列表序列化为 JSON 文件（ensure_ascii=False, indent=2）。", { i: true }),

          h3("3.5.5 draw_utils.py — 文字渲染"),
          p("关键设计决策：cv2.putText() 的 Hershey 字体不支持任何非 ASCII 字符（中文、日文等均显示为 ????）。因此本系统所有图像文字渲染统一使用 PIL/Pillow。", { i: true }),
          p("put_chinese_text(img, text, org, font_size, color)：在 OpenCV BGR 图像上绘制文字。流程：BGR→RGB→PIL Image→ImageDraw→写回原 numpy 数组。", { i: true }),
          p("put_chinese_text_with_bg(img, text, org, font_size, text_color, bg_color)：带半透明背景的文字（RGBA alpha 合成），用于标注图标签和预警信息。", { i: true }),
          p("字体优先级：Microsoft YaHei (msyh.ttc) > SimHei > SimSun > KaiTi。", { i: true }),

          h2("3.6 Web 界面（web/）"),
          p("Gradio Blocks 构建的交互式界面。build_interface() 创建 UI 布局：上传区 / 原图与标注图并排对比 / 成熟度表格 / 病虫害表格 / 生长异常指标 / 农事建议 / 预警列表。", { i: true }),
          p("analyze(image) 回调函数：临时保存上传图 → 调用 DragonFruitMonitor.process_and_save() → 读取标注图 → 格式化 Markdown 表格 → 返回 Gradio 展示元组。", { i: true }),
          p("run_server(port, share)：设置 NO_PROXY 环境变量（解决企业代理导致的 502 错误）→ 启动 Gradio 服务器。", { i: true }),

          h2("3.7 数据增强模块（data/）"),
          p("augmentation.py — augment_image(image) 生成 11 种增强变体：水平翻转、3 角度旋转、±30 亮度、×0.7/×1.3 对比度、高斯模糊、±10° HSV 色调偏移。expand_dataset() 对训练集批量增强并复制标注文件。", { i: true }),
          p("retrain.py — 调用 YOLOv5 train.py 重新训练成熟度模型。自动检测增强数据集，存在则使用 K_augmented.yaml。", { i: true }),
          p("train_pest.py — 调用 YOLOv5 classify/train.py 训练病虫害分类器。无需标注，按文件夹类别自动识别。", { i: true }),
          pb(),

          // ====== CHAPTER 4: 配置参数手册 ======
          h1("第四章  配置参数手册"),
          p("所有可调参数集中在 config.py 的 MonitoringConfig 数据类中。以下列出全部参数及其默认值和用途。", { i: true }),

          h2("4.1 路径配置"),
          tbl([2500, 4526, 2000], [
            tr([c("参数", 2500, { b: true, s: "E8F5E9" }), c("默认值", 4526, { b: true, s: "E8F5E9" }), c("类型", 2000, { b: true, s: "E8F5E9" })]),
            tr([c("weights", 2500), c("runs/train/exp4/weights/best.pt", 4526), c("Path", 2000)]),
            tr([c("data_yaml", 2500), c("yolo_dataset/K.yaml", 4526), c("Path", 2000)]),
            tr([c("pest_weights", 2500), c("None（跳过病虫害检测）", 4526), c("Optional[Path]", 2000)]),
            tr([c("output_dir", 2500), c("runs/dragon_fruit", 4526), c("Path", 2000)]),
            tr([c("log_dir", 2500), c("runs/dragon_fruit/logs", 4526), c("Path", 2000)]),
          ]),

          h2("4.2 检测参数"),
          tbl([2500, 2000, 4526], [
            tr([c("参数", 2500, { b: true, s: "E8F5E9" }), c("默认值", 2000, { b: true, s: "E8F5E9" }), c("说明", 4526, { b: true, s: "E8F5E9" })]),
            tr([c("conf_thres", 2500), c("0.25", 2000), c("检测置信度阈值，低于此值的检测框被过滤", 4526)]),
            tr([c("iou_thres", 2500), c("0.45", 2000), c("NMS IoU 阈值，去除重叠框", 4526)]),
            tr([c("imgsz", 2500), c("(640, 640)", 2000), c("模型输入尺寸 (height, width)", 4526)]),
            tr([c("target_size", 2500), c("(640, 640)", 2000), c("预处理 resize 目标尺寸", 4526)]),
            tr([c("device", 2500), c('""（自动）', 2000), c("计算设备：'0'=GPU0, 'cpu'=CPU", 4526)]),
          ]),

          h2("4.3 生长异常阈值"),
          tbl([2500, 2000, 4526], [
            tr([c("参数", 2500, { b: true, s: "E8F5E9" }), c("默认值", 2000, { b: true, s: "E8F5E9" }), c("说明", 4526, { b: true, s: "E8F5E9" })]),
            tr([c("greenness_threshold", 2500), c("0.30", 2000), c("绿化指数低于此值触发 low_greenness 警告", 4526)]),
            tr([c("yellowness_threshold", 2500), c("0.15", 2000), c("黄化率高于此值触发 leaf_yellowing 警告", 4526)]),
            tr([c("tilt_threshold", 2500), c("15.0", 2000), c("倾斜角度（度）高于此值触发 plant_tilting 警告", 4526)]),
          ]),

          h2("4.4 模块开关"),
          tbl([2500, 2000, 4526], [
            tr([c("参数", 2500, { b: true, s: "E8F5E9" }), c("默认值", 2000, { b: true, s: "E8F5E9" }), c("说明", 4526, { b: true, s: "E8F5E9" })]),
            tr([c("enable_preprocess", 2500), c("True", 2000), c("是否启用图像预处理（CLAHE+降噪）", 4526)]),
            tr([c("enable_pest", 2500), c("True", 2000), c("是否启用病虫害检测", 4526)]),
            tr([c("enable_growth", 2500), c("True", 2000), c("是否启用生长异常检测", 4526)]),
            tr([c("enable_clahe", 2500), c("True", 2000), c("预处理中是否启用 CLAHE", 4526)]),
            tr([c("enable_denoise", 2500), c("True", 2000), c("预处理中是否启用降噪", 4526)]),
            tr([c("enable_brightness_contrast", 2500), c("True", 2000), c("预处理中是否启用亮度对比度调整", 4526)]),
          ]),

          h2("4.5 算法内部常量"),
          p("以下常量定义在各自的模块文件中，不在 config.py 中（如需修改请直接编辑对应文件）：", { i: true }),
          tbl([2500, 2000, 2000, 2526], [
            tr([c("常量", 2500, { b: true, s: "F3E5F5" }), c("默认值", 2000, { b: true, s: "F3E5F5" }), c("文件", 2000, { b: true, s: "F3E5F5" }), c("说明", 2526, { b: true, s: "F3E5F5" })]),
            tr([c("CLAHE clip_limit", 2500), c("2.0", 2000), c("enhancers.py", 2000), c("对比度剪切阈值", 2526)]),
            tr([c("CLAHE tile_grid", 2500), c("(8, 8)", 2000), c("enhancers.py", 2000), c("网格大小", 2526)]),
            tr([c("alpha (contrast)", 2500), c("1.2", 2000), c("enhancers.py", 2000), c("对比度因子", 2526)]),
            tr([c("beta (brightness)", 2500), c("10", 2000), c("enhancers.py", 2000), c("亮度增量", 2526)]),
            tr([c("Gaussian kernel", 2500), c("(3,3) fast", 2000), c("denoisers.py", 2000), c("高斯核大小", 2526)]),
            tr([c("Classify input", 2500), c("(224, 224)", 2000), c("pest_disease.py", 2000), c("分类模型输入尺寸", 2526)]),
            tr([c("Canny low/high", 2500), c("50 / 150", 2000), c("geometry.py", 2000), c("边缘检测阈值", 2526)]),
            tr([c("Hough threshold", 2500), c("100", 2000), c("geometry.py", 2000), c("线检测最小投票数", 2526)]),
            tr([c("Hough minLineLength", 2500), c("80", 2000), c("geometry.py", 2000), c("最短线段长度", 2526)]),
            tr([c("Hough maxLineGap", 2500), c("20", 2000), c("geometry.py", 2000), c("最大线段间隙", 2526)]),
            tr([c("Gradio port", 2500), c("5000", 2000), c("cli.py", 2000), c("Web 服务端口", 2526)]),
          ]),
          pb(),

          // ====== CHAPTER 5: 数据集 ======
          h1("第五章  数据集"),

          h2("5.1 成熟度数据集（yolo_dataset/）"),
          p("格式：YOLO 标注（归一化 cx cy w h）。标注工具：labelImg。", { i: true }),
          tbl([1500, 1500, 1000, 5026], [
            tr([c("划分", 1500, { b: true, s: "E8F5E9" }), c("数量", 1500, { b: true, s: "E8F5E9" }), c("类别", 1000, { b: true, s: "E8F5E9" }), c("类别名（英文标签）", 5026, { b: true, s: "E8F5E9" })]),
            tr([c("train", 1500), c("54", 1500), c("2", 1000), c("shenghlg (Unripe), huolongguo (Ripe)", 5026)]),
            tr([c("val", 1500), c("9", 1500), c("2", 1000), c("shenghlg (Unripe), huolongguo (Ripe)", 5026)]),
            tr([c("test", 1500), c("7", 1500), c("2", 1000), c("shenghlg (Unripe), huolongguo (Ripe)", 5026)]),
          ]),
          p("最佳模型：runs/train/exp4/weights/best.pt — mAP@0.5=0.995, Recall=1.000。", { i: true }),

          h2("5.2 病虫害数据集（dragon_fruit/data/pest_dataset/）"),
          p("格式：标准分类目录结构（文件夹名 = 类别名），无需标注。支持直接使用 YOLOv5 classify/train.py 训练。", { i: true }),
          tbl([1000, 2000, 3000, 3026], [
            tr([c("ID", 1000, { b: true, s: "FFF3E0" }), c("类别", 2000, { b: true, s: "FFF3E0" }), c("英文", 3000, { b: true, s: "FFF3E0" }), c("选型理由", 3026, { b: true, s: "FFF3E0" })]),
            tr([c("0", 1000), c("健康", 2000), c("Healthy", 3000), c("基准对照", 3026)]),
            tr([c("1", 1000), c("蚜虫", 2000), c("Aphids", 3000), c("最常见虫害，成群附着特征明显", 3026)]),
            tr([c("2", 1000), c("炭疽病", 2000), c("Anthracnose", 3000), c("火龙果头号病害，褐色凹陷斑块", 3026)]),
          ]),
          p("当前状态：目录已建好，数据待收集。训练命令：python dragon_fruit/data/train_pest.py", { i: true }),

          h2("5.3 数据增强（dragon_fruit/data/augmentation.py）"),
          p("augment_image() 每张原图生成最多 11 种增强变体，expand_dataset() 批量处理整个训练集。增强操作包括：", { i: true }),
          p("● 几何增强：水平翻转、旋转 90°/180°/270°", { i: true }),
          p("● 光度增强：亮度 ±30、对比度 ×0.7 和 ×1.3", { i: true }),
          p("● 模糊增强：高斯模糊 5×5", { i: true }),
          p("● 颜色增强：HSV 色调 ±10°", { i: true }),
          pb(),

          // ====== CHAPTER 6: 运行与使用 ======
          h1("第六章  运行与使用"),

          h2("6.1 环境要求"),
          tbl([3000, 2000, 4026], [
            tr([c("组件", 3000, { b: true, s: "E8F5E9" }), c("最低版本", 2000, { b: true, s: "E8F5E9" }), c("说明", 4026, { b: true, s: "E8F5E9" })]),
            tr([c("Python", 3000), c("3.8+", 2000), c("推荐 3.12", 4026)]),
            tr([c("PyTorch", 3000), c("1.8.0+", 2000), c("推荐 2.0+（注意 2.6+ 需兼容修复）", 4026)]),
            tr([c("NumPy", 3000), c("< 2.0", 2000), c("必须 1.x，2.x 会导致 pandas 崩溃", 4026)]),
            tr([c("OpenCV", 3000), c("4.1.1+", 2000), c("图像处理", 4026)]),
            tr([c("Pillow", 3000), c("10.0+", 2000), c("英文文字渲染", 4026)]),
            tr([c("Ultralytics", 3000), c("8.2.34+", 2000), c("YOLO 框架", 4026)]),
            tr([c("Gradio", 3000), c("latest", 2000), c("Web 界面（可选）", 4026)]),
            tr([c("操作系统", 3000), c("Win / Linux", 2000), c("CPU / GPU 均可", 4026)]),
          ]),

          h2("6.2 安装"),
          ...monoBlock([
            "# 1. 安装 YOLOv5 基础依赖",
            "pip install -r requirements.txt",
            "# 2. 安装 Web 界面依赖（可选）",
            "pip install gradio",
            "# 3. 注意 NumPy 版本",
            "pip install \"numpy<2\"",
          ]),

          h2("6.3 CLI 命令行模式"),
          ...monoBlock([
            "cd E:\\yolov5-master",
            "",
            "# 分析单张图像",
            "python dragon_fruit_monitor.py --source 图片.jpg",
            "",
            "# 批量处理目录",
            "python dragon_fruit_monitor.py --source ./images/ --output results/",
            "",
            "# 指定自定义模型",
            "python dragon_fruit_monitor.py --source img.jpg --weights my_model.pt",
            "",
            "# 带病虫害模型",
            "python dragon_fruit_monitor.py --source img.jpg --pest-weights pest_best.pt",
            "",
            "# 禁用模块",
            "python dragon_fruit_monitor.py --source img.jpg --no-pest --no-growth",
          ]),

          h2("6.4 Web 界面模式"),
          ...monoBlock([
            "# 本地访问",
            "python dragon_fruit_monitor.py --serve --no-share",
            "# 浏览器打开 http://127.0.0.1:5000",
            "",
            "# 生成公网链接（需网络通畅）",
            "python dragon_fruit_monitor.py --serve",
          ]),

          h2("6.5 输出文件说明"),
          tbl([2500, 6526], [
            tr([c("文件", 2500, { b: true, s: "E8F5E9" }), c("内容", 6526, { b: true, s: "E8F5E9" })]),
            tr([c("{name}_annotated.jpg", 2500), c("标注图：边界框 + 标签 + 生长异常信息 + 预警覆盖", 6526)]),
            tr([c("{name}_result.json", 2500), c("单张图像的完整 JSON 结果", 6526)]),
            tr([c("batch_report.json", 2500), c("批量处理的汇总 JSON 报告", 6526)]),
            tr([c("logs/alerts_YYYY-MM-DD.csv", 2500), c("按日期归档的预警日志（UTF-8 BOM，Excel 兼容）", 6526)]),
          ]),
          pb(),

          // ====== CHAPTER 7: 关键技术细节 ======
          h1("第七章  关键技术细节"),

          h2("7.1 PyTorch 2.6+ 兼容性修复"),
          p("问题：PyTorch 2.6 将 torch.load() 的 weights_only 默认值从 False 改为 True。YOLOv5 的 checkpoint 是完整模型 pickle，包含自定义类（models.yolo.DetectionModel），被 weights_only 严格模式拒绝。", { i: true }),
          p("解决方案：dragon_fruit/__init__.py 在导入任何 YOLOv5 模块之前 monkey-patch torch.load，设置 weights_only=False。", { i: true }),
          ...monoBlock([
            "import torch",
            "_original_load = torch.load",
            "def _patched_load(*a, **kw):",
            "    kw.setdefault(\"weights_only\", False)",
            "    return _original_load(*a, **kw)",
            "torch.load = _patched_load",
          ]),

          h2("7.2 NumPy 版本约束"),
          p("NumPy 2.x 导致 pandas._libs 和 pyarrow.lib 导入崩溃（'numpy.core.multiarray failed to import'）。必须降级到 numpy<2。当前安装版本 1.26.4。", { i: true }),

          h2("7.3 文字渲染方案"),
          p("cv2.putText() 的 Hershey 内置字体仅支持 ASCII/Latin 字符，所有非 ASCII 字符（包括中文 CJK）均渲染为 ????。因此系统所有图像标注使用 PIL/Pillow 的 TrueType 字体渲染。", { i: true }),
          p("字体查找优先级：C:/Windows/Fonts/msyh.ttc（微软雅黑）> simhei.ttf（黑体）> simsun.ttc（宋体）> simkai.ttf（楷体）。当前系统标签使用英文，PIL 渲染同样适用。", { i: true }),

          h2("7.4 Gradio 代理兼容性"),
          p("部分企业网络环境下，系统代理设置会拦截 localhost 请求，导致 Gradio 启动时的健康检查失败（502 Bad Gateway）。", { i: true }),
          p("解决方案：web/app.py 的 run_server() 在启动前设置 NO_PROXY=localhost,127.0.0.1 环境变量。", { i: true }),
          pb(),

          // ====== CHAPTER 8: 总结与展望 ======
          h1("第八章  总结与展望"),

          h2("8.1 项目成果"),
          p("（1）成熟度检测：YOLOv5s 2 类目标检测，mAP@0.5 = 0.995，准确识别 Unripe / Ripe。", { i: true }),
          p("（2）病虫害识别：CNN 3 类分类（Healthy / Aphids / Anthracnose），含优雅降级策略。", { i: true }),
          p("（3）生长异常检测：纯 OpenCV HSV + 边缘检测，3 维度（绿化 / 黄化 / 倾斜），无训练数据需求。", { i: true }),
          p("（4）预警系统：6 条规则 / 3 级预警 / CSV+JSON 双格式日志。", { i: true }),
          p("（5）工程化：dragon_fruit/ 独立包，零侵入 YOLOv5，CLI + Gradio 双模式，28 个 Python 文件，完整中文技术文档。", { i: true }),

          h2("8.2 后续改进方向"),
          p("（1）数据集扩充：当前 ~70 张成熟度训练图，需扩大覆盖更多角度/光照/背景。可运行 augmentation.py 离线增强。", { i: true }),
          p("（2）病虫害数据收集：pest_dataset 目录已就绪，放入图片即可训练。每类建议至少 30-50 张。", { i: true }),
          p("（3）实时摄像头采集：YOLOv5 已内置 LoadStreams（utils/dataloaders.py），需硬件适配。", { i: true }),
          p("（4）边缘部署：export.py 支持 TFLite / ONNX / TorchScript 导出，可部署到树莓派 / Jetson。", { i: true }),
          p("（5）病虫害类别扩展：增加茎腐病、介壳虫、褐斑病等更多类别。", { i: true }),
          p("（6）生长异常优化：针对火龙果植株形态优化倾斜检测，增加植株高度比、冠幅估算等指标。", { i: true }),
          p("（7）历史数据库：建立长期检测数据库，支持趋势分析和监控报表。", { i: true }),
        ]
      }
    ]
  });

  const buffer = await Packer.toBuffer(doc);
  const outPath = "E:\\yolov5-master\\dragon_fruit\\项目报告_火龙果AI视觉监控系统.docx";
  fs.writeFileSync(outPath, buffer);
  console.log("Report saved to: " + outPath);
}

main().catch(console.error);
