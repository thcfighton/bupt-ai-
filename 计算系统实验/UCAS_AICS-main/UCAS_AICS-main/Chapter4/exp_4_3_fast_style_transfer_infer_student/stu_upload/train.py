# coding=utf-8
from torchvision.models import vgg19
from torch import nn
from zipfile import ZipFile
from torch.utils.data import Dataset, DataLoader
from torchvision.utils import save_image
import torch.nn.functional as F
import torch
import cv2
import numpy

#记者闪避i
class COCODataSet(Dataset):

    def __init__(self):
        super(COCODataSet, self).__init__()
        self.zip_files = ZipFile('./data/train2014.zip')
        self.data_set = []
        for file_name in self.zip_files.namelist():
            if file_name.endswith('.jpg'):
                self.data_set.append(file_name)

    def __len__(self):
        return len(self.data_set)

    def __getitem__(self, item):
        file_path = self.data_set[item]
        image = self.zip_files.read(file_path)
        image = numpy.asarray(bytearray(image), dtype='uint8')
        # 使用cv2.imdecode()函数从指定的内存缓存中读取数据，并把数据转换(解码)成彩色图像格式。
        image = cv2.imdecode(image, cv2.IMREAD_COLOR) 
        # 使用cv2.resize()将图像缩放为512*512大小，其中所采用的插值方式为：区域插值
        image = cv2.resize(image, (512, 512), interpolation=cv2.INTER_AREA) 
        # 使用cv2.cvtColor将图片从BGR格式转换成RGB格式
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # 将image从numpy形式转换为torch.float32,并将其归一化为[0,1]
        image = torch.from_numpy(image).float() / 255.0 
        # 用permute函数将tensor从HxWxC转换为CxHxW
        image = image.permute(2, 0, 1) 
        return image


class VGG19(nn.Module):
    def __init__(self):
        super(VGG19, self).__init__()
        #TODO: 调用vgg19网络
        a = vgg19()
        a = a.features
        #TODO: 定义self.layer1为第2层卷积后对应的特征
        self.layer1 = nn.Sequential(*list(a.children())[0:2]) #利用*list()函数将a.children()转换为列表并进行解包，即返回列表中的元素
        #TODO: 定义self.layer2为第4层卷积后对应的特征
        self.layer2 = nn.Sequential(*list(a.children())[2:4])
        #TODO: 定义self.layer3为第8层卷积后对应的特征
        self.layer3 = nn.Sequential(*list(a.children())[4:8])
        #TODO: 定义self.layer4为第12层卷积后对应的特征
        self.layer4 = nn.Sequential(*list(a.children())[8:12])

    def forward(self, input_):
        out1 = self.layer1(input_)
        out2 = self.layer2(out1)
        out3 = self.layer3(out2)
        out4 = self.layer4(out3)
        return out1, out2, out3, out4


class ResBlock(nn.Module):

    def __init__(self, c):
        super(ResBlock, self).__init__()
        self.layer = nn.Sequential(
            #TODO: 进行卷积，卷积核为3*1*1
            nn.Conv2d(c, c, 3 , 1, 1, bias=False),
            #TODO: 执行实例归一化
            nn.InstanceNorm2d(c),
            #TODO: 执行ReLU
            nn.ReLU(inplace=True),
            #TODO: 进行卷积，卷积核为3*1*1
            nn.Conv2d(c, c, 3 , 1, 1, bias=False),
            #TODO: 执行实例归一化
            nn.InstanceNorm2d(c)
            
        )

    def forward(self, x):
        #TODO: 返回残差运算的结果
        return x + self.layer(x)
    ##输入是x，输出是H(x)，其中H(x)是网络的一部分。在残差网络中，我们不直接学习H(x)，而是学习残差F(x) = H(x) - x。
    ##然后，我们可以通过F(x) + x来计算H(x)。


class TransNet(nn.Module):

    def __init__(self):
        super(TransNet, self).__init__()
        self.layer = nn.Sequential(
            
            ###################下采样层################
            # TODO：构建图像转换网络，第一层卷积
           nn.Conv2d(3, 32, 9, 1, padding=4, bias=False),
            # TODO：实例归一化
            nn.InstanceNorm2d(32),
            # TODO：创建激活函数ReLU
            nn.ReLU(inplace=True),
            # TODO：第二层卷积
            nn.Conv2d(32, 64, 3, 2, padding=1, bias=False),
            # TODO：实例归一化
            nn.InstanceNorm2d(64),
            # TODO：创建激活函数ReLU
            nn.ReLU(inplace=True),
            # TODO：第三层卷积
            nn.Conv2d(64, 128, 3, 2, padding=1, bias=False),
            # TODO：实例归一化
            nn.InstanceNorm2d(128),
            # TODO：创建激活函数ReLU
            nn.ReLU(inplace=True),

            ##################残差层##################
            ResBlock(128),
            ResBlock(128),
            ResBlock(128),
            ResBlock(128),
            ResBlock(128),

            ################上采样层##################
            #TODO: 使用torch.nn.Upsample对特征图进行上采样
            nn.Upsample(scale_factor=2, mode='nearest'),
            #TODO: 执行卷积操作
            nn.Conv2d(128, 64, 3, 1, padding=1, bias=False),
            #TODO: 实例归一化
            nn.InstanceNorm2d(64),
            #TODO: 执行ReLU操作
            nn.ReLU(inplace=True),

            #TODO: 使用torch.nn.Upsample对特征图进行上采样
            nn.Upsample(scale_factor=2, mode='nearest'),
            #TODO: 执行卷积操作
            nn.Conv2d(64, 32, 3, 1, padding=1, bias=False),
            #TODO: 实例归一化
            nn.InstanceNorm2d(32),
            #TODO: 执行ReLU操作
            nn.ReLU(inplace=True),
            
            ###############输出层#####################
            #TODO: 执行卷积操作
            nn.Conv2d(32, 3, 9, 1, padding=4),
            #TODO： sigmoid激活函数
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.layer(x)
    
def load_image(path):##这一部分注意赋值，否则不会改变原来 image的值
    # TODO: 使用cv2从路径中读取图片
    image=cv2.imread(path)
    # TODO: 使用cv2.cvtColor将图片从BGR格式转换成RGB格式
    image=cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
    # TODO: 使用cv2.resize()将图像缩放为512*512大小
    image=cv2.resize(image,(512,512))
    # TODO: 将image从numpy形式转换为torch.float32,并将其归一化为[0,1]
    image=torch.from_numpy(image).float()/255.0
    # TODO: 将tensor从HxWxC转换为CxHxW，并对在0维上增加一个维度
    image=image.permute(2,0,1).unsqueeze(0)
    return image


def get_gram_matrix(f_map):
    """
    """
    n, c, h, w = f_map.shape
    if n == 1:
        f_map = f_map.reshape(c, h * w)
        gram_matrix = torch.mm(f_map, f_map.t())
        return gram_matrix
    else:
        f_map = f_map.reshape(n, c, h * w)
        gram_matrix = torch.matmul(f_map, f_map.transpose(1, 2))
        return gram_matrix


if __name__ == '__main__':
    image_style = load_image('./data/udnie.jpg').cpu()
    print(image_style.shape)
    net = VGG19().cpu()
    g_net = TransNet().cpu()
    print("g_net build PASS!\n")
    #TODO: 使用adam优化器对g_net的参数进行优化，得到optimizer
    optimizer = torch.optim.Adam(g_net.parameters(), lr=0.001)
    #TODO: 在cpu上计算均方误差损失函得到loss_func函数
    loss_func = nn.MSELoss().cpu()
    print("build loss PASS!\n")
    data_set = COCODataSet()
    print("load COCODataSet PASS!\n")
    batch_size = 1
    data_loader = DataLoader(data_set, batch_size, True, drop_last=True)
    #TODO：输入的风格图像经过特征提取网络生成风格特征s1-s4
    s1, s2, s3, s4 = net(image_style)
    #TODO: 对风格特征s1-s4计算格拉姆矩阵并从当前计算图中分离下来,得到对应的s1-s4
    s1 = get_gram_matrix(s1).detach()   ##先对s1计算格拉姆矩阵，然后将计算结果从当前的计算图中分离出来，赋值给s1。
                                        ##这样，新的s1就不再参与梯度的计算和反向传播，也就是说，对新的s1进行任何操作，都不会影响到原来的计算图。
    s2 = get_gram_matrix(s2).detach()
    s3 = get_gram_matrix(s3).detach()
    s4 = get_gram_matrix(s4).detach()
    j = 0
    count = 0
    epochs = 0
    print("start training!\n")
    while j <= epochs:
        for i, image in enumerate(data_loader):
            image_c = image.cpu()
            #TODO: 将输入图像经过图像转化网络输出生成图像image_g
            image_g = g_net(image_c)
            print(image_g.shape)
            #TODO: 利用特征提取网络提取生成图像的特征out1、out2、out3、out4
            out1, out2, out3, out4 = net(image_g)
            ###############计算风格损失###################
            #TODO: 对生成图像的特征out1-out4计算gram矩阵，并与风格图像的特征s1-s4通过loss_func求损失，分别得到loss_s1-loss_s4
            loss_s1 = loss_func(get_gram_matrix(out1), s1)
            loss_s2 = loss_func(get_gram_matrix(out2), s2)
            loss_s3 = loss_func(get_gram_matrix(out3), s3)
            loss_s4 = loss_func(get_gram_matrix(out4), s4)
            #TODO：loss_s1-loss_s4相加得到风格损失loss_s
            loss_s = loss_s1 + loss_s2 + loss_s3 + loss_s4
            ###############计算内容损失###################
            #TODO: 将输入图像经过特征提取网络得到内容特图像的特征c1-c4
            c1, c2, c3, c4 = net(image_c)
            #TODO: 将内容图像特征c2从计算图中分离并与内容图像特征out2通过loss_func得到内容损失loss_c2
            loss_c2 = loss_func(c2.detach(), out2)
            loss_c = loss_c2

            ###############计算总损失###################
            loss = loss_c + 0.000000005 * loss_s

            #######清空梯度、计算梯度、更新参数###########
            #TODO: 梯度初始化为零
            optimizer.zero_grad()
            #TODO: 反向传播求梯度
            loss.backward()
            #TODO: 更新所有参数
            optimizer.step()
            print('j:',j, 'i:',i, 'loss:',loss.item(), 'loss_c:',loss_c.item(), 'loss_s:',loss_s.item())
            count += 1
            if i % 10 == 0:
                #TODO: 将图像转换网络的参数fst_train.pth存储在models文件夹下
                torch.save(g_net.state_dict(), './models/fst_train.pth')
                #TODO: 利用save_image函数将tensor形式的生成图像image_g以及输入图像image_c以jpg左右拼接的形式保存在/out/train/文件夹下
                image_c=F.interpolate(image_c,size=image_g.shape[2:])
                save_image(torch.cat((image_g, image_c), 3), './out/train/%d_%d.jpg' % (j, i))
        j += 1

    print("TRAIN RESULT PASS!\n")
