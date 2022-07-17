# annotation_transform_pyqt

transform annotation formats for CV learning, like yolo, coco, etc.

## Environment

```
python >= 3.7
Pillow >= 8.4.0
PyQt5 >= 5.15.6
```

## How to use

just run the command `python main.py`,then it will show the pyqt window:

<div align="center">
 <img src="https://github.com/bmxbmx3/annotation_transform_pyqt/pic/main.jpg" width="60%"/>
  <br>main window</br>
  <br></br>
</div>

## What it can do

1. Transform the common annotation formats for CV learning.
2. Rename, filter in/out the label name.

## The core idea to implement this code

<div align="center">
 <img src="https://github.com/bmxbmx3/annotation_transform_pyqt/pic/concept.jpg" width="60%"/>
  <br>main window</br>
  <br></br>
</div>

We can use the compilation thought to make a middle format called "middle json", which can connect any two of the common
used annotation formats, like yolo or coco.

The basic "middle json" format is like below:

```json
{
  "image": {
    "path": "",
    "width": int,
    "height": int,
    "extra": {}
  },
  "label": [
    {
      "name": "",
      "xmin": int,
      "xmax": int,
      "ymin": int,
      "ymax": int,
      "extra": {}
    }
  ]
}
```

If you want to extend more formats, just follow the code in the "algorithm" directory to make your own.And I'm glad to welcome your PR for this project. :)