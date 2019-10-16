from pycocotools.coco import COCO
import os
import math
root_dataset = "/data0/qilei_chen/old_alien/AI_EYE_IMGS/ROP_DATASET_with_label/9LESIONS/"
annotation_folder = "annotations"
anno_filename = "ridge_in_one_instances_train2014.json"
cocoAnno = COCO(os.path.join(root_dataset,annotation_folder,anno_filename))

imgIds = cocoAnno.getImgIds()
width_vs_height = [0 for i in range(40)]
seg_vs_img = [0 for i in range(40)]
for imgId in imgIds:
    img_record = cocoAnno.loadImgs([imgId])[0]
    img_area = float(img_record["height"]*img_record["width"])
    annIds = cocoAnno.getAnnIds(imgIds = [img_record["id"]])
    anns = cocoAnno.loadAnns(annIds)
    mask = cocoAnno.annToMask(anns[0])
    width_vs_height_ratio = float(anns[0]["bbox"][2])/float(anns[0]["bbox"][3])
    wvsh_index = int(math.floor(width_vs_height_ratio/0.1))
    if wvsh_index>=40:
        width_vs_height[39]+=1
    else:
        width_vs_height[wvsh_index]+=1
    for ann in anns[1:]:
        mask += cocoAnno.annToMask(ann)
        width_vs_height_ratio = float(ann["bbox"][2])/float(ann["bbox"][3])
        wvsh_index = int(math.floor(width_vs_height_ratio/0.1))
        if wvsh_index>=40:
            width_vs_height[39]+=1
        else:
            width_vs_height[wvsh_index]+=1
    mask[mask >1]=1
    seg_count = mask[(mask==1)]
    
        
print(width_vs_height)
