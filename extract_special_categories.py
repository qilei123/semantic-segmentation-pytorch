import os
import json

def select_anns_widh_id_list(id_list,new_id_list,anno_dir,new_anno_dir):
    anno_json = json.load(open(anno_dir))
    images_dict = dict()

    for img in anno_json['images']:
        images_dict[img['id']] = img

    annos_by_image_id = dict()
    for anno in anno_json['annotations']:
        if not annos_by_image_id.has_key(anno['image_id']):
            annos_by_image_id[anno['image_id']]=[]
        annos_by_image_id[anno['image_id']].append(anno)    
    
    new_anno_json=dict()
    id_map=dict()
    count = [0,0,0]
    for index in range(len(id_list)):
        id_map[id_list[index]]=new_id_list[index]
        
    new_anno_json['categories']=[]
    new_anno_json['images']=[]
    new_anno_json['annotations']=[]
    for key in annos_by_image_id.keys():
        need_image=False
        for anno in annos_by_image_id[key]:
            if anno['category_id'] in id_list:
                anno['category_id']=id_map[anno['category_id']]
                count[anno['category_id']-1]+=1
                new_anno_json['annotations'].append(anno)
                
                need_image=True
        if need_image:
            new_anno_json['images'].append(images_dict[key])
    print(count)
    for category in anno_json['categories']:
        if category['id'] in id_list:
            category['id'] = id_map[category['id']]
            new_anno_json['categories'].append(category)
    print(len(new_anno_json['annotations']))
    print(len(new_anno_json['images']))
    with open(new_anno_dir,'w') as json_file:
        json.dump(new_anno_json,json_file)    


if __name__=="__main__":
    id_list=[4,5,6]
    new_id_list=[1,2,3]
    anno_dir='annotations/instances_train2014.json'
    new_anno_dir='annotations/ridge_in_three_instances_train2014.json'
    select_anns_widh_id_list(id_list,new_id_list,anno_dir,new_anno_dir)