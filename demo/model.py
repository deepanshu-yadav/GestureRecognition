import torch
from torch import nn

from models import  mobilenetv2
import pdb

def generate_model(opt):

    from models.mobilenetv2 import get_fine_tuning_parameters
    model = mobilenetv2.get_model(
        num_classes=opt['n_classes'],
        sample_size=opt['sample_size'],
        width_mult=opt['width_mult'])
      
    print('loading pretrained model {}'.format(opt.pretrain_path))
    pretrain = torch.load(opt.pretrain_path)

    model = modify_kernels(opt, model, opt.pretrain_modality)
    model.load_state_dict(pretrain['state_dict'])

    model.module.classifier = nn.Sequential(
                    nn.Dropout(0.9),
                    nn.Linear(model.module.classifier[1].in_features, opt.n_finetune_classes)
                    )

    model = modify_kernels(opt, model, opt.modality)
    parameters = get_fine_tuning_parameters(model, opt.ft_begin_index)
    return model, parameters


def _construct_depth_model(base_model):
    # modify the first convolution kernels for Depth input
    modules = list(base_model.modules())

    first_conv_idx = list(filter(lambda x: isinstance(modules[x], nn.Conv3d),
                                 list(range(len(modules)))))[0]
    conv_layer = modules[first_conv_idx]
    container = modules[first_conv_idx - 1]

    # modify parameters, assume the first blob contains the convolution kernels
    motion_length = 1
    params = [x.clone() for x in conv_layer.parameters()]
    kernel_size = params[0].size()
    new_kernel_size = kernel_size[:1] + (1*motion_length,  ) + kernel_size[2:]
    new_kernels = params[0].data.mean(dim=1, keepdim=True).expand(new_kernel_size).contiguous()

    new_conv = nn.Conv3d(1, conv_layer.out_channels, conv_layer.kernel_size, conv_layer.stride,
                         conv_layer.padding, bias=True if len(params) == 2 else False)
    new_conv.weight.data = new_kernels
    if len(params) == 2:
        new_conv.bias.data = params[1].data # add bias if neccessary
    layer_name = list(container.state_dict().keys())[0][:-7] # remove .weight suffix to get the layer name

    # replace the first convlution layer
    setattr(container, layer_name, new_conv)

    return base_model

def _construct_rgbdepth_model(base_model):
    # modify the first convolution kernels for RGB-D input
    modules = list(base_model.modules())

    first_conv_idx = list(filter(lambda x: isinstance(modules[x], nn.Conv3d),
                           list(range(len(modules)))))[0]
    conv_layer = modules[first_conv_idx]
    container = modules[first_conv_idx - 1]
    # modify parameters, assume the first blob contains the convolution kernels
    motion_length = 1
    params = [x.clone() for x in conv_layer.parameters()]
    kernel_size = params[0].size()
    new_kernel_size = kernel_size[:1] + (1 * motion_length,) + kernel_size[2:]
    new_kernels = torch.mul(torch.cat((params[0].data, params[0].data.mean(dim=1,keepdim=True).expand(new_kernel_size).contiguous()), 1), 0.6)
    new_kernel_size = kernel_size[:1] + (3 + 1 * motion_length,) + kernel_size[2:]
    new_conv = nn.Conv3d(4, conv_layer.out_channels, conv_layer.kernel_size, conv_layer.stride,
                         conv_layer.padding, bias=True if len(params) == 2 else False)
    new_conv.weight.data = new_kernels
    if len(params) == 2:
        new_conv.bias.data = params[1].data  # add bias if neccessary
    layer_name = list(container.state_dict().keys())[0][:-7]  # remove .weight suffix to get the layer name

    # replace the first convolution layer
    setattr(container, layer_name, new_conv)
    return base_model

def _modify_first_conv_layer(base_model, new_kernel_size1, new_filter_num):
    modules = list(base_model.modules())
    first_conv_idx = list(filter(lambda x: isinstance(modules[x], nn.Conv3d),
                                               list(range(len(modules)))))[0]
    conv_layer = modules[first_conv_idx]
    container = modules[first_conv_idx - 1]
 
    new_conv = nn.Conv3d(new_filter_num, conv_layer.out_channels, kernel_size=(new_kernel_size1,7,7),
                         stride=(1,2,2), padding=(1,3,3), bias=False)
    layer_name = list(container.state_dict().keys())[0][:-7]

    setattr(container, layer_name, new_conv)
    return base_model

def modify_kernels(opt, model, modality):
    if modality == 'RGB' and opt.model not in ['c3d', 'squeezenet', 'mobilenet','shufflenet', 'mobilenetv2', 'shufflenetv2']:
        print("[INFO]: RGB model is used for init model")
        model = _modify_first_conv_layer(model,3,3) ##### Check models trained (3,7,7) or (7,7,7)
    elif modality == 'Depth':
        print("[INFO]: Converting the pretrained model to Depth init model")
        model = _construct_depth_model(model)
        print("[INFO]: Done. Flow model ready.")
    elif modality == 'RGB-D':
        print("[INFO]: Converting the pretrained model to RGB+D init model")
        model = _construct_rgbdepth_model(model)
        print("[INFO]: Done. RGB-D model ready.")
    modules = list(model.modules())
    first_conv_idx = list(filter(lambda x: isinstance(modules[x], nn.Conv3d),
                                               list(range(len(modules)))))[0]
    #conv_layer = modules[first_conv_idx]
    #if conv_layer.kernel_size[0]> opt.sample_duration:
     #   model = _modify_first_conv_layer(model,int(opt.sample_duration/2),1)
    return model
