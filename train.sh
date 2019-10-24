git pull
#python3 train.py --gpus 0,1 --cfg config/ropridge-resnet50dilated-ppm_deepsup.yaml
#python3 train.py --gpus 0,1 --cfg config/ropridge-resnet50-upernet.yaml
#python3 train.py --gpus 0,1 --cfg config/ropridge-resnet101-upernet.yaml
#python3 train.py --gpus 0,1 --cfg config/ropridge3-hrnetv2.yaml
python3 train.py --gpus 0,1 --cfg config/ropridge3-hrnetv2.yaml
