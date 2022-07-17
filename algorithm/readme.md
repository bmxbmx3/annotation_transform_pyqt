# 中间标注文件格式

对于每张图片生成对应的json信息：

图片： 图片保存路径 图片长宽，可扩展其他信息

标注： 标注框的中心点，长宽（角度），可扩展其他信息

{
"image":
{
"path":"",
"width":int,
"height":int,
"extra":{}}

"label":
[
{
"name":"",
"xmin":int,
"xmax":int,
"ymin":int,
"ymax":int,
"extra":{}}
]

}