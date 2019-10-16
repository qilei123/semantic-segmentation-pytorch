from pycocotools.coco import COCO
import os
root_dataset = "/data0/qilei_chen/old_alien/AI_EYE_IMGS/ROP_DATASET_with_label/9LESIONS/"
annotation_folder = "annotations"
anno_filename = "ridge_in_one_instances_train2014.json"
cocoAnno = COCO(os.path.join(root_dataset,annotation_folder,anno_filename))

imgIds = cocoAnno.getImgIds()
width_vs_height = [0 for i in range(30)]
seg_vs_img = [0 for i in range(30)]
for imgId in imgIds:
    img_record = cocoAnno.loadImgs([imgId])[0]
    annIds = cocoAnno.getAnnIds(imgIds = [img_record["id"]])
    anns = cocoAnno.loadAnns(annIds)
    for ann in anns:
        print(ann)
        mask = cocoAnno.annToMask(anns[0])
        seg_count = mask[(mask==1)]
        print(seg_count.size)
        
    break
