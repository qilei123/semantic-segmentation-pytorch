from pycocotools.coco import COCO
import os
root_dataset = "/data0/qilei_chen/old_alien/AI_EYE_IMGS/ROP_DATASET_with_label/9LESIONS/"
annotation_folder = "train2014"
anno_filename = "ridge_in_one_instances_train2014.json"
cocoAnno = COCO(os.path.join(root_dataset,annotation_folder,anno_filename))

imgIds = cocoAnno.getImgIds()

for imgId in imgIds:
    img_record = cocoAnno.loadImgs([imgId])[0]
    print(img_record)
