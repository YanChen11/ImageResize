package main

import (
	"fmt"
	"github.com/disintegration/imaging"
	"github.com/google/uuid"
	"image"
	"log"
	"os"
	"path/filepath"
	"strconv"
	"strings"
)

var (
	originalWidth  float64
	originalHeight float64
	resizedWidth   float64
	resizedHeight  float64
	widthRatio     float64
	heightRatio    float64
	desiredWidth   float64
	desiredHeight  float64
	upperSize      int64
	quality        = 75
)

func main() {
	argvs := os.Args
	if len(argvs) != 5 {
		log.Fatal("参数不符合要求")
	}

	originalImage := argvs[1]
	//变形底图尺寸
	resizedWidth,_ = strconv.ParseFloat(argvs[2], 64)
	resizedHeight,_ = strconv.ParseFloat(argvs[3], 64)
	upperSize,_ = strconv.ParseInt(argvs[4], 10, 64)

	src, err := imaging.Open(originalImage)
	if err != nil {
		log.Fatal(err.Error())
	}
	dstImage := src

	//原图尺寸
	originalWidth = float64(src.Bounds().Dx())
	originalHeight = float64(src.Bounds().Dy())
	//变形比例
	widthRatio = resizedWidth / originalWidth
	heightRatio = resizedHeight / originalHeight

	//变形后图片尺寸
	if widthRatio > heightRatio {
		desiredWidth = originalWidth * heightRatio
		desiredHeight = resizedHeight
	} else if heightRatio > widthRatio {
		desiredWidth = resizedWidth
		desiredHeight = originalHeight * widthRatio
	}

	if widthRatio == heightRatio {
		dstImage = resize(src, int(resizedWidth), int(resizedHeight))
	} else {
	//	变形底图
		background := resize(src, int(resizedWidth), int(resizedHeight))
	//	模糊底图
		background = blur(background)
	//	变形原图
		front := resize(src, int(desiredWidth), int(desiredHeight))
	//	合并图片
		dstImage = composite(background, front)
	}

//	保存图片
	fullName, err := filepath.Abs(originalImage)
	if err != nil {
		log.Fatal(err.Error())
	}
	dir := filepath.Dir(fullName)
	fileName := filepath.Base(fullName)
	newBaseName := uuid.New().String()
	dstFileName := dir + string(filepath.Separator) + newBaseName + "." + strings.Split(fileName, ".")[1]
	err = imaging.Save(dstImage, dstFileName, imaging.JPEGQuality(quality))
	if err != nil {
		log.Fatal(err.Error())
	}
	fmt.Println(newBaseName)
//	控制图片 size
	limitSize(dstFileName, dstImage)
}

//图片变形
func resize(src image.Image, width int, height int) image.Image {
	dst := imaging.Resize(src, width, height, imaging.Lanczos)
	return dst
}

//模糊底图
func blur(src image.Image) image.Image {
	layer := 10
	for i := 1; i < layer; i++ {
		src = imaging.Blur(src, 18.0)
	}
	return src
}

//合并图片
func composite(background image.Image, front image.Image) image.Image {
	dst := imaging.PasteCenter(background, front)
	return dst
}

//限制图片 size
func limitSize(file string, src image.Image) {
	info, err := os.Stat(file)
	if err != nil {
		log.Fatal(err.Error())
	}

	if info.Size() > upperSize * 1024 {
		for info.Size() > upperSize * 1024 && quality > 0 {
			quality --
			imaging.Save(src, file, imaging.JPEGQuality(quality))
			info, _ = os.Stat(file)
		}
	}
	fmt.Println(info.Size())
}