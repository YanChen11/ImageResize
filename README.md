# ImageResize
图片变形（将指定图片变形为特定宽高和 size 的图片）

### 设计初衷
在 DSP 系统的开发过程中，由于对接的 ADX 数量众多，而且即使同一家 ADX 的模板也是数量众多，规格各异。<br/>
然而，从易用性的角度触发，不可能要求用户上传所有尺寸的图片。所以，只能挑选一部分尺寸作为主尺寸，用户只需要上传主尺寸要求的图片，然后 DSP 系统负责变形出其他尺寸的图片。<br/>

### 变形逻辑
由于该图片变形功能是为 DSP 系统开发，所以在实际变形过程中，除了实现基本的图片变形功能外，还考虑到目标图片的合规性要求（DSP 系统中的图片会上传给 ADX 审核）<br/>
1. 如果目标图片的宽高和原始图片的宽高比例相等，即 src_width/dest_width = src_height/dest_height，那么直接对原始图片进行缩放。如果得到的目标图片 size > dest_size，则将目标图片降低质量
2. 对于目标图片的宽高和原始图片的宽高比例不相等的情况：<br/>
        1. 如果 src_width/dest_width > src_height/dest_height，首先将原始图片按照 src_height/dest_height 的比例变形得到中心图片，然后将原始图片按照 src_width/dest_width 的比例变形得到底图，然后从底图的右下角开始向左上按照 dest_width、dest_height 截取一部分作为背景图，然后将背景图模糊处理（目的是为了降低最终生成的目标图片的 size），最终将中心图片放到背景图的正中间合并成一张图片<br/>
        2. 如果 src_width/dest_width < src_height/dest_height，操作方式与上一步正好相反
        
 ### demo
原始图片（210×240）<br/>
![images](https://user-images.githubusercontent.com/22043537/111021753-9e47a680-8409-11eb-9950-e6dc995c7682.jpeg)
目标图片
1. 等比例缩放（420×480）<br/>
![f7b31d05-46fd-4e51-bf31-c044d6634d2d](https://user-images.githubusercontent.com/22043537/111021785-d6e78000-8409-11eb-918a-8d7c1214f5ca.jpeg)
2. 宽度比大于高度比（420×400）<br/>
![abd31766-793c-4c76-832e-da573520f8cb](https://user-images.githubusercontent.com/22043537/111021855-1c0bb200-840a-11eb-91a6-fef7f8760e37.jpeg)
3. 宽度比小于高度比（400×480）<br/>
![bc37f0c1-6604-4146-8183-051c6f013d40](https://user-images.githubusercontent.com/22043537/111021878-43627f00-840a-11eb-93dc-53abef46d251.jpeg)
 

三个版本的图片变形功能及参数格式都相同

### 参数格式

src_img               需要进行变形的图片（原始图片）的路径<br/>
dest_width        期望变形得到的图片（目的图片）的宽<br/>
dest_height       期望变形得到的图片（目的图片）的高<br/>
dest_size            期望变形得到的图片（目的图片）的 size 的上限<br/>

### 三个版本的图片变形的区别

第一个版本（image.py）需要借助 openCV 库，运行速度最快，但需要事先安装 openCV。并且，由于 openCV 对图片的处理非常精细，导致变形得到的图片通常 size 都会比较大。所以，很多时候为了是目标图片的 size 满足要求，需要降低图片的质量。<br/>
第二个版本（image_v2.py）为纯 Python 版本，只需要借助部分 Python 的库函数即可实现图片变形。这一版本对图片的处理虽然没有上一版本精细，但图片质量仍可满足要求。但由于是纯 Python 实现，所以运行速度会很慢，通常运行时间是第一版本的 6~7 倍。<br/>
第三个版本（image_resize）为 golang 版本，运行速度虽然不及第一版本（运行时间通常为第一版本的 2 倍），但相对于第二版本有很大提升。同时，由于对图片的处理不及第一版本精细，所以目标图片的 size 相对较小，但仍然可以满足使用要求（目标图片质量与第二版本相当）。
