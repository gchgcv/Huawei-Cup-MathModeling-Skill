# 深层参考：Word 公式与 DOCX

## 要求

- 行间和行内数学表达式应使用可编辑的 Word 公式对象（OMML）。
- 不用截图或普通文本冒充公式。
- 公式编号、正文引用和符号表保持一致。
- 生成后必须检查 DOCX 内是否存在 OMML，并人工或渲染检查复杂公式。

## 验证

可运行：

```bash
python scripts/verify_docx_math.py paper.docx --min-equations 1
```

该脚本只能检查结构和明显的原始 LaTeX，不等同于视觉渲染正确。矩阵、分段函数、多行公式和编号仍需打开 Word 或渲染后检查。
