import os
import fitz

'''
功能性函数
# 将PDF转化为图片
pdfPath pdf文件的路径
imgPath 图像要保存的文件夹
zoom_x x方向的缩放系数
zoom_y y方向的缩放系数
rotation_angle 旋转角度
'''

def pdf_image(pdfPath, imgPath, filename, zoom_x, zoom_y, rotation_angle):
    print(filename)
    basepath = os.path.dirname(__file__)  # 当前文件所在路径
    print(basepath)
    # 打开PDF文件
    pdf = fitz.open(f'{basepath}/{pdfPath}{filename}.pdf')
    # 逐页读取PDF
    print(pdf.pageCount)
    for pg in range(0, pdf.pageCount):
        print(pg)
        page = pdf[pg]
        # 设置缩放和旋转系数
        trans = fitz.Matrix(zoom_x, zoom_y).preRotate(rotation_angle)
        pm = page.getPixmap(matrix=trans, alpha=False)
        # 开始写图像
        # pm.writePNG(imgPath+str(pg)+".png")
        pm.writePNG(f'{basepath}/{imgPath}{filename}.png')
    pdf.close()


# pdf_image("/Users/mfz/Code/Proletariat-Programmer/DataMask/src/static/analysis_result/1/SRR385938.tsv/plots/cluster/",
#           "/Users/mfz/Code/Proletariat-Programmer/DataMask/src/static/analysis_result/1/SRR385938.tsv/plots/cluster/",
#           "density", 5, 5, 0)

def loadall_pdf2png(uid, filename):
    cluster_list = ["density", "parallel_coordinates", "scatter"]
    loci_list = ["density", "parallel_coordinates", "scatter",
                 "similarity_matrix", "vaf_parallel_coordinates", "vaf_scatter"]
    
    for item in cluster_list:
        pdf_image(f'static/analysis_result/{uid}/{filename}/plots/cluster/',
                  f'static/analysis_result/{uid}/{filename}/plots/cluster/',
                item, 5, 5, 0)

    for item in loci_list:
        if item == "density":
            pdf_image(f'static/analysis_result/{uid}/{filename}/plots/loci/',
                    f'static/analysis_result/{uid}/{filename}/plots/loci/',
                    item, 2, 2, 0)
        else:
            pdf_image(f'static/analysis_result/{uid}/{filename}/plots/loci/',
                    f'static/analysis_result/{uid}/{filename}/plots/loci/',
                    item, 5, 5, 0)



# pdf_image("static/analysis_result/1/SRR385938.tsv/plots/cluster/",
#           "static/analysis_result/1/SRR385938.tsv/plots/cluster/",
#           "density", 5, 5, 0)


# loadall_pdf2png(1, "SRR385938.tsv")
