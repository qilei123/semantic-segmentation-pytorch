# System libs
import os
import argparse
from distutils.version import LooseVersion
# Numerical libs
import numpy as np
import torch
import torch.nn as nn
from scipy.io import loadmat
import csv
# Our libs
from dataset import TestDataset,TestROPRidgeDataset
from models import ModelBuilder, SegmentationModule
from utils import colorEncode, find_recursive, setup_logger
from lib.nn import user_scattered_collate, async_copy_to
from lib.utils import as_numpy
from PIL import Image
from tqdm import tqdm
from config import cfg
from torchvision import transforms
colors = loadmat('data/color150.mat')['colors']
names = {}
with open('data/object150_info.csv') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        names[int(row[0])] = row[5].split(";")[0]


def visualize_result(data, pred, cfg):
    (img, info) = data
    
    #for i in range(3):
    #img[:,:,2] = img[:,:,2]-img[:,:,2]*gt_mask+255*gt_mask
    # print predictions in descending order
    pred = np.int32(pred)
    pixs = pred.size
    uniques, counts = np.unique(pred, return_counts=True)
    print("Predictions in [{}]:".format(info))
    for idx in np.argsort(counts)[::-1]:
        name = names[uniques[idx] + 1]
        ratio = counts[idx] / pixs * 100
        if ratio > 0.1:
            print("  {}: {:.2f}%".format(name, ratio))

    # colorize prediction
    pred_color = colorEncode(pred, colors).astype(np.uint8)

    # aggregate images and save
    im_vis = np.concatenate((img, pred_color), axis=1)

    img_name = info.split('/')[-1]
    Image.fromarray(im_vis).save(
        os.path.join(cfg.TEST.result, img_name.replace('.jpg', '.png')))
def imresize(im, size, interp='bilinear'):
    if interp == 'nearest':
        resample = Image.NEAREST
    elif interp == 'bilinear':
        resample = Image.BILINEAR
    elif interp == 'bicubic':
        resample = Image.BICUBIC
    else:
        raise Exception('resample method undefined!')

    return im.resize(size, resample)
def round2nearest_multiple(x, p):
    #return x
    return ((x - 1) // p + 1) * p

def img_transform( img):
    # 0-255 to 0-1
    img = np.float32(np.array(img)) / 255.
    #print(np.unique(img))
    img = img.transpose((2, 0, 1))
    normalize = transforms.Normalize(
        mean=[0.5, 0.5, 0.5],
        std=[0.5, 0.5, 0.5])
    img = normalize(torch.from_numpy(img.copy()))
    #print(torch.max(img))
    return img
def load_image(image_path,imgMinSize = 1200,imgMaxSize = 1600,padding_constant = 4):

    img = Image.open(image_path).convert('RGB')

    
    ori_width, ori_height = img.size

    img_resized_list = []
    this_short_size = imgMinSize
    # calculate target height and width
    scale = min(this_short_size / float(min(ori_height, ori_width)),
                imgMaxSize / float(max(ori_height, ori_width)))
    target_height, target_width = int(ori_height * scale), int(ori_width * scale)

    # to avoid rounding in network
    target_width = round2nearest_multiple(target_width, padding_constant)
    target_height = round2nearest_multiple(target_height, padding_constant)

    # resize images
    img_resized = imresize(img, (target_width, target_height), interp='bilinear')


    # image transform, to torch float tensor 3xHxW
    img_resized = img_transform(img_resized)
    img_resized = torch.unsqueeze(img_resized, 0)
    img_resized_list.append(img_resized)

    output = dict()
    output['img_ori'] = np.array(img)
    output['img_data'] = [x.contiguous() for x in img_resized_list]
    output['info'] = os.path.basename(image_path)

    return output

def test(segmentation_module, image_path, gpu):
    segmentation_module.eval()

    batch_data = load_image(image_path)
    segSize = (batch_data['img_ori'].shape[0],
                batch_data['img_ori'].shape[1])
    img_resized_list = batch_data['img_data']

    with torch.no_grad():
        scores = torch.zeros(1, cfg.DATASET.num_class, segSize[0], segSize[1])
        scores = async_copy_to(scores, gpu)

        for img in img_resized_list:
            feed_dict = batch_data.copy()
            feed_dict['img_data'] = img
            del feed_dict['img_ori']
            del feed_dict['info']
            feed_dict = async_copy_to(feed_dict, gpu)
            # forward pass
            pred_tmp = segmentation_module(feed_dict, segSize=segSize)
            scores = scores + pred_tmp / 1#len(cfg.DATASET.imgSizes)
        
        _, pred = torch.max(scores, dim=1)
        pred = as_numpy(pred.squeeze(0).cpu())

    # visualization
    visualize_result(
        (batch_data['img_ori'], batch_data['info']),
        pred,
        cfg
    )



def inference(cfg, image_path,gpu=0):
    torch.cuda.set_device(gpu)

    # Network Builders
    net_encoder = ModelBuilder.build_encoder(
        arch=cfg.MODEL.arch_encoder,
        fc_dim=cfg.MODEL.fc_dim,
        weights=cfg.MODEL.weights_encoder)
    net_decoder = ModelBuilder.build_decoder(
        arch=cfg.MODEL.arch_decoder,
        fc_dim=cfg.MODEL.fc_dim,
        num_class=cfg.DATASET.num_class,
        weights=cfg.MODEL.weights_decoder,
        use_softmax=True)

    crit = nn.NLLLoss(ignore_index=-1)

    segmentation_module = SegmentationModule(net_encoder, net_decoder, crit)

    # Dataset and Loader
    '''
    dataset_test = TestDataset(
        cfg.list_test,
        cfg.DATASET)
    '''
    dataset_test = TestROPRidgeDataset(
        root_dataset = cfg.DATASET.root_dataset,
        opt = cfg.DATASET,
        img_folder = cfg.DATASET.img_folder_val,
        annotation_folder= "annotations",
        anno_filename = cfg.DATASET.list_val,
        batch_per_gpu=cfg.TRAIN.batch_size_per_gpu)
    loader_test = torch.utils.data.DataLoader(
        dataset_test,
        batch_size=cfg.TEST.batch_size,
        shuffle=False,
        collate_fn=user_scattered_collate,
        num_workers=5,
        drop_last=True)

    segmentation_module.cuda()

    # Main loop
    test(segmentation_module, image_path, gpu)

    print('Inference done!')


if __name__ == '__main__':
    assert LooseVersion(torch.__version__) >= LooseVersion('0.4.0'), \
        'PyTorch>=0.4.0 is required'

    parser = argparse.ArgumentParser(
        description="PyTorch Semantic Segmentation Testing"
    )
    parser.add_argument(
        "--image_path",
        required=True,
        type=str,
        default="",
        help="an image paths, or a directory name"
    )
    parser.add_argument(
        "--checkpoint",
        required=False,
        type=str,
        default="",
        help="an image paths, or a directory name"
    )
    parser.add_argument(
        "--result",
        required=False,
        type=str,
        default="",
        help="an image paths, or a directory name"
    )
    parser.add_argument(
        "--cfg",
        default="config/ade20k-resnet50dilated-ppm_deepsup.yaml",
        metavar="FILE",
        help="path to config file",
        type=str,
    )
    parser.add_argument(
        "--gpu",
        default=0,
        type=int,
        help="gpu id for evaluation"
    )
    parser.add_argument(
        "opts",
        help="Modify config options using the command-line",
        default=None,
        nargs=argparse.REMAINDER,
    )
    args = parser.parse_args()

    cfg.merge_from_file(args.cfg)
    cfg.merge_from_list(args.opts)
    # cfg.freeze()
    if len(args.checkpoint)>0:
        cfg.TEST.checkpoint = args.checkpoint
    if len(args.result)>0:
        cfg.TEST.result = args.result 
    logger = setup_logger(distributed_rank=0)   # TODO
    logger.info("Loaded configuration file {}".format(args.cfg))
    logger.info("Running with config:\n{}".format(cfg))

    cfg.MODEL.arch_encoder = cfg.MODEL.arch_encoder.lower()
    cfg.MODEL.arch_decoder = cfg.MODEL.arch_decoder.lower()

    # absolute paths of model weights
    cfg.MODEL.weights_encoder = os.path.join(
        cfg.DIR, 'encoder_' + cfg.TEST.checkpoint)
    cfg.MODEL.weights_decoder = os.path.join(
        cfg.DIR, 'decoder_' + cfg.TEST.checkpoint)

    assert os.path.exists(cfg.MODEL.weights_encoder) and \
        os.path.exists(cfg.MODEL.weights_decoder), "checkpoint does not exitst!"
    '''
    # generate testing image list
    if os.path.isdir(args.imgs[0]):
        imgs = find_recursive(args.imgs[0])
    else:
        imgs = [args.imgs]
    assert len(imgs), "imgs should be a path to image (.jpg) or directory."
    cfg.list_test = [{'fpath_img': x} for x in imgs]
    '''
    
    if not os.path.isdir(cfg.TEST.result):
        os.makedirs(cfg.TEST.result)
    
    inference(cfg,args.image_path, args.gpu)
