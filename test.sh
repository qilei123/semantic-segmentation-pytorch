git pull
#python3 test.py --gpu 0 --cfg config/ropridge-resnet50-upernet.yaml --checkpoint epoch_5.pth --result val5_res50
#python3 test.py --gpu 0 --cfg config/ropridge-resnet50-upernet.yaml --checkpoint epoch_10.pth --result val10_res50
#python3 test.py --gpu 0 --cfg config/ropridge-resnet50-upernet.yaml --checkpoint epoch_15.pth --result val15_res50
#python3 test.py --gpu 0 --cfg config/ropridge-resnet50-upernet.yaml --checkpoint epoch_20.pth --result val20_res50
#python3 test.py --gpu 0 --cfg config/ropridge-resnet50-upernet.yaml --checkpoint epoch_25.pth --result val25_res50
python3 test.py --gpu 0 --cfg config/ropridge-resnet101-upernet.yaml --checkpoint epoch_5.pth --result val5_res101
python3 test.py --gpu 0 --cfg config/ropridge-resnet101-upernet.yaml --checkpoint epoch_10.pth --result val10_res101
python3 test.py --gpu 0 --cfg config/ropridge-resnet101-upernet.yaml --checkpoint epoch_15.pth --result val15_res101
python3 test.py --gpu 0 --cfg config/ropridge-resnet101-upernet.yaml --checkpoint epoch_20.pth --result val20_res101
python3 test.py --gpu 0 --cfg config/ropridge-resnet101-upernet.yaml --checkpoint epoch_25.pth --result val25_res101