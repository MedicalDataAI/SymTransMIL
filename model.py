import operator
import torch
import torch.nn as nn
import torchvision.models as models
from torch import Tensor
import torch.nn.functional as F

class BasicBlock(nn.Module):
    def __init__(self, ):
        super(BasicBlock, self).__init__()
        self.conv1 = nn.Conv2d(512, 256, kernel_size=3, stride=2, padding=1)
        self.bn1 = nn.BatchNorm2d(256)
        self.relu = nn.ReLU()
        self.conv2 = nn.Conv2d(256, 128, kernel_size=3, stride=2, padding=1)
        self.bn2 = nn.BatchNorm2d(128)
        self.conv_residual = nn.Conv2d(512, 128, kernel_size=1, stride=4)
        self.bn_residual = nn.BatchNorm2d(128)
    def forward(self, x):
        residual = self.conv_residual(x)
        residual = self.bn_residual(residual)
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)
        out = self.conv2(out)
        out = self.bn2(out)
        out = self.relu(out)
        out = out + residual
        out = self.relu(out)
        out = nn.AdaptiveAvgPool2d((1, 1))(out)
        return out


class Mlp(nn.Module):
    def __init__(self, embed_dim, hidden_features=None, out_features=None, act_layer=nn.GELU, drop=0.):
        super(Mlp, self).__init__()
        hidden_features = hidden_features or 4 * embed_dim
        out_features = out_features or embed_dim
        self.layer_norm = nn.LayerNorm(embed_dim)
        self.fc1 = nn.Linear(embed_dim, hidden_features)
        self.act = act_layer()
        self.fc2 = nn.Linear(hidden_features, out_features)
        self.drop = nn.Dropout(drop)
    def forward(self, x):
        x_ = x
        x = self.layer_norm(x)
        x = self.fc1(x)
        x = self.act(x)
        x = self.fc2(x)
        return x_ + x


class SymmetryCrossAttentionWithMlp(nn.Module):

    def __init__(self, embed_dim=512, num_heads=8, mlp_hidden_dim=2048, dropout_rate=0.):
        super(SymmetryCrossAttentionWithMlp, self).__init__()
        if embed_dim <= 0 or num_heads <= 0 or embed_dim % num_heads != 0:
            raise ValueError("embed_dim must be positive and divisible by num_heads")
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads
        self.scale = self.head_dim ** -0.5
        self.query_proj = nn.Linear(embed_dim, embed_dim)
        self.key_proj = nn.Linear(embed_dim, embed_dim)
        self.value_proj = nn.Linear(embed_dim, embed_dim)
        self.fc_out = nn.Linear(embed_dim, embed_dim)
        self.softmax = nn.Softmax(dim=-1)
        self.layer_norm = nn.LayerNorm(embed_dim)
        self.mlp = Mlp(embed_dim, hidden_features=mlp_hidden_dim, drop=dropout_rate)
        self.alpha = nn.Parameter(torch.tensor(0.0))
        self.beta = nn.Parameter(torch.tensor(0.0))

    def forward(self, x_raw, x_flip, spatial_shape):
        if x_raw.ndim != 3 or x_flip.ndim != 3:
            raise ValueError("x_raw and x_flip must have shape [B, N, C]")
        if x_raw.shape != x_flip.shape:
            raise ValueError("x_raw and x_flip must have the same shape")
        if x_raw.shape[-1] != self.num_heads * self.head_dim:
            raise ValueError("the feature channel dimension must match embed_dim")
        try:
            H, W = spatial_shape
            H, W = operator.index(H), operator.index(W)
        except (TypeError, ValueError) as exc:
            raise ValueError("spatial_shape must contain two positive integers") from exc
        if H <= 0 or W <= 0 or H * W != x_raw.shape[1]:
            raise ValueError("spatial_shape must match the number of feature tokens")

        x_raw_, x_flip_ = x_raw, x_flip

        x_raw = self.layer_norm(x_raw)
        x_flip = self.layer_norm(x_flip)

        Q_raw = self.query_proj(x_raw)
        K_raw = self.key_proj(x_raw)
        V_raw = self.value_proj(x_raw)

        Q_flip = self.query_proj(x_flip)
        K_flip = self.key_proj(x_flip)
        V_flip = self.value_proj(x_flip)

        batch_size = Q_raw.shape[0]
        Q_raw = Q_raw.view(batch_size, -1, self.num_heads, self.head_dim).permute(0, 2, 1, 3)
        K_flip = K_flip.view(batch_size, -1, self.num_heads, self.head_dim).permute(0, 2, 1, 3)
        V_flip = V_flip.view(batch_size, -1, self.num_heads, self.head_dim).permute(0, 2, 1, 3)

        Q_flip = Q_flip.view(batch_size, -1, self.num_heads, self.head_dim).permute(0, 2, 1, 3)
        K_raw = K_raw.view(batch_size, -1, self.num_heads, self.head_dim).permute(0, 2, 1, 3)
        V_raw = V_raw.view(batch_size, -1, self.num_heads, self.head_dim).permute(0, 2, 1, 3)

        attention_raw_to_flip = torch.einsum('nhqd,nhkd->nhqk', Q_raw, K_flip) * self.scale
        attention_flip_to_raw = torch.einsum('nhqd,nhkd->nhqk', Q_flip, K_raw) * self.scale

        yy, xx = torch.meshgrid(
            torch.arange(H, device=x_raw.device),
            torch.arange(W, device=x_raw.device),
            indexing="ij"
        )
        pos = torch.stack([yy.flatten(), xx.flatten()], dim=-1).float()
        dist2 = (pos[:, None, :] - pos[None, :, :]).square().sum(-1)
        sigma = 2.0
        G = torch.exp(-dist2 / (2 * sigma**2))

        prior_raw, prior_flip = x_raw, x_flip
        if x_raw.dtype in (torch.float16, torch.bfloat16):
            prior_raw, prior_flip = x_raw.float(), x_flip.float()
        D = (prior_raw - prior_flip).abs().mean(dim=-1)
        D = (D - D.mean(dim=-1, keepdim=True)) / (
            D.std(dim=-1, keepdim=True, unbiased=False) + 1e-6
        )
        D = D.clamp(-3, 3)

        bias = G[None, None, :, :] * (
            self.alpha + self.beta * D[:, None, None, :]
        )
        bias = bias.to(attention_raw_to_flip.dtype)
        attention_raw_to_flip = attention_raw_to_flip + bias
        attention_flip_to_raw = attention_flip_to_raw + bias

        attention_raw_to_flip = self.softmax(attention_raw_to_flip)
        attention_flip_to_raw = self.softmax(attention_flip_to_raw)

        raw_attention = torch.einsum('nhqk,nhkd->nhqd', attention_raw_to_flip, V_flip)
        flip_attention = torch.einsum('nhqk,nhkd->nhqd', attention_flip_to_raw, V_raw)

        raw_attention = raw_attention.permute(0, 2, 1, 3).contiguous().view(batch_size, -1, self.num_heads * self.head_dim)
        flip_attention = flip_attention.permute(0, 2, 1, 3).contiguous().view(batch_size, -1, self.num_heads * self.head_dim)

        raw_attention = self.fc_out(raw_attention)+x_raw_
        flip_attention = self.fc_out(flip_attention)+x_flip_

        F_raw_attention = self.mlp(raw_attention)
        F_flip_attention = self.mlp(flip_attention)

        return F_raw_attention, F_flip_attention
    
class SymmetrySelfAttentionWithMlp(nn.Module):
    def __init__(self, embed_dim=512, num_heads=8, mlp_hidden_dim=2048, dropout_rate=0.):
        super(SymmetrySelfAttentionWithMlp, self).__init__()
        if embed_dim <= 0 or num_heads <= 0 or embed_dim % num_heads != 0:
            raise ValueError("embed_dim must be positive and divisible by num_heads")
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads
        self.scale = self.head_dim ** -0.5
        self.query_proj = nn.Linear(embed_dim, embed_dim)
        self.key_proj = nn.Linear(embed_dim, embed_dim)
        self.value_proj = nn.Linear(embed_dim, embed_dim)
        self.fc_out = nn.Linear(embed_dim, embed_dim)
        self.softmax = nn.Softmax(dim=-1)
        self.layer_norm = nn.LayerNorm(embed_dim)
        self.mlp = Mlp(embed_dim, hidden_features=mlp_hidden_dim, drop=dropout_rate)

    def forward(self, x_raw, x_flip):
        x_raw_, x_flip_ = x_raw, x_flip

        x_raw = self.layer_norm(x_raw)
        x_flip = self.layer_norm(x_flip)


        Q_raw = self.query_proj(x_raw)
        K_raw = self.key_proj(x_raw)
        V_raw = self.value_proj(x_raw)

        Q_flip = self.query_proj(x_flip)
        K_flip = self.key_proj(x_flip)
        V_flip = self.value_proj(x_flip)


        batch_size = Q_raw.shape[0]
        Q_raw = Q_raw.view(batch_size, -1, self.num_heads, self.head_dim).permute(0, 2, 1, 3)
        K_flip = K_flip.view(batch_size, -1, self.num_heads, self.head_dim).permute(0, 2, 1, 3)
        V_flip = V_flip.view(batch_size, -1, self.num_heads, self.head_dim).permute(0, 2, 1, 3)

        Q_flip = Q_flip.view(batch_size, -1, self.num_heads, self.head_dim).permute(0, 2, 1, 3)
        K_raw = K_raw.view(batch_size, -1, self.num_heads, self.head_dim).permute(0, 2, 1, 3)
        V_raw = V_raw.view(batch_size, -1, self.num_heads, self.head_dim).permute(0, 2, 1, 3)


        attention_raw_to_flip = torch.einsum('nhqd,nhkd->nhqk', Q_raw, K_raw) * self.scale
        attention_flip_to_raw = torch.einsum('nhqd,nhkd->nhqk', Q_flip, K_flip) * self.scale


        attention_raw = self.softmax(attention_raw_to_flip)
        attention_flip = self.softmax(attention_flip_to_raw)


        raw_attention = torch.einsum('nhqk,nhkd->nhqd', attention_raw, V_raw)
        flip_attention = torch.einsum('nhqk,nhkd->nhqd', attention_flip, V_flip)

        raw_attention = raw_attention.permute(0, 2, 1, 3).contiguous().view(batch_size, -1, self.num_heads * self.head_dim)
        flip_attention = flip_attention.permute(0, 2, 1, 3).contiguous().view(batch_size, -1, self.num_heads * self.head_dim)

        raw_attention = self.fc_out(raw_attention)+x_raw_
        flip_attention = self.fc_out(flip_attention)+x_flip_


        F_raw_attention = self.mlp(raw_attention)
        F_flip_attention = self.mlp(flip_attention)

        return F_raw_attention, F_flip_attention

class SymmetryEnhancedResNet18(nn.Module):
    def __init__(self, num_classes=2, embed_dim=512, num_heads=8, pretrained=True):
        super(SymmetryEnhancedResNet18, self).__init__()
        base_resnet = models.resnet18(pretrained=pretrained)
        self.resnet18 = base_resnet
        self.resnet18.conv1 = nn.Conv2d(1, 64, kernel_size=7, stride=2, padding=3, bias=False)
        self.resnet18 = nn.Sequential(*list(self.resnet18.children())[:-2])
        self.cross_attention = SymmetryCrossAttentionWithMlp(embed_dim=embed_dim, num_heads=num_heads)
        self.self_attention = SymmetrySelfAttentionWithMlp(embed_dim=embed_dim, num_heads=num_heads)
        self.norm = nn.BatchNorm2d(512)
        self.conv_layers = BasicBlock()
        self.fc = nn.Linear(128, num_classes)

    def forward(self, x):
        batch_size, C, num_slices, H, W = x.size()

        x_flipped = torch.flip(x, dims=[-1])

        x = x.view(batch_size * num_slices, C, H, W)
        x_flipped = x_flipped.view(batch_size * num_slices, C, H, W)

        features_original = self.resnet18(x)
        features_flipped = self.resnet18(x_flipped)

        features_original_ = features_original.flatten(2).transpose(1, 2)
        features_flipped_ = features_flipped.flatten(2).transpose(1, 2)

        F_raw_attention, F_flip_attention = self.self_attention(features_original_, features_flipped_)
        F_raw_attention_1, F_flip_attention_1 = self.cross_attention(
            features_original_,
            features_flipped_,
            spatial_shape=features_original.shape[-2:]
        )

        raw_attention = (F_raw_attention_1 + F_raw_attention).transpose(1, 2).reshape_as(features_original)
        flip_attention = (F_flip_attention_1 + F_flip_attention).transpose(1, 2).reshape_as(features_flipped)

        raw_attention = self.norm(raw_attention)
        flip_attention = self.norm(flip_attention)

        fused_features = raw_attention * flip_attention

        fused_features1 = self.conv_layers(fused_features)

        features = torch.mean(fused_features1.view(batch_size, num_slices, -1), dim=1)

        out = self.fc(features)

        return out, features_original, features_flipped

