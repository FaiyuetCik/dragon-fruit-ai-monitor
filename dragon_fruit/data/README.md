# 病虫害数据集说明

## 目录结构

```
pest_dataset/
  train/
    healthy/        # 健康火龙果植株/果实图片
    aphids/         # 蚜虫侵害图片
    anthracnose/    # 炭疽病图片
  val/
    healthy/
    aphids/
    anthracnose/
```

## 数据收集指南

### 拍照要求
- 分辨率：建议 720P 以上
- 拍摄距离：10-50 cm，确保病害特征清晰可见
- 每类至少 30 张，建议 100 张以上
- 涵盖不同光照条件、角度、生长阶段

### 类别说明
| 类别 | 说明 | 关键特征 |
|------|------|----------|
| healthy | 健康叶片/果实 | 叶片绿色饱满，果实表皮光滑无斑 |
| aphids | 蚜虫侵害 | 叶片/嫩茎有成群小虫，蜜露分泌物，叶片卷曲 |
| anthracnose | 炭疽病 | 褐色凹陷斑块，边缘深褐色，有时有同心轮纹 |

## 训练命令

```bash
cd <project-root>
python dragon_fruit/data/train_pest.py --epochs 50 --img 224 --batch 32
```
